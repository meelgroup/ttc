import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Optional

GITHUB_REPO = "meelgroup/ttc"

try:
    from importlib.metadata import version as _pkg_version
    VERSION = _pkg_version("ttc")
except Exception:
    # Running from a source checkout with no installed metadata (e.g. dev mode
    # or a bare tarball). The sibling-bin fast path handles these cases, so
    # VERSION only matters on the download branch — which such users won't hit.
    VERSION = "0.0.0"

BOOTSTRAP_WHEEL_PACKAGES = ["pycddlib", "polytope", "z3-solver", "cvxopt"]
# pip-install name → import name. pycddlib installs as `cdd`, z3-solver as `z3`.
BOOTSTRAP_IMPORT_NAMES = ["cdd", "polytope", "z3", "cvxopt"]

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


def _bootstrap_packages_installed() -> bool:
    import importlib.util
    for name in BOOTSTRAP_IMPORT_NAMES:
        if importlib.util.find_spec(name) is None:
            return False
    return True


def ensure_ready() -> Path:
    sibling = _sibling_bin_dir()
    if sibling is not None and _bootstrap_packages_installed():
        return sibling

    bin_dir = _state_dir() / "bin"
    if all((bin_dir / b).exists() for b in NATIVE_BINARIES) and _bootstrap_packages_installed():
        return bin_dir

    artifact = _platform_artifact()
    archive_name = f"ttc-{VERSION}-{artifact}.tar.gz"
    url = os.environ.get("TTC_ARCHIVE_URL") or (
        f"https://github.com/{GITHUB_REPO}/releases/download/v{VERSION}/{archive_name}"
    )

    print(f"[ttc] First-run setup: downloading {archive_name} ...", file=sys.stderr)

    import requests

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

    # Glob rather than reconstructing from VERSION — decouples extraction from
    # whatever the archive was named, so a version mismatch between the
    # installed package and the downloaded archive doesn't wedge us.
    stage_candidates = list(extract_dir.glob(f"ttc-*-{artifact}"))
    if len(stage_candidates) != 1:
        raise RuntimeError(
            f"expected exactly one stage dir in {extract_dir}, got {stage_candidates}"
        )
    stage = stage_candidates[0]

    bin_dir.mkdir(exist_ok=True)
    for b in NATIVE_BINARIES:
        src = stage / "bin" / b
        dst = bin_dir / b
        src.replace(dst)
        dst.chmod(dst.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    wheels_dir = stage / "wheels"
    print("[ttc] Installing runtime dependencies ...", file=sys.stderr)
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--quiet",
        "--find-links", str(wheels_dir),
        "--no-index",
        *BOOTSTRAP_WHEEL_PACKAGES,
    ])

    shutil.rmtree(extract_dir)
    print("[ttc] Setup complete.", file=sys.stderr)
    return bin_dir
