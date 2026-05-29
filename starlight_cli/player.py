import shutil
import subprocess
import sys


def play(url: str):
    mpv = shutil.which("mpv")
    if not mpv:
        print("mpv not found. Install it:", file=sys.stderr)
        print("  apt:  sudo apt install mpv", file=sys.stderr)
        print("  brew: brew install mpv", file=sys.stderr)
        print("  choco: choco install mpv", file=sys.stderr)
        sys.exit(1)

    cmd = [mpv, url]
    subprocess.run(cmd)
