import subprocess

from core.messages import console_message


def run_cmd(command: list, check=True, sudo=True, capture_output=False, text=False):
    """Runs a shell command with optional sudo and output capturing."""
    if sudo:
        command = ["sudo"] + command
    console_message(f"[CMD] {' '.join(command)}")
    return subprocess.run(command, check=check, capture_output=capture_output, text=text)
