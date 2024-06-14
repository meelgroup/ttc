import subprocess
import os
import sys
from .utils import log
import threading


def stream_output(pipe, output_type):
    for line in iter(pipe.readline, ''):
        print(f"{line.strip()}")
    pipe.close()


def run_latte_on_matrix(matrix_file, timeout=3600):
    log("Running latte...", 2)
    count_command = os.path.expanduser("~/latte/bin/count")
    print("Latte command:", count_command, matrix_file)

    try:
        with subprocess.Popen([count_command, matrix_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) as proc:
            stdout_thread = threading.Thread(
                target=stream_output, args=(proc.stdout, 'stdout'))
            stderr_thread = threading.Thread(
                target=stream_output, args=(proc.stderr, 'stderr'))

            stdout_thread.start()
            stderr_thread.start()

            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout_thread.join()
                stderr_thread.join()
                raise RuntimeError("latte process timed out after 1 hour")

            stdout_thread.join()
            stderr_thread.join()

            if proc.returncode != 0:
                raise RuntimeError("latte process encountered an error")

            # Capture the final output for processing
            stdout, stderr = proc.communicate()

            # Return the last line of the stdout which contains the count
            count = stdout.strip().split("\n")[-1]

            if not stdout.strip():
                print("The latte output is empty.")
                sys.exit(1)

            return int(count)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"latte error: {e.stderr}")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"latte error: {e.stderr}")
