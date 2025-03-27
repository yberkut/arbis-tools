import os
import shutil

from pathlib import Path

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


def backup_keys(source: Path, destination: Path, dry_run: bool = False):
    """
    Backs up all key files from the source directory to the destination directory.

    Args:
        source (Path): The path to the directory containing key files to be backed up.
        destination (Path): The path to the destination directory where the keys will be copied.
        dry_run (bool, optional): If True, simulates the backup process without copying any files. Defaults to False.

    Returns:
        None

    Behavior:
    - If the source directory does not exist or is not a directory, an error message is displayed, and the function exits.
    - If dry_run is enabled, the function prints a message indicating what it would do without making any changes.
    - If dry_run is disabled, all files and subdirectories from the source directory are copied to the destination.
    - If the destination directory already exists, existing files will be overwritten.
    - A success message is displayed once the backup is complete.
    """
    if not source.exists() or not source.is_dir():
        error_message(f"Source directory '{source}' does not exist.")
        return

    if dry_run:
        dry_run_message(f"Would copy all keys from {source} to {destination}")
        return

    shutil.copytree(source, destination, dirs_exist_ok=True)
    success_message(f"All keys backed up successfully to {destination}")
