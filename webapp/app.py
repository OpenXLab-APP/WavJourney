from flask import Flask, request, render_template
import os
import subprocess

app = Flask(__name__)

def call_chatgpt(prompt_file, input_text):
    # Your actual function to call the ChatGPT API will go here
    # For now, return a placeholder string
    with open(prompt_file, 'r') as file:
        prompt = file.read()
    return f"Prompt: {prompt}\nInput: {input_text}"

def call_convert_script(input_text):
    # Your actual function to call the script will go here
    # For now, return a placeholder string
        # Run the script and capture the output
    process = subprocess.Popen(['python', '../convert_haml_to_py_code.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = process.communicate(input=input_text)
    return output + error

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form.get('InputTextbox', '')
        script_text = request.form.get('ScriptTextbox', '')
        haml_text = request.form.get('HAMLTextbox', '')
        python_code_text = request.form.get('PythonCodeTextbox', '')
        if 'TextToScriptButton' in request.form:
            script_text = call_chatgpt('../prompts/text_to_audio_script.prompt', input_text)

        elif 'ScriptToHAMLButton' in request.form:
            haml_text = call_chatgpt('../prompts/audio_script_to_HAML.prompt', script_text)

        elif 'HAMLToPythonCodeButton' in request.form:
            python_code_text = call_convert_script(haml_text)

        return render_template('index.html', haml_text=haml_text, python_code_text=python_code_text, script_text=script_text, input_text=input_text)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
