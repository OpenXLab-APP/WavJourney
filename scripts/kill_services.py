import yaml
import os

# Read the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Extract values for each application
tts_port = config['Text-to-Speech']['service-port']

ttm_port = config['Text-to-Music']['service-port']

tta_port = config['Text-to-Audio']['service-port']

sr_port = config['Speech-Restoration']['service-port']

vp_port = config['Voice-Parser']['service-port']


# Execute the commands 
os.system(f'kill $(lsof -t -i :{tts_port})')
os.system(f'kill $(lsof -t -i :{tta_port})')
os.system(f'kill $(lsof -t -i :{ttm_port})')
os.system(f'kill $(lsof -t -i :{sr_port})')
os.system(f'kill $(lsof -t -i :{vp_port})')



