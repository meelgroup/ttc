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


def run_tool_on_matrix(matrix_file, toolname, timeout=3600):
    log(f"Running {toolname}...", 2)
    count_command = get_count_command(toolname)
    if isinstance(count_command, list):
        count_command.insert(1, matrix_file)
    else:
        count_command = [count_command, matrix_file]
    log(f"{toolname} command:  {count_command}", 3)

    stdout_lines = []
    stderr_lines = []

    try:
        with subprocess.Popen(count_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) as proc:
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
                raise RuntimeError(
                    f"{toolname} process timed out after 1 hour")

            stdout_thread.join()
            stderr_thread.join()

            # Join the captured output
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)

            # Check for specific error message in stdout or stderr

            count = handle_output(stdout, stderr, toolname)

            return int(count)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def get_count_command(toolname):
    if toolname == "latte":
        latte_path = os.path.expanduser("~/latte/bin/count")
        if not os.path.isfile(latte_path):
            raise FileNotFoundError(
                f"{latte_path} does not exist. Please ensure that the tool is installed correctly.")
        return latte_path
    elif toolname == "volesti":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        bin_dir = os.path.join(parent_dir, 'bin')
        volesti_path = os.path.join(bin_dir, 'volume')
        if not os.path.isfile(volesti_path):
            raise FileNotFoundError(
                f"{volesti_path} does not exist. Please ensure that the tool is installed correctly.")
        volesti_command = [volesti_path, gbl.volesti_algo,
                           str(gbl.volesti_walk_length)]
        volesti_command = [volesti_path]
        return volesti_command
    else:
        raise ValueError(f"Unknown toolname: {toolname}")


def handle_output(stdout_, stderr_, toolname):
    print(f"got this from tool output: {stdout_} {stderr_}")
    error_message = "is unbounded"
    count = -1
    empty_polytope_message = "Empty polytope or unbounded polytope!"
    if error_message in stdout_ or error_message in stderr_:
        log(
            "Unbounded polytope!\n TODO: Make sure this polytope is not empty", 0)
        sys.exit(0)
    if empty_polytope_message in stdout_ or empty_polytope_message in stderr_:
        log("Empty polytope!", 3)
    elif toolname == "latte":
        with open("numOfLatticePoints", 'r') as f:
            count = f.read()
    elif toolname == "volesti":
        for line in stdout_.splitlines():
            if line.startswith("c vol"):
                parts = line.split()
                if parts[2] == "inf":
                    return 0
                count = float(parts[2])
                if count < 0:
                    print(f"c WARNING: Volume is negative ({count})")
                break
        if count == -1:
            print(stdout_)
            raise ValueError("Volume line not found in output")
    else:
        raise ValueError(f"Unknown toolname: {toolname}")
    return count


def run_latte_on_matrix(matrix_file, timeout=3600):
    toolname = "latte"
    return run_tool_on_matrix(matrix_file, toolname, timeout)


def convert_latte_to_vpolytope(matrix_file):
    log(f"Converting latte to vpolytope...", 1)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    bin_dir = os.path.join(parent_dir, 'bin')
    latte2ine_path = os.path.join(bin_dir, 'latte2ine')
    lrs_path = os.path.join(bin_dir, 'lrs')

    if not os.path.isfile(latte2ine_path):
        raise FileNotFoundError(
            f"{latte2ine_path} does not exist. Please ensure that the tool is installed correctly.")
    if not os.path.isfile(lrs_path):
        raise FileNotFoundError(
            f"{lrs_path} does not exist. Please ensure that the tool is installed correctly.")

    ine_file = matrix_file + ".ine"
    ext_file = matrix_file + ".ext"

    with open(matrix_file, 'r') as infile, open(ine_file, 'w') as outfile:
        result = subprocess.run([latte2ine_path], text=True,
                                stdin=infile, stdout=outfile, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(
            f"latte2vpolytope failed with return code {result.returncode}")
    result = subprocess.run([lrs_path, ine_file, ext_file],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ext_file


def run_volesti_on_matrix(matrix_file, timeout=3600):
    log(f"Running volesti...", 1)
    ine_file = convert_latte_to_vpolytope(matrix_file)
    with open(ine_file, 'r') as f:
        x = f.read()
        if "No feasible solution" in x:
            log("****** No feasible solution found in this matrix", 4)
            return 0
    volume = run_tool_on_matrix(ine_file, toolname="volesti")
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # parent_dir = os.path.dirname(script_dir)
    # bin_dir = os.path.join(parent_dir, 'bin')
    # # bin_dir = os.path.join(os.getcwd(), 'bin')
    # toolname = "volesti"
    # # Generate .ine file using latte2ine
    # ine_file = matrix_file + ".ine"

    # command = os.path.join(bin_dir, "latte2ine")

    # # with open(ine_file, 'w') as f:
    # #     subprocess.run([command], stdin=open(matrix_file),
    # #                    stdout=f, stderr=subprocess.PIPE, text=True)

    # # Run volesti on the generated .ine file
    # command = os.path.join(bin_dir, 'volume')

    # result = subprocess.run([command,  matrix_file], text=True,
    #                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # for line in result.stdout.splitlines():
    #     if line.startswith("c vol"):
    #         parts = line.split()
    #         volume = float(parts[2])
    #         if volume < 0:
    #             print(f"c WARNING: Volume is negative ({volume})")
    #         break
    #     # else:
    #     raise ValueError(
    #         "Volume line is malformed or volume is not a number")
    # else:
    #     raise ValueError("Volume line not found in output")

    return volume


def run_bvcount_on_matrix(matrix_file, timeout=3600):
    polytope = Polytope.from_file(matrix_file)
    count = polytope.count_lattice_points()
    return count
