import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "backup": {
        "source": "",
        "target": "",
        "enable_versioning": True,
        "versions_to_keep": 5
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
