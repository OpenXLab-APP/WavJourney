import pdb
import shutil

import gradio as gr

import pipeline
import utils
from pipeline import generate_json_file, generate_audio
from voice_presets import load_voice_presets_metadata, add_session_voice_preset, \
    remove_session_voice_preset

import openai

VOICE_PRESETS_HEADERS = ['ID', 'Description']
DELETE_FILE_WHEN_DO_CLEAR = False
DEBUG = False


def generate_script_fn(instruction, _state: gr.State):
    try:
        session_id = _state['session_id']
        json_script = generate_json_file(session_id, instruction)
        table_text = pipeline.convert_json_to_md(json_script)
    except Exception as e:
        gr.Warning(str(e))
        print(f"Generating script error: {str(e)}")
        return [None, gr.Button.update(interactive=False), _state, gr.Button.update(interactive=True)]
    _state = {
        **_state,
        'session_id': session_id,
        'json_script': json_script
    }
    return [
        table_text, 
        _state,
        gr.Button.update(interactive=True),
        gr.Button.update(interactive=True),
        gr.Button.update(interactive=True),
        gr.Button.update(interactive=True),
    ]


def generate_audio_fn(state):
    btn_state = gr.Button.update(interactive=True)
    try:
        audio_path = generate_audio(**state)
        return [
            gr.make_waveform(str(audio_path)),
            btn_state,
            btn_state,
            btn_state,
            btn_state,
        ]
    except Exception as e:
        print(f"Generation audio error: {str(e)}")
        gr.Warning(str(e))
    return [
        None,
        btn_state,
        btn_state,
        btn_state,
        btn_state,
    ]


def clear_fn(state):
    if DELETE_FILE_WHEN_DO_CLEAR:
        shutil.rmtree('output', ignore_errors=True)
    state = {'session_id': pipeline.init_session()}
    return [gr.Textbox.update(value=''), gr.Video.update(value=None),
            gr.Markdown.update(value=''), gr.Button.update(interactive=False), gr.Button.update(interactive=False),
            state, gr.Dataframe.update(visible=False), gr.Button.update(visible=False),
            gr.Textbox.update(value=''), gr.Textbox.update(value=''), gr.File.update(value=None)]


def textbox_listener(textbox_input):
    if len(textbox_input) > 0:
        return gr.Button.update(interactive=True)
    else:
        return gr.Button.update(interactive=False)


def get_voice_preset_to_list(state: gr.State):
    if state.__class__ == dict:
        session_id = state['session_id']
    else:
        session_id = state.value['session_id']
    voice_presets = load_voice_presets_metadata(
        utils.get_session_voice_preset_path(session_id),
        safe_if_metadata_not_exist=True
    )
    dataframe = []
    for key in voice_presets.keys():
        row = [key, voice_presets[key]['desc']]
        dataframe.append(row)
    return dataframe


def df_on_select(evt: gr.SelectData):
    print(f"You selected {evt.value} at {evt.index} from {evt.target}")
    return {'selected_voice_preset': evt.index}


def del_voice_preset(selected_voice_presets, ui_state, dataframe):
    gr_visible = gr.Dataframe.update(visible=True)
    btn_visible = gr.Button.update(visible=True)
    current_presets = get_voice_preset_to_list(ui_state)
    if selected_voice_presets['selected_voice_preset'] is None or \
            selected_voice_presets['selected_voice_preset'][0] > len(current_presets) - 1:
        gr.Warning('None row is selected')
        return [current_presets, gr_visible, btn_visible, selected_voice_presets]
    # Do the real file deletion
    index = selected_voice_presets['selected_voice_preset'][0]
    vp_id = dataframe['ID'][index]
    remove_session_voice_preset(vp_id, ui_state['session_id'])
    current_presets = get_voice_preset_to_list(ui_state)
    gr.Dataframe.update(value=current_presets)
    if len(current_presets) == 0:
        gr_visible = gr.Dataframe.update(visible=False)
        btn_visible = gr.Button.update(visible=False)
    selected_voice_presets['selected_voice_preset'] = None
    return [current_presets, gr_visible, btn_visible, selected_voice_presets]


def get_system_voice_presets():
    system_presets = load_voice_presets_metadata(utils.get_system_voice_preset_path())
    data = []
    for k, v in system_presets.items():
        data.append([k, v['desc']])
    # headers = ['id', 'description']
    # table_txt = tabulate(data, headers, tablefmt="github")
    return data


def set_openai_key(key):
    openai.api_key = key
    return key


def add_voice_preset(vp_id, vp_desc, file, ui_state, added_voice_preset):
    if vp_id is None or vp_desc is None or file is None or vp_id.strip() == '' or vp_desc.strip() == '':
        gr.Warning('please complete all three fields')
    else:
        count: int = added_voice_preset['count']
        # check if greater than 3
        session_id = ui_state['session_id']
        file_path = file.name
        print(f'session {session_id}, id {id}, desc {vp_desc}, file {file_path}')
        # Do adding ...
        try:
            add_session_voice_preset(vp_id, vp_desc, file_path, session_id)
            added_voice_preset['count'] = count + 1
        except Exception as exception:
            gr.Warning(str(exception))
    # After added
    dataframe = get_voice_preset_to_list(ui_state)
    df_visible = gr.Dataframe.update(visible=True)
    del_visible = gr.Button.update(visible=True)
    if len(dataframe) == 0:
        df_visible = gr.Dataframe.update(visible=False)
        del_visible = gr.Button.update(visible=False)
    return [gr.Textbox.update(value=''), gr.Textbox.update(value=''), gr.File.update(value=None),
            ui_state, added_voice_preset, dataframe, gr.Button.update(interactive=True),
            df_visible, del_visible]


