from pathlib import Path

def get_usb_mount_point(usb_conf):
    return Path(usb_conf['mount_point'])

def get_usb_key_dirs(usb_conf):
    mount_point = get_usb_mount_point(usb_conf)
    return {
        'system': mount_point / "keys" / "system",
        'vm': mount_point / "keys" / "vms",
        'backup': mount_point / "keys" / "backup"
    }