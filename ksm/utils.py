import subprocess
import yaml
from pathlib import Path
import re
import typer

CONFIG_PATH = Path("arbis-tools-config.yaml")


def read_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def run_cmd(command: list, check=True, sudo=True):
    if sudo:
        command = ["sudo"] + command
    typer.echo(f"[CMD] {' '.join(command)}")
    subprocess.run(command, check=check)


def ask_confirm(message: str) -> bool:
    typer.echo(f"{message} [y/N]")
    confirm = input().lower()
    return confirm == 'y'


def list_partitions(device: str):
    typer.echo(f"\n[INFO] Available partitions on {device}:")
    run_cmd(["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT", device], check=False)


def parse_size(size_str):
    """Парсить розмір у MiB або GiB. Дозволені одиниці: M, MiB, G, GiB, MB, GB."""
    size_str = size_str.strip().upper().replace("IB", "").replace("B", "")
    match = re.match(r'^(\d+(\.\d+)?)([MG])$', size_str)
    if not match:
        typer.echo("❌ Invalid size format. Use formats like 120MiB, 2G, 2GiB, 30MB, 30M")
        raise typer.Abort()
    value, _, unit = match.groups()
    value = float(value)
    if unit == 'M':
        return value  # already in MiB
    elif unit == 'G':
        return value * 1024  # convert GiB to MiB
