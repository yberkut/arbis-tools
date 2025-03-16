from ksm.utils import read_config, run_cmd, ask_confirm, list_partitions, parse_size
import typer
from pathlib import Path
import subprocess
import re


def get_free_space(device: str):
    result = subprocess.run(["sudo", "parted", device, "print", "free"], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    free_spaces = []
    for line in output.splitlines():
        if "Free Space" in line:
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2:
                start, end = parts[0], parts[1]
                free_spaces.append((start, end))
    return free_spaces


def validate_partition_name(partition: str, device: str, skip_validation: bool = False):
    if skip_validation:
        return
    if not re.match(r'^sd[a-z][0-9]+$', partition):
        typer.echo("❌ Invalid partition name format (example: sdb3)")
        raise typer.Abort()
    if not f"/dev/{partition}".startswith(device):
        typer.echo(f"❌ Selected partition {partition} does not belong to device {device}")
        raise typer.Abort()


def init_usb_store(dry_run: bool = False):
    config = read_config()
    usb_conf = config['usb']

    device = usb_conf['device']
    if not re.match(r'^/dev/(disk/by-id/|sd[a-z])', device):
        typer.echo(f"❌ Invalid device path: {device}")
        raise typer.Abort()

    luks_name = usb_conf['luks_name']
    mount_point = Path(usb_conf['mount_point'])

    def run(cmd):
        if dry_run:
            typer.echo(f"[DRY-RUN] {' '.join(cmd)}")
        else:
            run_cmd(cmd)

    list_partitions(device)

    typer.echo("\n[CHOICE] Select an option:")
    typer.echo("1) Use existing partition")
    typer.echo("2) Create new partition")
    choice = input("Enter choice (1/2): ").strip()

    luks_device_path = None

    if choice == '1':
        partition = input("Enter partition name (e.g., sdb2): ").strip()
        validate_partition_name(partition, device, skip_validation=dry_run)
        full_partition = f"/dev/{partition}"

        typer.echo(f"[INFO] Checking if {full_partition} is LUKS...")
        result = subprocess.run(["sudo", "cryptsetup", "isLuks", full_partition])
        if result.returncode == 0:
            typer.echo(f"✅ {full_partition} is a valid LUKS partition. Trying to open...")
            run(["cryptsetup", "open", full_partition, luks_name])
        else:
            if not ask_confirm(f"⚠️ {full_partition} is NOT LUKS. All data will be erased. Continue?"):
                typer.echo("Aborted.")
                raise typer.Abort()
            run(["cryptsetup", "luksFormat", full_partition])
            run(["cryptsetup", "open", full_partition, luks_name])
            luks_device_path = f"/dev/mapper/{luks_name}"
            run(["mkfs.ext4", luks_device_path])

        luks_device_path = f"/dev/mapper/{luks_name}"

    elif choice == '2':
        typer.echo("[INFO] Checking free space...")
        free_spaces = get_free_space(device)
        if not free_spaces:
            typer.echo("❌ No free space available. Aborting.")
            raise typer.Abort()

        start_str, end_str = free_spaces[-1]
        start_mb = parse_size(start_str)
        end_mb = parse_size(end_str)
        free_space_mb = end_mb - start_mb

        typer.echo(f"[INFO] Last free space: {start_mb} MiB - {end_mb} MiB (Total: {free_space_mb:.2f} MiB)")

        partition_size_str = input("Enter size for new partition (e.g., 2G, 120MiB): ").strip()
        partition_size_mb = parse_size(partition_size_str)

        if partition_size_mb <= 0:
            typer.echo("❌ Partition size must be greater than zero.")
            raise typer.Abort()

        if partition_size_mb > free_space_mb:
            typer.echo(f"❌ Not enough free space. Requested: {partition_size_mb:.2f} MiB, Available: {free_space_mb:.2f} MiB")
            raise typer.Abort()

        end_new_mb = start_mb + partition_size_mb

        typer.echo(f"[ACTION] Creating partition from {start_mb:.2f}MiB to {end_new_mb:.2f}MiB")

        run(["parted", device, "--script", "mkpart", "primary", f"{start_mb:.2f}MiB", f"{end_new_mb:.2f}MiB"])

        list_partitions(device)

        partition = input("Enter new partition name (e.g., sdb3): ").strip()
        if dry_run:
            typer.echo(f"[DRY-RUN] Assuming partition {partition} would be created.")
        validate_partition_name(partition, device, skip_validation=dry_run)
        full_partition = f"/dev/{partition}"

        run(["cryptsetup", "luksFormat", full_partition])
        run(["cryptsetup", "open", full_partition, luks_name])
        luks_device_path = f"/dev/mapper/{luks_name}"
        run(["mkfs.ext4", luks_device_path])

    else:
        typer.echo("❌ Invalid choice. Aborting.")
        raise typer.Abort()

    if not dry_run:
        mount_point.mkdir(parents=True, exist_ok=True)
        run(["mount", luks_device_path, str(mount_point)])

        (mount_point / "keys" / "system").mkdir(parents=True, exist_ok=True)
        (mount_point / "keys" / "vms").mkdir(parents=True, exist_ok=True)
        (mount_point / "passwords").mkdir(parents=True, exist_ok=True)

        typer.echo(f"✅ USB store initialized at {mount_point}")

        run(["umount", str(mount_point)])
        run(["cryptsetup", "close", luks_name])

        typer.echo("✅ USB store closed and ready.")
    else:
        typer.echo(f"[DRY-RUN] Would initialize and prepare USB store at {mount_point}")
