import re
import typer

def parse_size(size_str):
    """Парсить розмір у kB, MiB або GiB. Дозволені одиниці: k, kB, kiB, M, MB, MiB, G, GB, GiB. Не залежить від регістру"""
    size_str = size_str.strip().upper().replace("IB", "").replace("B", "")
    match = re.match(r'^(\d+(\.\d+)?)([KMG])$', size_str)
    if not match:
        typer.echo("❌ Invalid size format. Use formats like 1048kB, 120MiB, 2G, 2GiB, 30MB, 30M")
        raise typer.Abort()
    value, _, unit = match.groups()
    value = float(value)
    if unit == 'K':
        return value  # already in kB
    elif unit == 'M':
        return value * 1024  # convert MiB to kB
    elif unit == 'G':
        return value * 1024 * 1024  # convert GiB to kB