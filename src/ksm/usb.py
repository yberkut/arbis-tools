import typer
from pathlib import Path
import subprocess
import re

from core.get_free_space import get_free_space
from core.list_partitions import list_partitions
from core.messages import error_message, dry_run_message, console_message, success_message, ask_confirm
from core.config import read_usb_config
from core.run_cmd import run_cmd
from core.validate_partition_name import validate_partition_name


def lock_usb_store(dry_run: bool = False):
    """Unmounts and locks the USB LUKS storage."""
    usb_conf = read_usb_config()
    mount_point = Path(usb_conf['mount_point'])
    luks_name = usb_conf['luks_name']

    def run(cmd):
        if dry_run:
            dry_run_message(cmd)
        else:
            run_cmd(cmd)

    # Check if mount point exists (ignored in dry run)
    if not dry_run and not mount_point.exists():
        error_message(f"Mount point {mount_point} does not exist. Nothing to lock.")
        return

    # Unmount the filesystem
    run(["umount", str(mount_point)])

    # Lock the LUKS container
    run(["cryptsetup", "close", luks_name])

    success_message("USB store locked successfully.")


def unlock_usb_store(dry_run: bool = False):
    """Unlocks and mounts the USB LUKS storage."""
    usb_conf = read_usb_config()

    device = usb_conf['device']
    luks_name = usb_conf['luks_name']
    mount_point = Path(usb_conf['mount_point'])
    luks_device_path = f"/dev/mapper/{luks_name}"

    def run(cmd):
        if dry_run:
            dry_run_message(cmd)
        else:
            run_cmd(cmd)

    console_message(f"[INFO] Unlocking USB store on {device}...")
    list_partitions(device)

    partition = input("Enter partition name (e.g., sdb2): ").strip()
    validate_partition_name(partition, device, skip_validation=dry_run)
    full_partition = f"/dev/{partition}"

    run(["cryptsetup", "open", full_partition, luks_name])

    if not dry_run:
        mount_point.mkdir(parents=True, exist_ok=True)
    run(["mount", luks_device_path, str(mount_point)])

    success_message(f"USB store unlocked and mounted at {mount_point}")


def init_usb_store(dry_run: bool = False):
    usb_conf = read_usb_config()

    device = usb_conf['device']
    if not re.match(r'^/dev/(disk/by-id/|sd[a-z])', device):
        error_message(f"Invalid device path: {device}")
        raise typer.Abort()

    luks_name = usb_conf['luks_name']
    mount_point = Path(usb_conf['mount_point'])

    def run(cmd):
        if dry_run:
            dry_run_message(cmd)
        else:
            run_cmd(cmd)

    list_partitions(device)

    console_message("\n[CHOICE] Select an option:")
    console_message("1) Use existing partition")
    console_message("2) Create new partition")
    choice = input("Enter choice (1/2): ").strip()

    luks_device_path = None

    if choice == '1':
        partition = input("Enter partition name (e.g., sdb2): ").strip()
        validate_partition_name(partition, device, skip_validation=dry_run)
        full_partition = f"/dev/{partition}"

        console_message(f"[INFO] Checking if {full_partition} is LUKS...")
        result = subprocess.run(["sudo", "cryptsetup", "isLuks", full_partition])
        if result.returncode == 0:
            success_message(f"{full_partition} is a valid LUKS partition. Trying to open...")
            run(["cryptsetup", "open", full_partition, luks_name])
        else:
            if not ask_confirm(f"⚠️ {full_partition} is NOT LUKS. All data will be erased. Continue?"):
                error_message("Aborted.")
                raise typer.Abort()
            run(["cryptsetup", "luksFormat", full_partition])
            run(["cryptsetup", "open", full_partition, luks_name])
            luks_device_path = f"/dev/mapper/{luks_name}"
            run(["mkfs.ext4", luks_device_path])

        luks_device_path = f"/dev/mapper/{luks_name}"

    elif choice == '2':
        console_message("[INFO] Checking free space...")
        free_spaces = get_free_space(device)
        if not free_spaces:
            error_message("No free space available. Aborting.")
            raise typer.Abort()

        start_str, end_str = free_spaces[-1]
        from core.parse_size import parse_size
        start_kb = parse_size(start_str)
        end_kb = parse_size(end_str)
        free_space_kb = end_kb - start_kb

        console_message(f"[INFO] Last free space: {start_kb} kB - {end_kb} kB (Total: {free_space_kb:.2f} kB)")

        partition_size_str = input("Enter size for new partition (e.g., 2G, 120MiB): ").strip()
        partition_size_kb = parse_size(partition_size_str)

        if partition_size_kb <= 0:
            error_message("Partition size must be greater than zero.")
            raise typer.Abort()

        if partition_size_kb > free_space_kb:
            error_message(
                f"Not enough free space. Requested: {partition_size_kb / 1024:.2f} MiB, Available: {free_space_kb / 1024:.2f} MiB")
            raise typer.Abort()

        end_new_kb = start_kb + partition_size_kb

        console_message(f"[ACTION] Creating partition from {start_kb / 1024:.2f}MiB to {end_new_kb / 1024:.2f}MiB")

        run(["parted", device, "--script", "mkpart", "primary", f"{start_kb:.2f}kB", f"{end_new_kb:.2f}kB"])

        list_partitions(device)

        partition = input("Enter new partition name (e.g., sdb3): ").strip()
        if dry_run:
            dry_run_message(f"Assuming partition {partition} would be created.")
        validate_partition_name(partition, device, skip_validation=dry_run)
        full_partition = f"/dev/{partition}"

        run(["cryptsetup", "luksFormat", full_partition])
        run(["cryptsetup", "open", full_partition, luks_name])
        luks_device_path = f"/dev/mapper/{luks_name}"
        run(["mkfs.ext4", luks_device_path])

    else:
        error_message("Invalid choice. Aborting.")
        raise typer.Abort()

    if not dry_run:
        mount_point.mkdir(parents=True, exist_ok=True)
        run(["mount", luks_device_path, str(mount_point)])

        (mount_point / "keys" / "system").mkdir(parents=True, exist_ok=True)
        (mount_point / "keys" / "vms").mkdir(parents=True, exist_ok=True)
        (mount_point / "passwords").mkdir(parents=True, exist_ok=True)

        success_message(f"USB store initialized at {mount_point}")

        run(["umount", str(mount_point)])
        run(["cryptsetup", "close", luks_name])

        success_message("USB store closed and ready.")
    else:
        dry_run_message(f"Would initialize and prepare USB store at {mount_point}")
