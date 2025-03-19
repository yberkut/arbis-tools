import typer


def ask_confirm(message: str) -> bool:
    typer.echo(f"{message} [y/N]")
    confirm = input().lower()
    return confirm == 'y'
