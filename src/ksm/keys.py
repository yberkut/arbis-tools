import os
import shutil

from pathlib import Path

from core.run_cmd import run_cmd
from core.messages import dry_run_message, success_message, error_message, ask_confirm, console_message


def create_key(key_path: Path, size: int, dry_run: bool = False):
    """
    Creates a new key file with random bytes.

    Args:
        key_path (Path): The full path where the key file should be created.
        size (int): The size of the key file in bytes.
        dry_run (bool, optional): If True, simulates the action without creating the file. Defaults to False.

    Returns:
        None

    Behavior:
    - If the key file already exists, an error message is displayed and the function exits.
    - If dry_run is enabled, the function only prints what it would do without making any changes.
    - The function ensures the parent directory exists before creating the key file.
    - The key file is filled with cryptographically secure random bytes.
    """
    if key_path.exists():
        error_message(f"Key '{key_path}' already exists.")
        return

    if dry_run:
        dry_run_message(f"Would create key: {key_path} ({size} bytes)")
        return

    key_path.parent.mkdir(parents=True, exist_ok=True)
    with key_path.open("wb") as f:
        f.write(os.urandom(size))

    success_message(f"Key '{key_path}' created successfully.")


def list_keys(directory: Path):
    """
    Lists all key files in the given directory.

    Args:
        directory (Path): The directory containing key files.

    Returns:
        None

    Behavior:
    - If the directory does not exist, an error message is displayed and the function exits.
    - If no key files are found, an informational message is displayed.
    - Otherwise, the function prints a list of all found key files.
    """
    if not directory.exists() or not directory.is_dir():
        error_message(f"Directory '{directory}' does not exist.")
        return

    keys = [p for p in directory.iterdir() if p.is_file()]
    if not keys:
        console_message("No keys found.")
    else:
        console_message("Available keys:")
        for key in keys:
            console_message(f" - {key.name}")


def delete_key(key_path: Path, dry_run: bool = False):
    """
    Deletes a key file at the given path.

    Args:
        key_path (Path): The full path of the key file to delete.
        dry_run (bool, optional): If True, simulates the deletion without removing the file. Defaults to False.

    Returns:
        None

    Behavior:
    - If the key file does not exist, an error message is displayed and the function exits.
    - The user is prompted for confirmation before deletion.
    - If dry_run is enabled, the function only prints what it would do without making any changes.
    - The key file is deleted permanently if confirmed.
    """
    if not key_path.exists():
        error_message(f"Key '{key_path}' not found.")
        return

    if not ask_confirm(f"Are you sure you want to delete the key: {key_path}?"):
        error_message("Operation aborted by user.")
        return

    if dry_run:
        dry_run_message(f"Would delete key: {key_path}")
        return

    key_path.unlink()
    success_message(f"Key '{key_path}' deleted successfully.")


def rotate_key(name: str, luks_device: str, slot: int, dry_run: bool):
    """
    Rotates a key in the specified LUKS container at a given slot.

    Args:
        name (str): The file path of the new key to add.
        luks_device (str): The LUKS container device (e.g., /dev/mapper/vg0-root).
        slot (int): The LUKS key slot to replace.
        dry_run (bool, optional): If True, simulates the key rotation without executing it. Defaults to False.

    Returns:
        None

    Behavior:
    - If the specified key file does not exist, an error message is displayed.
    - If dry_run is enabled, prints what actions would be performed.
    - The function first checks existing LUKS key slots.
    - It then adds the new key and removes the old one from the specified slot.
    """
    key_file = Path(name)
    if not key_file.exists():
        error_message(f"Key '{name}' not found.")
        return

    if dry_run:
        dry_run_message(f"Would check existing LUKS slots in {luks_device}")
        dry_run_message(f"Would add new key from {key_file} to slot {slot} in {luks_device}")
        dry_run_message(f"Would remove key from slot {slot} in {luks_device}")
        return

    try:
        existing_keys = run_cmd(["cryptsetup", "luksDump", luks_device], capture_output=True, text=True,
                                check=True).stdout
        console_message("🔍 Existing LUKS Slots:")
        console_message(existing_keys)

        run_cmd(["cryptsetup", "luksAddKey", luks_device, str(key_file)], check=True)
        run_cmd(["cryptsetup", "luksKillSlot", luks_device, str(slot)], check=True)

        success_message(f"Key '{name}' successfully rotated in slot {slot} of {luks_device}.")
    except Exception as e:
        error_message(f"Failed to rotate key '{name}' in {luks_device}: {str(e)}")


def backup_keys(source: Path, destination: Path, dry_run: bool = False):
    """Backs up all keys from the source directory to the destination."""
    if not source.exists() or not source.is_dir():
        error_message(f"Source directory '{source}' does not exist.")
        return

    if dry_run:
        dry_run_message(f"Would copy all keys from {source} to {destination}")
        return

    shutil.copytree(source, destination, dirs_exist_ok=True)
    success_message(f"All keys backed up successfully to {destination}")
