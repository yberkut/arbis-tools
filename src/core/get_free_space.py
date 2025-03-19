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
