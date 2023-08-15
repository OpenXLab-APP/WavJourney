import os
import sys
sys.path.append('../AudioJourney')
import logging
import yaml
import numpy as np
import torch
import torchaudio
from torchaudio.transforms import SpeedPerturbation
import nltk
from APIs import WRITE_AUDIO, LOUDNESS_NORM
from flask import Flask, request, jsonify
from transformers import BarkModel, AutoProcessor


with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Configure the logging format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a FileHandler for the log file
os.makedirs('services_logs', exist_ok=True)
log_filename = 'services_logs/Text-to-Speech.log'
file_handler = logging.FileHandler(log_filename, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the FileHandler to the root logger
logging.getLogger('').addHandler(file_handler)

# Initialize the model here
SPEED = float(config['Text-to-Speech']['speed'])
speed_perturb = SpeedPerturbation(32000, [SPEED])

logging.info('Loading Bark model ...')
# TODO: fp16?
model = BarkModel.from_pretrained("suno/bark")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)
model = model.to_bettertransformer()    # Flash attention
SAMPLE_RATE = model.generation_config.sample_rate
SEMANTIC_TEMPERATURE = 0.9
COARSE_TEMPERATURE = 0.5
FINE_TEMPERATURE = 0.5

processor = AutoProcessor.from_pretrained("suno/bark")

app = Flask(__name__)

@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    # Receive the text from the POST request
    data = request.json
    text = data['text']
    speaker_id = data['speaker_id']
    speaker_npz = data['speaker_npz']
    volume = float(data.get('volume', -35))
    output_wav = data.get('output_wav', 'out.wav')
    
    logging.info(f'TTS (Bark): Speaker: {speaker_id}, Volume: {volume} dB, Prompt: {text}')

    try:   
        # Generate audio using the global pipe object
        text = text.replace('\n', ' ').strip()
        sentences = nltk.sent_tokenize(text)
        silence = torch.zeros(int(0.1 * SAMPLE_RATE), device=device).unsqueeze(0)  # 0.1 second of silence

        pieces = []
        for sentence in sentences:
            inputs = processor(sentence, voice_preset=speaker_npz).to(device)
            # NOTE: you must run the line below, otherwise you will see the runtime error
            # RuntimeError: view size is not compatible with input tensor's size and stride (at least one dimension spans across two contiguous subspaces). Use .reshape(...) instead.
            inputs['history_prompt']['coarse_prompt'] = inputs['history_prompt']['coarse_prompt'].transpose(0, 1).contiguous().transpose(0, 1)

            with torch.inference_mode():
                # TODO: min_eos_p?
                output = model.generate(
                    **inputs,
                    do_sample = True,
                    semantic_temperature = SEMANTIC_TEMPERATURE,
                    coarse_temperature = COARSE_TEMPERATURE,
                    fine_temperature = FINE_TEMPERATURE
                )

            pieces += [output, silence]

        result_audio = torch.cat(pieces, dim=1)
        wav_tensor = result_audio.to(dtype=torch.float32).cpu()
        wav = torchaudio.functional.resample(wav_tensor, orig_freq=SAMPLE_RATE, new_freq=32000)
        wav = speed_perturb(wav.float())[0].squeeze(0)
        wav = wav.numpy()
        wav = LOUDNESS_NORM(wav, volumn=volume)
        WRITE_AUDIO(wav, name=output_wav)

        # Return success message and the filename of the generated audio
        return jsonify({'message': f'Text-to-Speech generated successfully | {speaker_id}: {text}', 'file': output_wav})

    except Exception as e:
        raise e
        # Return error message if something goes wrong
        return jsonify({'API error': str(e)}), 500


if __name__ == '__main__':
    service_port = config['Text-to-Speech']['service-port']
    app.run(debug=False, port=service_port)
