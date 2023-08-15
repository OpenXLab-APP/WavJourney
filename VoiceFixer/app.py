from genericpath import exists
import os
import os.path
import logging
from voicefixer import VoiceFixer
from flask import Flask, request, jsonify

# Configure the logging format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a FileHandler for the log file
os.makedirs('services_logs', exist_ok=True)
log_filename = 'services_logs/Speech-Restoration.log'
file_handler = logging.FileHandler(log_filename, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the FileHandler to the root logger
logging.getLogger('').addHandler(file_handler)

# Initialize the model here
vf = VoiceFixer()
logging.info('VoiceFixer is loaded ...')

app = Flask(__name__)

@app.route('/fix_audio', methods=['POST'])
def fix_audio():
    # Receive the text from the POST request
    data = request.json
    processfile = data['processfile']

    logging.info(f'Fixing {processfile} ...')

    try:
        vf.restore(input=processfile, output=processfile, cuda=True, mode=0)
        
        # Return success message and the filename of the generated audio
        return jsonify({'message': 'Speech restored successfully', 'file': processfile})

    except Exception as e:
        # Return error message if something goes wrong
        return jsonify({'API error': str(e)}), 500
    

if __name__ == '__main__':
    import yaml
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    service_port = config['Speech-Restoration']['service-port']
    app.run(debug=False, port=service_port)

