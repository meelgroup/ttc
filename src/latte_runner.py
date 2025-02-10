import math
import fractions
import subprocess
import os
import re
import sys
from .utils import log
import threading
from .global_storage import gbl
from .polytope_bv import Polytope


def stream_output(pipe, output_list):
    for line in iter(pipe.readline, ''):
        if gbl.verbosity >= 4:
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
    elif toolname.startswith("volesti"):
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
        # TODO: make this correct
        if "vp" in toolname:
            volesti_command.append("--vpoly")
        return volesti_command
    else:
        raise ValueError(f"Unknown toolname: {toolname}")


def handle_output(stdout_, stderr_, toolname):
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


def convert_fraction_to_decimal(input_file_path, output_file_path):
    """
    Reads each line from input_file_path, ignores any line starting with '*',
    and replaces fractional values (e.g., 119/86) with their decimal
    representation. Writes all processed lines to output_file_path.

    Example lines:
        1  119/86 -54/43 -39/43
    become, for instance:
        1  1.3837 -1.2558 -0.90698
    (printed with Python's default float precision; actual decimals may differ
    slightly depending on the fraction.)

    The rest of the formatting (line beginnings, number of spaces before/after
    tokens, etc.) is preserved as closely as possible. Any line starting with '*'
    is completely ignored in the output.
    """

    fraction_pattern = re.compile(r'([-+]?\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)')

    with open(input_file_path, 'r') as fin, open(output_file_path, 'w') as fout:
        for line in fin:
            # Ignore comment lines that start with '*'
            if line.lstrip().startswith('*'):
                continue

            # Function to replace "num/den" with a decimal
            def replace_fraction(match):
                # match.group(1) is the numerator part, match.group(2) is denominator
                numerator = fractions.Fraction(match.group(1))
                denominator = fractions.Fraction(match.group(2))
                val = numerator / denominator
                # Convert fraction to float, then to string
                return str(float(val))

            # Replace all fractional tokens with decimals
            # This preserves the original line's spacing around tokens,
            # but the fractional token itself is replaced in-place.
            new_line = fraction_pattern.sub(replace_fraction, line)

            fout.write(new_line)

def latte_to_ine_nofraction(input_file_path, output_file_path):
    with open(input_file_path, 'r') as f_in, open(output_file_path, 'w') as f_out:
        lines = f_in.readlines()
        # First line has two integers: number of constraints (m) and dimension (n)
        m, n = map(int, lines[0].strip().split())
        constraints = [line.strip() for line in lines[1:] if line.strip()]

        # Write to .ine file
        f_out.write("H-representation\n")
        f_out.write("begin\n")
        f_out.write(f" {m} {n} rational\n")
        for line in constraints:
            f_out.write(f" {line}\n")
        f_out.write("end\n")
        log(f"Converted {input_file_path} to {output_file_path}", 3)
        return 0


def latte_to_ine(input_file_path, output_file_path):
    with open(input_file_path, 'r') as f_in, open(output_file_path, 'w') as f_out:
        lines = f_in.readlines()
        # First line has two integers: number of constraints (m) and dimension (n)
        m, n = map(int, lines[0].strip().split())
        constraints = [line.strip() for line in lines[1:] if line.strip()]

        # Write the header to the .ine file
        f_out.write("H-representation\n")
        f_out.write("begin\n")
        f_out.write(f" {m} {n} rational\n")

        # Process each line: rationalize coefficients so they become integers
        for line in constraints:
            parts = line.split()
            # Convert each part to a Fraction
            frac_parts = [fractions.Fraction(p) for p in parts]

            # Compute LCM of denominators
            lcm_denom = 1
            for frac_part in frac_parts:
                lcm_denom = (
                    lcm_denom * frac_part.denominator) // math.gcd(lcm_denom, frac_part.denominator)

            # Multiply each fraction by the LCM to get integer coefficients
            int_parts = [frac_part * lcm_denom for frac_part in frac_parts]

            # Write out the integerized line
            f_out.write(" " + " ".join(str(int(p)) for p in int_parts) + "\n")

        f_out.write("end\n")

def convert_latte_to_polytope(matrix_file, type="vpolytope"):
    use_latte2ine_bin = False
    log(f"Converting latte to vpolytope...", 1)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    bin_dir = os.path.join(parent_dir, 'bin')
    latte2ine_path = os.path.join(bin_dir, 'latte2ine')
    lrs_path = os.path.join(bin_dir, 'lrs')

    if not os.path.isfile(latte2ine_path) and use_latte2ine_bin:
        raise FileNotFoundError(
            f"{latte2ine_path} does not exist. Please ensure that the tool is installed correctly.")
    if not os.path.isfile(lrs_path):
        raise FileNotFoundError(
            f"{lrs_path} does not exist. Please ensure that the tool is installed correctly.")

    ine_file = matrix_file + ".ine"

    if use_latte2ine_bin:
        with open(matrix_file, 'r') as infile, open(ine_file, 'w') as outfile:
            result = subprocess.run([latte2ine_path], text=True,
                                    stdin=infile, stdout=outfile, stderr=subprocess.PIPE)
    else:
        result = latte_to_ine(matrix_file, ine_file)

    if type == "hpolytope":
        return ine_file
    else:
        assert(type == "vpolytope")

    ext_file_temp = matrix_file + ".ext_temp"
    ext_file = matrix_file + ".ext"
    result = subprocess.run([lrs_path, ine_file, ext_file_temp],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    convert_fraction_to_decimal(ext_file_temp, ext_file)
    if result.returncode != 0:
        raise RuntimeError(
            f"latte2vpolytope failed with return code {result.returncode}")
    return ext_file


def run_volesti_on_matrix(matrix_file, timeout=3600):
    log(f"Running volesti...", 1)
    use_vpolytope = False
    if use_vpolytope:
        ext_file = convert_latte_to_polytope(matrix_file, type="vpolytope")
        with open(ext_file, 'r') as f:
            x = f.read()
            if "No feasible solution" in x:
                log("c [ttc->transformtovpolytope] No feasible solution found in this matrix", 4)
                return 0
        volume = run_tool_on_matrix(ext_file, toolname="volesti_vp")
    else:
        ine_file = convert_latte_to_polytope(matrix_file, type="hpolytope")
        volume = run_tool_on_matrix(ine_file, toolname="volesti")
    return volume
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



def run_bvcount_on_matrix(matrix_file, timeout=3600):
    polytope = Polytope.from_file(matrix_file)
    count = polytope.count_lattice_points()
    return count
