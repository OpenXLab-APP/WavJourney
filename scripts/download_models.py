import yaml
import os

# Read the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Extract values for each application
tts_env = config['Text-to-Speech']['env']

ttm_env = config['Text-to-Music']['env']
ttm_model_size = config['Text-to-Music']['model_size']

tta_env = config['Text-to-Audio']['env']

sr_env = config['Speech-Restoration']['env']

# Downloading the TTS models
print('Step 1: Downloading TTS model ...')
os.system(f'conda run --live-stream -n {tts_env} python -c \'from transformers import BarkModel; BarkModel.from_pretrained("suno/bark")\'')

print('Step 2: Downloading TTA model ...')
os.system(f'conda run --live-stream -n {tta_env} python -c \'from audiocraft.models import AudioGen; tta_model = AudioGen.get_pretrained("facebook/audiogen-medium")\'')

print('Step 3: Downloading TTM model ...')
os.system(f'conda run --live-stream -n {ttm_env} python -c \'from audiocraft.models import MusicGen; tta_model = MusicGen.get_pretrained("facebook/musicgen-{ttm_model_size}")\'')

print('Step 4: Downloading SR model ...')
os.system(f'conda run --live-stream -n {sr_env} python -c \'from voicefixer import VoiceFixer; vf = VoiceFixer()\'')

print('All models successfully downloaded!')
