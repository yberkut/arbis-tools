import os
import shutil

import typer
from pathlib import Path

from build.lib.core.messages import console_message
from core.config import read_usb_config
from core.messages import dry_run_message, success_message, error_message, ask_confirm
from core.run_cmd import run_cmd
from ksm.config import get_usb_key_dirs, get_usb_mount_point


def create_key(name: str, key_type: str, key_size: int, dry_run: bool):
    """
    Creates a new key for the given type (system, vm, backup).

    If `dry_run` is enabled, the function will simulate the operation without making changes.
    """
    valid_types = ['system', 'vm', 'backup']
    if key_type not in valid_types:
        error_message(f"Invalid key type. Valid types: {valid_types}")
        raise typer.Abort()

    usb_conf = read_usb_config()
    # Determine the key storage directory
    key_dirs = get_usb_key_dirs(usb_conf)
    key_dir = key_dirs.get(key_type)

    # Ensure key storage directory exists
    if not key_dir.exists():
        if dry_run:
            dry_run_message(f"Would create directory: {key_dir}")
        else:
            key_dir.mkdir(parents=True, exist_ok=True)

    key_file = key_dir / name

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


def delete_key(name: str, dry_run: bool = False):
    """Deletes a key from the USB storage."""
    usb_conf = read_usb_config()
    key_dirs = get_usb_key_dirs(usb_conf)

    key_file = next((path / name for path in key_dirs.values() if (path / name).exists()), None)

    if not key_file:
        error_message(f"Key '{name}' not found.")
        return

    if not ask_confirm(f"Are you sure you want to delete the key: {key_file}?"):
        error_message("Operation aborted by user.")
        return

    if dry_run:
        dry_run_message(f"Would delete key: {key_file}")
        return

    key_file.unlink()
    success_message(f"Key '{name}' deleted successfully.")


def list_keys(dry_run: bool):
    """Lists all stored keys in a tree-like structure.
    Use --dry-run to see how it could look like
    """
    usb_conf = read_usb_config()
    key_dirs = get_usb_key_dirs(usb_conf)

    console_message("🔑 Stored keys:")

    if dry_run:
        console_message("📂 system")
        console_message("   ├── main.key")
        console_message("   ├── backup.key")
        console_message("📂 vm")
        console_message("   ├── vm1.key")
        console_message("📂 backup")
        console_message("   ├── external_backup.key")
        return

    found_keys = False

    for category, path in key_dirs.items():
        if path.exists():
            keys = list(path.iterdir())
            if keys:
                found_keys = True
                console_message(f"📂 {category}")
                for key in keys:
                    console_message(f"   ├── {key.name}")

    if not found_keys:
        error_message("No keys found.")


def rotate_key(name: str, key_type: str, luks_device: str, slot: int, dry_run: bool):
    """Rotates a key in the specified LUKS container at a given slot."""
    usb_conf = read_usb_config()
    key_dirs = get_usb_key_dirs(usb_conf)

    key_dir = key_dirs.get(key_type)
    if not key_dir:
        error_message(f"Invalid key type: {key_type}")
        return

    key_file = key_dir / name
    if not key_file.exists():
        error_message(f"Key '{name}' not found in {key_type} directory.")
        return

    if dry_run:
        dry_run_message(f"Would check existing LUKS slots in {luks_device}")
        dry_run_message(f"Would add new key from {key_file} to slot {slot} in {luks_device}")
        dry_run_message(f"Would remove key from slot {slot} in {luks_device}")
        return

    try:
        # Show LUKS slot usage
        existing_keys = run_cmd(["cryptsetup", "luksDump", luks_device], capture_output=True, text=True,
                                check=True).stdout
        console_message("🔍 Existing LUKS Slots:")
        console_message(existing_keys)

        # Add new key to the specified slot
        run_cmd(["cryptsetup", "luksAddKey", luks_device, str(key_file)], check=True)

        # Remove old key from the specified slot
        run_cmd(["cryptsetup", "luksKillSlot", luks_device, str(slot)], check=True)

        success_message(f"Key '{name}' successfully rotated in slot {slot} of {luks_device}.")
    except Exception as e:
        error_message(f"Failed to rotate key '{name}' in {luks_device}: {str(e)}")


def backup_keys(destination: Path, key_type: str = None, key_name: str = None, dry_run: bool = False):
    """Backs up all keys, keys from a specific directory, or a specific key."""
    usb_conf = read_usb_config()
    key_dirs = get_usb_key_dirs(usb_conf)

    if key_name:
        if not key_type or key_type not in key_dirs:
            error_message("You must specify a valid key type (system, vm, backup) when backing up a single key.")
            return
        key_file = key_dirs[key_type] / key_name
        if not key_file.exists():
            error_message(f"Key '{key_name}' not found in {key_type} directory.")
            return

        if dry_run:
            dry_run_message(f"Would copy {key_file} to {destination}")
            return

        shutil.copy2(key_file, destination)
        success_message(f"Key '{key_name}' backed up successfully to {destination}")

    elif key_type:
        if key_type not in key_dirs:
            error_message("Invalid key type specified.")
            return

        source_dir = key_dirs[key_type]
        if not source_dir.exists():
            error_message(f"No keys found in {key_type} directory.")
            return

        if dry_run:
            dry_run_message(f"Would copy all keys from {source_dir} to {destination}")
            return

        shutil.copytree(source_dir, destination / key_type, dirs_exist_ok=True)
        success_message(f"All keys from '{key_type}' backed up successfully to {destination}")

    else:
        mount_point = get_usb_mount_point(usb_conf)
        if dry_run:
            dry_run_message(f"Would copy all keys from {mount_point}/keys to {destination}")
            return

        shutil.copytree(mount_point / "keys", destination, dirs_exist_ok=True)
        success_message(f"All keys backed up successfully to {destination}")
