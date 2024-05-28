import subprocess
from src.utils import log


def run_latte_on_matrix(matrix_file):
    log("Running latte...", 2)
    result = subprocess.run(["latte", matrix_file],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"latte error: {result.stderr}")
    log(f"latte output: {result.stdout.strip()}", 3)
    return int(result.stdout.strip())
