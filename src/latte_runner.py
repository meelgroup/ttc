import subprocess
import os
import sys
from .utils import log
import threading
from .global_storage import gbl
from .polytope_bv import Polytope


def stream_output(pipe, output_list):
    if gbl.verbosity < 4:
        return
    for line in iter(pipe.readline, ''):
        sys.stdout.write(f"{line}")
        sys.stdout.flush()
        output_list.append(line)
    pipe.close()


def run_tool_on_matrix(matrix_file, toolname, count_command, timeout=3600):
    log(f"Running {toolname}...", 2)
    log(f"Latte command:  {count_command} {matrix_file}", 3)

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
            error_message = "is unbounded"
            empty_polytope_message = "Empty polytope or unbounded polytope!"
            if error_message in stdout or error_message in stderr:
                log(
                    "Unbounded polytope!\n TODO: Make sure this polytope is not empty", 0)
                sys.exit(0)
            if empty_polytope_message in stdout or empty_polytope_message in stderr:
                log("Empty polytope!", 3)
                count = 0
            else:
                # Return the last line of the stdout which contains the count
                # count = stdout.strip().split("\n")[-1]
                # print(f" ------------------ Count: {stdout}")
                # read file numOfLatticePoints and return the count
                with open("numOfLatticePoints", 'r') as f:
                    count = f.read()
            return int(count)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"latte error: {e.stderr}")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"latte error: {e.stderr}")


def run_latte_on_matrix(matrix_file, timeout=3600):
    command = os.path.expanduser("~/latte/bin/count")
    toolname = "latte"
    return run_tool_on_matrix(matrix_file, toolname, command, timeout)


def run_volesti_on_matrix(matrix_file, timeout=3600):
    log(f"Running volesti...", 1)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    bin_dir = os.path.join(parent_dir, 'bin')
    # bin_dir = os.path.join(os.getcwd(), 'bin')
    command = os.path.join(bin_dir, 'volume')
    toolname = "volesti"
    result = subprocess.run([command, matrix_file], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in result.stdout.splitlines():
        if line.startswith("c vol"):
            parts = line.split()
            volume = float(parts[2])
            if volume < 0:
                print(f"c WARNING: Volume is negative ({volume})")
            break
        else:
            raise ValueError(
                "Volume line is malformed or volume is not a number")
    else:
        raise ValueError("Volume line not found in output")

    return volume


def run_bvcount_on_matrix(matrix_file, timeout=3600):
    polytope = Polytope.from_file(matrix_file)
    count = polytope.count_lattice_points()
    return count
