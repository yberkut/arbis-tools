import re
import typer


def validate_partition_name(partition: str, device: str, skip_validation: bool = False):
    if skip_validation:
        return
    if not re.match(r'^sd[a-z][0-9]+$', partition):
        typer.echo("❌ Invalid partition name format (example: sdb3)")
        raise typer.Abort()
    if not f"/dev/{partition}".startswith(device):
        typer.echo(f"❌ Selected partition {partition} does not belong to device {device}")
        raise typer.Abort()
