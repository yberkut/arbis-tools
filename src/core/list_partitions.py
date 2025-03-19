import typer

from core.run_cmd import run_cmd


def list_partitions(device: str):
    typer.echo(f"\n[INFO] Available partitions on {device}:")
    run_cmd(["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT", device], check=False)
