"""
Script to verify config structure and help with Streamlit Secrets format.
"""
import yaml
from yaml.loader import SafeLoader

# Load the local config.yaml to see exact structure
with open("config.yaml") as f:
    config = yaml.load(f, Loader=SafeLoader)

print("=" * 60)
print("LOCAL CONFIG.YAML STRUCTURE")
print("=" * 60)
print(yaml.dump(config, default_flow_style=False))

print("\n" + "=" * 60)
print("STREAMLIT SECRETS FORMAT (TOML)")
print("=" * 60)
print("""
[credentials.usernames.worker1]
email = "worker1@example.com"
name = "Health Worker 1"
password = "$2b$12$rE90qSO9zWbGdDHInqwc5e3sLi5JSpbWflrRYD4vRU/9vYrlXbWz6"

[credentials.usernames.worker2]
email = "worker2@example.com"
name = "Health Worker 2"
password = "$2b$12$rE90qSO9zWbGdDHInqwc5e3sLi5JSpbWflrRYD4vRU/9vYrlXbWz6"

[credentials.usernames.worker3]
email = "worker3@example.com"
name = "Health Worker 3"
password = "$2b$12$rE90qSO9zWbGdDHInqwc5e3sLi5JSpbWflrRYD4vRU/9vYrlXbWz6"

[cookie]
expiry_days = 30
key = "random_signature_key_change_this_in_production"
name = "cfm_chiklod_auth"

[preauthorized.emails]
emails = ["worker1@example.com", "worker2@example.com", "worker3@example.com"]
""")

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)
print(f"✓ Credentials structure: {type(config['credentials'])}")
print(f"✓ Usernames: {list(config['credentials']['usernames'].keys())}")
print(f"✓ Cookie config: {config['cookie']}")
