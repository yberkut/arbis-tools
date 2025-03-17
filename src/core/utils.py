import subprocess
import yaml
from pathlib import Path
import re
import typer


def read_config():
    with open(Path("arbis-tools-config.yaml"), "r") as f:
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
    """Парсить розмір у kB, MiB або GiB. Дозволені одиниці: k, kB, kiB, M, MB, MiB, G, GB, GiB. Не залежить від регістру"""
    size_str = size_str.strip().upper().replace("IB", "").replace("B", "")
    match = re.match(r'^(\d+(\.\d+)?)([KMG])$', size_str)
    if not match:
        typer.echo("❌ Invalid size format. Use formats like 1048kB, 120MiB, 2G, 2GiB, 30MB, 30M")
        raise typer.Abort()
    value, _, unit = match.groups()
    value = float(value)
    if unit == 'K':
        return value  # already in kB
    elif unit == 'M':
        return value * 1024  # convert MiB to kB
    elif unit == 'G':
        return value * 1024 * 1024  # convert GiB to kB


def get_free_space(device: str):
    result = subprocess.run(["sudo", "parted", device, "print", "free"], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    free_spaces = []
    for line in output.splitlines():
        if "Free Space" in line:
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2:
                start, end = parts[0], parts[1]
                free_spaces.append((start, end))
    return free_spaces


def validate_partition_name(partition: str, device: str, skip_validation: bool = False):
    if skip_validation:
        return
    if not re.match(r'^sd[a-z][0-9]+$', partition):
        typer.echo("❌ Invalid partition name format (example: sdb3)")
        raise typer.Abort()
    if not f"/dev/{partition}".startswith(device):
        typer.echo(f"❌ Selected partition {partition} does not belong to device {device}")
        raise typer.Abort()
