import os
import subprocess
import argparse
from .global_storage import gbl
import numpy as np
import random
import string
import pandas as pd


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="Convert SMT-LIB 2 constraints to matrix form using cvc5.")
    parser.add_argument('smt_file', type=str,
                        help='Path to the SMT-LIB 2 file.')
    parser.add_argument('-v', '--verbosity', type=int,
                        default=0, help='Set verbosity level.')
    parser.add_argument("--nohall", action="store_true",
                        help='Use the Karnaugh map extension to convert CNF to DNF, default is HALL tool.')
    parser.add_argument("--cubes", action="store_true",
                        help='Decompose into cubes and exit.')
    parser.add_argument("--intbv", action="store_true", default=False,
                        help='Count lattice points using bv counter.')
    parser.add_argument("--pact", action="store_true", default=False,
                        help='Count lattice points using pact counter.')
    parser.add_argument("--optcnt", action="store_true", default=False,
                        help='Count lattice points by solving optimization.')
    parser.add_argument("-l", "--decomposelim", type=int, default=0,
                        help='Limit on the number of decompositions.')
    parser.add_argument("-d", "--disjoint", action="store_true",
                        help='Use disjoint decomposition in LRA (disjoint is defualt in LIA).')
    parser.add_argument("--seed", type=int, default=123,
                        help='Random seed to use in random algorithms.')
    parser.add_argument("--dontdelete", action="store_true",
                        help='Do not delete temporary files.')

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
    log(f"bin_dir: {bin_dir}", 4)
    # bin_dir = os.path.join(os.getcwd(), 'bin')
    for tool in tools:
        tool_path = os.path.join(bin_dir, tool)
        if not os.path.isfile(tool_path):
            raise EnvironmentError(f"{tool} not found in the 'bin' directory.")
        if not os.access(tool_path, os.X_OK):
            raise EnvironmentError(
                f"{tool} is not executable in the 'bin' directory.")

def write_matrix_to_file(matrix, output_file):
    log(f"Writing matrix to file: {output_file}", 4)
    matrix_array = matrix.to_numpy()

    # Get the size of the matrix
    num_constraints, num_variables = matrix_array.shape

    with open(output_file, 'w') as f:
        f.write(f"{num_constraints} {num_variables}\n")
        for row in matrix_array:
            f.write(" ".join(map(str, row)) + "\n")

def print_final_result(final_result):
    log(f"Total time: {(time.time() - gbl.starttime):.3f} s")

    if gbl.logic == "lia":
        resultstr = "s mc"
    else:
        resultstr = "s vol"
    print(f"{resultstr} {final_result}")

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


def create_all_polytope_files(cubes, mapping):
    filenames = []
    random_prefix = ''.join(random.choice(string.ascii_letters)
                            for _ in range(8))
    for i, cube in enumerate(cubes):
        filename = create_polytope_from_cube(
            cube, mapping, f"{random_prefix}_cube{i+1}.ine")
        filenames.append(filename)
    log(f"Created {len(filenames)} polytope files", 2)
    return filenames

def cleanup():
    if gbl.dontdelete:
        log("Skipping cleanup as --dontdelete is set", 3)
        return
    files = gbl.tempfiles
    log("Cleaning up...", 3)
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            log(f"Removed {file}", 4)
    log("Cleaned up.", 3)


