import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Optional

import requests

GITHUB_REPO = "meelgroup/ttc"
VERSION = "0.1.0"

CUSTOM_WHEEL_PACKAGES = ["pycddlib", "polytope"]

NATIVE_BINARIES = ["cvc5", "hall_tool", "lrs", "sample", "volume"]


def _platform_artifact() -> str:
    system = platform.system()
    machine = platform.machine()
    if system == "Linux" and machine == "x86_64":
        return "linux-x86_64"
    if system == "Darwin" and machine == "arm64":
        return "macos-arm64"
    raise RuntimeError(
        f"Unsupported platform: {system}/{machine}. "
        f"Pre-built binaries are available for linux-x86_64 and macos-arm64."
    )


def _state_dir() -> Path:
    d = Path.home() / ".local" / "share" / "ttc" / VERSION
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sibling_bin_dir() -> Optional[Path]:
    """Tarball/install.sh flow ships binaries in <repo>/bin next to ttc.py."""
    candidate = Path(__file__).resolve().parent / "bin"
    if all((candidate / b).exists() for b in NATIVE_BINARIES):
        return candidate
    return None


def _wheels_installed() -> bool:
    for pkg in CUSTOM_WHEEL_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            return False
    return True


def ensure_ready() -> Path:
    sibling = _sibling_bin_dir()
    if sibling is not None and _wheels_installed():
        return sibling

    bin_dir = _state_dir() / "bin"
    if all((bin_dir / b).exists() for b in NATIVE_BINARIES) and _wheels_installed():
        return bin_dir

    artifact = _platform_artifact()
    archive_name = f"ttc-{VERSION}-{artifact}.tar.gz"
    url = os.environ.get("TTC_ARCHIVE_URL") or (
        f"https://github.com/{GITHUB_REPO}/releases/download/v{VERSION}/{archive_name}"
    )

    print(f"[ttc] First-run setup: downloading {archive_name} ...", file=sys.stderr)

    state = _state_dir()
    archive_path = state / archive_name

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(archive_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)

    extract_dir = state / "extract"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir()
    with tarfile.open(archive_path) as tar:
        tar.extractall(extract_dir)
    archive_path.unlink()

    stage = extract_dir / f"ttc-{VERSION}-{artifact}"

    bin_dir.mkdir(exist_ok=True)
    for b in NATIVE_BINARIES:
        src = stage / "bin" / b
        dst = bin_dir / b
        src.replace(dst)
        dst.chmod(dst.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    wheels_dir = stage / "wheels"
    print("[ttc] Installing dependencies ...", file=sys.stderr)
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--quiet",
        "--find-links", str(wheels_dir),
        "--no-index",
        *CUSTOM_WHEEL_PACKAGES,
    ])

    shutil.rmtree(extract_dir)
    print("[ttc] Setup complete.", file=sys.stderr)
    return bin_dir
