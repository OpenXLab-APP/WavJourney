from genericpath import exists
import os
import os.path
import logging
import yaml
from model import VoiceParser
from flask import Flask, request, jsonify

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

service_port = config['Voice-Parser']['service-port']
vp_device = config['Voice-Parser']['device']

# Configure the logging format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a FileHandler for the log file
os.makedirs('services_logs', exist_ok=True)
log_filename = 'services_logs/Voice-Parser.log'
file_handler = logging.FileHandler(log_filename, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the FileHandler to the root logger
logging.getLogger('').addHandler(file_handler)

# Initialize the model here
vp = VoiceParser(device=vp_device)
logging.info('VoiceParser is loaded ...')

app = Flask(__name__)

@app.route('/parse_voice', methods=['POST'])
def parse_voice():
    # Receive the text from the POST request
    data = request.json
    wav_path = data['wav_path']
    out_dir = data['out_dir']

    logging.info(f'Parsing {wav_path} ...')

    try:
        vp.extract_acoustic_embed(wav_path, out_dir)
        
        # Return success message and the filename of the generated audio
        return jsonify({'message': f'Sucessfully parsed {wav_path}'})

    except Exception as e:
        # Return error message if something goes wrong
        return jsonify({'API error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=False, port=service_port)

