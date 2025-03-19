import yaml
from pathlib import Path


def read_config():
    with open(Path("arbis-tools-config.yaml"), "r") as f:
        return yaml.safe_load(f)
