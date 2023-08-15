import sys
sys.path.append('../AudioJourney')
import os
import yaml
import logging
import torchaudio
from APIs import WRITE_AUDIO, LOUDNESS_NORM
from utils import fade
from flask import Flask, request, jsonify

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Configure the logging format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a FileHandler for the log file
os.makedirs('services_logs', exist_ok=True)
log_filename = 'services_logs/Text-to-Audio-Music.log'
file_handler = logging.FileHandler(log_filename, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the FileHandler to the root logger
logging.getLogger('').addHandler(file_handler)


# Initialize the model here
from audiocraft.models import AudioGen, MusicGen
tta_model = AudioGen.get_pretrained('facebook/audiogen-medium')
logging.info('AudioGen is loaded ...')

model_size = config['Text-to-Music']['model_size']
ttm_model = MusicGen.get_pretrained(f'facebook/musicgen-{model_size}')
logging.info(f'MusicGen ({model_size}) is loaded ...')

app = Flask(__name__)

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    # Receive the text from the POST request
    data = request.json
    text = data['text']
    length = float(data.get('length', 5.0))
    volume = float(data.get('volume', -35))
    output_wav = data.get('output_wav', 'out.wav')

    logging.info(f'TTA (AudioGen): Prompt: {text}, length: {length} seconds, volume: {volume} dB')
    
    try:
        tta_model.set_generation_params(duration=length)  
        wav = tta_model.generate([text])  
        wav = torchaudio.functional.resample(wav, orig_freq=16000, new_freq=32000)

        wav = wav.squeeze().cpu().detach().numpy()
        wav = fade(LOUDNESS_NORM(wav, volumn=volume))
        WRITE_AUDIO(wav, name=output_wav)

        # Return success message and the filename of the generated audio
        return jsonify({'message': f'Text-to-Audio generated successfully | {text}', 'file': output_wav})

    except Exception as e:
        return jsonify({'API error': str(e)}), 500


@app.route('/generate_music', methods=['POST'])
def generate_music():
    # Receive the text from the POST request
    data = request.json
    text = data['text']
    length = float(data.get('length', 5.0))
    volume = float(data.get('volume', -35))
    output_wav = data.get('output_wav', 'out.wav')

    logging.info(f'TTM (MusicGen): Prompt: {text}, length: {length} seconds, volume: {volume} dB')


    try:
        ttm_model.set_generation_params(duration=length)  
        wav = ttm_model.generate([text])  
        wav = wav[0][0].cpu().detach().numpy()
        wav = fade(LOUDNESS_NORM(wav, volumn=volume))
        WRITE_AUDIO(wav, name=output_wav)

        # Return success message and the filename of the generated audio
        return jsonify({'message': f'Text-to-Music generated successfully | {text}', 'file': output_wav})

    except Exception as e:
        # Return error message if something goes wrong
        return jsonify({'API error': str(e)}), 500


if __name__ == '__main__':
    import yaml
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    tta_service_port = config['Text-to-Audio']['service-port']
    ttm_service_port = config['Text-to-Audio']['service-port']

    if tta_service_port != ttm_service_port:
        msg = 'Ports of TTA and TTM should be same if you are using Audiocraft ...'
        logging.info(msg)
        raise ValueError(msg)

    app.run(debug=False, port=tta_service_port)


