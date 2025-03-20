import typer

def dry_run_message(message: str):
    """Prints a dry-run message with a unique prefix and emoji."""
    typer.echo(f"🔎 [DRY-RUN] {message}")

def success_message(message: str):
    """Prints a success message with a checkmark emoji."""
    typer.echo(f"✅ {message}")

def error_message(message: str):
    """Prints an error message with a cross emoji."""
    typer.echo(f"❌ {message}")
