from pathlib import Path

import typer
from ksm.keys import create_key as createkey_func, delete_key as delete_key_func, list_keys as list_keys_func, \
    rotate_key as rotate_key_func, backup_keys as backup_keys_func
from ksm.usb import init_usb_store as init_usb_store_func, unlock_usb_store as unlock_usb_store_func, \
    lock_usb_store as lock_usb_store_func
from core.config import read_config

app = typer.Typer(help="Key and Secret Manager (KSM) for Arbis Tools")


@app.command()
def init_usb_store(
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Initialize or reuse USB storage for keys and passwords."""
    init_usb_store_func(dry_run=dry_run)


@app.command()
def unlock_usb_store(
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Unlock and mount the USB LUKS storage."""
    unlock_usb_store_func(dry_run=dry_run)


@app.command()
def lock_usb_store(
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Lock and unmount the USB LUKS storage."""
    lock_usb_store_func(dry_run=dry_run)


@app.command()
def create_key(
        name: str = typer.Option(None, "--name",
                                 help="Optional key name. If not provided, a default name from config will be used."),
        key_type: str = typer.Option(None, "--type", help="Type of key: system, vm, backup"),
        key_size: int = typer.Option(None, "--size",
                                     help="Key size in bytes. If not provided, default from config will be used."),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Create a new key. If no parameters are provided, try to use values from config. Otherwise, show HELP."""

    # Load configuration
    config = read_config()
    usb_conf = config.get("usb", {})

    # Retrieve values from config if not provided by user
    if not name:
        name = usb_conf.get("keyfile")

    if not key_type:
        key_type = usb_conf.get("key_type")

    if not key_size:
        key_size = usb_conf.get("keyfile_size", 4096)  # Default size from config

    # If required parameters are still missing, show HELP
    if not name or not key_type:
        typer.echo("⚠️ Missing required parameters!")
        typer.echo("ℹ️ You need to specify --name and --type manually, or define them in arbis-tools-config.yaml.")
        raise typer.Exit()

    # Execute key creation function
    createkey_func(name, key_type, key_size, dry_run)


@app.command()
def delete_key(
        name: str = typer.Argument(..., help="Name of the key to delete"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Delete a key from the USB storage."""
    delete_key_func(name, dry_run)


@app.command()
def list_keys(
        dry_run: bool = typer.Option(False, "--dry-run", help="Show expected structure without accessing files")
):
    """Lists all stored keys in a tree-like structure.

    Use --dry-run to see how it could look like
    """
    list_keys_func(dry_run)


@app.command()
def rotate_key(
        name: str = typer.Argument(..., help="Name of the key to rotate"),
        key_type: str = typer.Argument(..., help="Key type (system, vm, backup)"),
        luks_device: str = typer.Argument(..., help="LUKS container device (e.g., /dev/mapper/vg0-root)"),
        slot: int = typer.Argument(..., help="LUKS key slot to replace"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")

):
    """Rotates a key in the specified LUKS container."""
    rotate_key_func(name, key_type, luks_device, slot, dry_run)


@app.command()
def backup_keys(
        destination: Path = typer.Argument(..., help="Destination path for backup"),
        key_type: str = typer.Option(None, "--key-type", help="Backup only keys from this type (system, vm, backup)"),
        key_name: str = typer.Option(None, "--key-name", help="Backup only this specific key"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Backs up keys with multiple options."""
    backup_keys_func(destination, key_type, key_name, dry_run)


@app.command()
def generate_password(name: str, length: int = 32):
    typer.echo(f"[GENERATE-PASSWORD] Name: {name}, Length: {length}")


@app.command()
def list_passwords():
    typer.echo("[LIST-PASSWORDS]")


@app.command()
def delete_password(name: str):
    typer.echo(f"[DELETE-PASSWORD] Name: {name}")


@app.command()
def copy_password(name: str):
    typer.echo(f"[COPY-PASSWORD] Name: {name}")


@app.command()
def backup_passwords(output: str):
    typer.echo(f"[BACKUP-PASSWORDS] Output: {output}")


if __name__ == "__main__":
    app()
