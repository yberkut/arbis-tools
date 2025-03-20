import os
import typer
from pathlib import Path
from core.read_config import read_config
from core.ask_confirm import ask_confirm
from core.messages import dry_run_message, success_message, error_message


def create_key(name: str, key_type: str, key_size: int, dry_run: bool):
    """
    Creates a new key for the given type (system, vm, backup).

    If `dry_run` is enabled, the function will simulate the operation without making changes.
    """
    valid_types = ['system', 'vm', 'backup']
    if key_type not in valid_types:
        error_message(f"Invalid key type. Valid types: {valid_types}")
        raise typer.Abort()

    config = read_config()
    usb_conf = config.get('usb', {})
    mount_point = Path(usb_conf.get('mount_point', '/mnt/usb'))

    # Determine the key storage directory
    key_dirs = {
        'system': mount_point / "keys" / "system",
        'vm': mount_point / "keys" / "vms",
        'backup': mount_point / "keys" / "backup"
    }
    key_dir = key_dirs.get(key_type)

    # Ensure key storage directory exists
    if not key_dir.exists():
        if dry_run:
            dry_run_message(f"Would create directory: {key_dir}")
        else:
            key_dir.mkdir(parents=True, exist_ok=True)

    key_file = key_dir / f"{name}.key"

    # Check if the key already exists
    if key_file.exists():
        if not ask_confirm(f"Key {key_file} already exists. Overwrite?"):
            error_message("Operation aborted by user.")
            raise typer.Abort()

    # Dry-run mode
    if dry_run:
        dry_run_message(f"Would create key: {key_file} ({key_size} bytes)")
        return

    # Generate and save the key
    key_data = os.urandom(key_size)
    with key_file.open("wb") as f:
        f.write(key_data)

    # Verify file size
    actual_size = key_file.stat().st_size
    if actual_size != key_size:
        error_message("Written key size does not match expected size.")
        raise typer.Abort()

    success_message(f"Key '{name}' ({key_type}) created successfully at {key_file}")
