import subprocess
import os
import sys
from .utils import log
import threading


def stream_output(pipe, output_list):
    for line in iter(pipe.readline, ''):
        sys.stdout.write(f"{line}")
        sys.stdout.flush()
        output_list.append(line)
    pipe.close()


def run_latte_on_matrix(matrix_file, timeout=3600):
    log("Running latte...", 2)
    count_command = os.path.expanduser("~/latte/bin/count")
    print("Latte command:", count_command, matrix_file)

    stdout_lines = []
    stderr_lines = []

    try:
        with subprocess.Popen([count_command, matrix_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) as proc:
            stdout_thread = threading.Thread(
                target=stream_output, args=(proc.stdout, stdout_lines))
            stderr_thread = threading.Thread(
                target=stream_output, args=(proc.stderr, stderr_lines))

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

            # Join the captured output
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)

            # Check for specific error message in stdout or stderr
            error_message = "Empty polytope or unbounded polytope!"
            if error_message in stdout or error_message in stderr:
                print(error_message)
                sys.exit(0)

            # Return the last line of the stdout which contains the count
            count = stdout.strip().split("\n")[-1]
            return int(count)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"latte error: {e.stderr}")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"latte error: {e.stderr}")
