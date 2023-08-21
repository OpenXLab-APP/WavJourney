import yaml
import os

# Read the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Extract values for each application
service_port = config['Service-Port']

# Execute the commands 
os.system(f'kill $(lsof -t -i :{service_port})')




