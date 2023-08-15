import yaml
import os

# Read the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

os.makedirs('services_logs', exist_ok=True)

# Extract values for each application
tts_model = config['Text-to-Speech']['model']
tts_env = config['Text-to-Speech']['env']

ttm_model = config['Text-to-Music']['model']
ttm_env = config['Text-to-Music']['env']

tta_model = config['Text-to-Audio']['model']
tta_env = config['Text-to-Audio']['env']

sr_model = config['Speech-Restoration']['model']
sr_env = config['Speech-Restoration']['env']
enable_sr = config['Speech-Restoration']['Enable']

vp_model = config['Voice-Parser']['model']
vp_env = config['Voice-Parser']['env']

# Execute the commands 
os.system(f'nohup conda run --live-stream -n {tts_env} python {tts_model}/app.py > services_logs/meta_tts.out 2>&1 &')
os.system(f'nohup conda run --live-stream -n {vp_env} python {vp_model}/app.py > services_logs/meta_vp.out 2>&1 &')

if enable_sr:
    os.system(f'nohup conda run --live-stream -n {sr_env} python {sr_model}/app.py > services_logs/meta_sr.out 2>&1 &')

# Using AudioCraft for TTA & TTM
if tta_env == ttm_env:
    os.system(f'nohup conda run --live-stream -n {ttm_env} python {ttm_model}/app.py > services_logs/meta_tta_ttm.out 2>&1 &')

# Using AudioLDM for TTA, MusicGen for TTM
if tta_env != ttm_env:
    os.system(f'nohup conda run --live-stream -n {tta_env} python {tta_model}/app.py > services_logs/meta_tta.out 2>&1 &')
    os.system(f'nohup conda run --live-stream -n {ttm_env} python {ttm_model}/app.py > services_logs/meta_ttm.out 2>&1 &')
