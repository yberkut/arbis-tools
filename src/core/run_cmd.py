import subprocess
import typer


def run_cmd(command: list, check=True, sudo=True):
    if sudo:
        command = ["sudo"] + command
    typer.echo(f"[CMD] {' '.join(command)}")
    subprocess.run(command, check=check)
