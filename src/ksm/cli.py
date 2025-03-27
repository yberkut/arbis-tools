import typer
from pathlib import Path

from ksm.keys import create_key, list_keys, backup_keys, delete_key, rotate_key

app = typer.Typer(help="Key and Secret Manager (KSM)")


@app.command()
def create_key_cmd(
        key_path: Path = typer.Argument(..., help="Full path to the new key"),
        size: int = typer.Argument(4096, help="Size of the key in bytes"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Creates a new key."""
    create_key(key_path, size, dry_run)


@app.command()
def list_keys_cmd(
        directory: Path = typer.Argument(..., help="Directory containing keys")
):
    """Lists all keys in the specified directory."""
    list_keys(directory)


@app.command()
def backup_keys_cmd(
        source: Path = typer.Argument(..., help="Source directory for backup"),
        destination: Path = typer.Argument(..., help="Destination path for backup"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Backs up keys with multiple options."""
    backup_keys(source, destination, dry_run)


@app.command()
def delete_key_cmd(
        key_path: Path = typer.Argument(..., help="Full path to the key to delete"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show actions without executing")
):
    """Deletes a key from the specified path."""
    delete_key(key_path, dry_run)


if __name__ == "__main__":
    app()