with gr.Blocks() as interface:
    system_voice_presets = get_system_voice_presets()
    # State
    ui_state = gr.State(value={'session_id': pipeline.init_session()})
    selected_voice_presets = gr.State(value={'selected_voice_preset': None})
    added_voice_preset_state = gr.State(value={'added_file': None, 'count': 0})
    # UI Component
    key_text_input = gr.Textbox(label='Please Enter OPENAI Key for acessing GPT4', lines=1, placeholder="Input instruction here.",
                            value='')
    text_input_value = '' if DEBUG is False else "News channel BBC broadcast about Trump playing street fighter 6 against Biden"
    text_input = gr.Textbox(label='Input', lines=2, placeholder="Input instruction here.",
                            value=text_input_value)
    markdown_output = gr.Markdown(label='Audio Script', lines=2)
    generate_script_btn = gr.Button(value='Generate Script', interactive=False)
    audio_output = gr.Video(type='filepath')
    generate_audio_btn = gr.Button(value='Generate Audio', interactive=False)
    clear_btn = gr.ClearButton(value='Clear Inputs')
    # System Voice Presets
    gr.Markdown(label='System Voice Presets', value='# System Voice Presets')
    system_markdown_voice_presets = gr.Dataframe(label='System Voice Presets', headers=VOICE_PRESETS_HEADERS,
                                                 value=system_voice_presets)
    # User Voice Preset Related
    gr.Markdown(label='User Voice Presets', value='# User Voice Presets')
    get_voice_preset_to_list(ui_state)
    voice_presets_df = gr.Dataframe(headers=VOICE_PRESETS_HEADERS, col_count=len(VOICE_PRESETS_HEADERS),
                                    value=get_voice_preset_to_list(ui_state), interactive=False, visible=False)
    # voice_presets_ds = gr.Dataset(components=[gr.Dataframe(visible=True)], samples=get_voice_preset_to_list(ui_state))
    del_voice_btn = gr.Button(value='Delete Selected Voice Preset', visible=False)
    gr.Markdown(label='Add Voice Preset', value='## Add Voice Preset')
    vp_text_id = gr.Textbox(label='Id', lines=1, placeholder="Input voice preset id here.")
    vp_text_desc = gr.Textbox(label='Desc', lines=1, placeholder="Input description here.")
    vp_file = gr.File(label='Wav File', type='file', description='Upload your wav file here.', file_types=['.wav'],
                      interactive=True)
    vp_submit = gr.Button(label='Upload Voice Preset', value="Upload Voice Preset")
    # events
    key_text_input.change(fn=set_openai_key, inputs=[key_text_input], outputs=[key_text_input])
    text_input.change(fn=textbox_listener, inputs=[text_input], outputs=[generate_script_btn])
    generate_audio_btn.click(
        fn=generate_audio_fn,
        inputs=[ui_state],
        outputs=[
            audio_output,
            generate_audio_btn,
            generate_script_btn,
            clear_btn,
            vp_submit,
        ],
        api_name='audio_journey',
    )
    generate_audio_btn.click(
        fn=lambda _: [
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
        ],
        outputs=[
            generate_audio_btn,
            generate_script_btn,
            clear_btn,
            vp_submit,
        ]
    )
    clear_btn.click(fn=clear_fn, inputs=ui_state,
                    outputs=[text_input, audio_output, markdown_output, generate_audio_btn, generate_script_btn,
                             ui_state, voice_presets_df, del_voice_btn,
                             vp_text_id, vp_text_desc, vp_file])
    generate_script_btn.click(
        fn=generate_script_fn, inputs=[text_input, ui_state],
        outputs=[
            markdown_output,
            ui_state,
            generate_audio_btn,
            generate_script_btn,
            clear_btn,
            vp_submit,
        ]
    )
    generate_script_btn.click(
        fn=lambda _: [
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
        ],
        outputs=[
            generate_audio_btn,
            generate_script_btn,
            clear_btn,
            vp_submit,
        ]
    )
    voice_presets_df.select(df_on_select, outputs=[selected_voice_presets])
    voice_presets_df.update(lambda x: print(x))
    del_voice_btn.click(del_voice_preset, inputs=[selected_voice_presets, ui_state, voice_presets_df],
                        outputs=[voice_presets_df, voice_presets_df, del_voice_btn, selected_voice_presets])
    # user voice preset upload
    vp_submit.click(add_voice_preset, inputs=[vp_text_id, vp_text_desc, vp_file, ui_state, added_voice_preset_state],
                    outputs=[vp_text_id, vp_text_desc, vp_file, ui_state, added_voice_preset_state, voice_presets_df,
                             vp_submit,
                             voice_presets_df, del_voice_btn])
    vp_submit.click(lambda _: gr.Button.update(interactive=False), inputs=[vp_submit])
    # debug only
    # print_state_btn = gr.Button(value='Print State')
    # print_state_btn.click(fn=lambda state, state2: print(state, state2), inputs=[ui_state, selected_voice_presets])
interface.queue(concurrency_count=5)
interface.launch()
