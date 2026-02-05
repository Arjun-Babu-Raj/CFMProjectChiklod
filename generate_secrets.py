"""
Generate exact Streamlit Secrets format from config.yaml
"""
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

print("=" * 80)
print("COPY THIS EXACT TEXT INTO STREAMLIT CLOUD SECRETS")
print("=" * 80)
print()

# Generate TOML format
toml_content = ""

# Add each worker's credentials
for username, user_data in config['credentials']['usernames'].items():
    toml_content += f'[credentials.usernames.{username}]\n'
    toml_content += f'email = "{user_data["email"]}"\n'
    toml_content += f'name = "{user_data["name"]}"\n'
    toml_content += f'password = "{user_data["password"]}"\n'
    toml_content += '\n'

# Add cookie config
toml_content += '[cookie]\n'
toml_content += f'expiry_days = {config["cookie"]["expiry_days"]}\n'
toml_content += f'key = "{config["cookie"]["key"]}"\n'
toml_content += f'name = "{config["cookie"]["name"]}"\n'

print(toml_content)
print()
print("=" * 80)
print(f"Worker1 password hash: {config['credentials']['usernames']['worker1']['password']}")
print("=" * 80)
