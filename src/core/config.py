import yaml
from pathlib import Path


def read_config():
    with open(Path("arbis-tools-config.yaml"), "r") as f:
        return yaml.safe_load(f)


def read_usb_config():
    config = read_config()
    return config.get('usb', {})