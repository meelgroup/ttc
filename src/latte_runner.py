import subprocess
import os
import sys
from .utils import log


def run_latte_on_matrix(matrix_file):
    log("Running latte...", 2)
    count_command = os.path.expanduser("~/latte/bin/count")
    result = subprocess.run([count_command, matrix_file],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"latte error: {result.stderr}")
    log(f"latte output: \n {result.stderr.strip()}", 3)
    log(f"{result.stdout.strip()}", 3)
    # return the last line of the output which contains the count
    count = result.stdout.strip().split("\n")[-1]

    if not result.stdout.strip():
        print("The latte output is empty.")
        sys.exit(1)
    return int(count)
