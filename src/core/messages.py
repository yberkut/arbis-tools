import typer

def console_message(message: str):
    """Prints a message in console."""
    typer.echo(message)

def dry_run_message(message: str):
    """Prints a dry-run message with a unique prefix and emoji."""
    console_message(f"🔎 [DRY-RUN] {message}")

def success_message(message: str):
    """Prints a success message with a checkmark emoji."""
    console_message(f"✅ {message}")

def error_message(message: str):
    """Prints an error message with a cross emoji."""
    console_message(f"❌ {message}")
