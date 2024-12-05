import os
import subprocess
import argparse
from .global_storage import gbl
import numpy as np


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="Convert SMT-LIB 2 constraints to matrix form using cvc5.")
    parser.add_argument('smt_file', type=str,
                        help='Path to the SMT-LIB 2 file.')
    parser.add_argument('-v', '--verbosity', type=int,
                        default=0, help='Set verbosity level.')
    parser.add_argument('-hall', '--hall', type=bool, default=False,
                        help='Use the HALL tool to convert CNF to DNF, default is Karnaugh map extension.')
    return parser


def check_existence_of_smt_file(smt_file):
    if not os.path.exists(smt_file):
        raise FileNotFoundError(f"c Input file not found in {smt_file}")


def check_existence_of_tools(tools):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Move one level up
    parent_dir = os.path.dirname(script_dir)
    # Replace cwd to the parent directory
    bin_dir = os.path.join(parent_dir, 'bin')
    print(f"bin_dir: {bin_dir}")
    # bin_dir = os.path.join(os.getcwd(), 'bin')
    for tool in tools:
        tool_path = os.path.join(bin_dir, tool)
        if not os.path.isfile(tool_path):
            raise EnvironmentError(f"{tool} not found in the 'bin' directory.")
        if not os.access(tool_path, os.X_OK):
            raise EnvironmentError(
                f"{tool} is not executable in the 'bin' directory.")


def set_cnf_to_dnf_tool(use_hall):
    if use_hall:
        gbl.cnf_to_dnf_tool = 'hall'
        gbl.tool_list.append('hall_tool')
    else:
        gbl.cnf_to_dnf_tool = 'cnftranslate'
        gbl.tool_list.append('cnftranslate')


def write_matrix_to_file(matrix, output_file):
    log(f"Writing matrix to file: {output_file}", 2)
    matrix_array = matrix.to_numpy()

    # Get the size of the matrix
    num_constraints, num_variables = matrix_array.shape

    with open(output_file, 'w') as f:
        f.write(f"{num_constraints} {num_variables}\n")
        for row in matrix_array:
            f.write(" ".join(map(str, row)) + "\n")


def log(message, level=1):
    if gbl.verbosity >= level:
        print(message)


def clean_on_exit(temp_files):
    log("Cleaning up...", 2)
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            log(f"Removed {file}", 3)
    log("Cleaned up.", 2)
