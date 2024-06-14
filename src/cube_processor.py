from .latte_runner import run_latte_on_matrix
from .utils import *
import pandas as pd
import sys

def process_cubes(cubes, mapping):
    log("Processing cubes to get final result", 1)
    final_sum = 0
    for i, cube in enumerate(cubes):
        log(f"Processing cube {i+1}/{len(cubes)}: {cube}", 2)
        matrix_file = "matrix.tmp"
        dfd = pd.DataFrame(columns=mapping.constraint_matrix.columns)
        for literal in cube:
            if literal in [0, 1]:
                continue
            # if lit is not in constraint_matrix, then show warning and exit
            if literal not in mapping.constraint_matrix.index:
                log(f"Literal {literal} not found in constraint matrix", 0)
                sys.exit(1)
            dfd = dfd._append(mapping.constraint_matrix.loc[literal])
        # drop index
        write_matrix_to_file(dfd, matrix_file)
        result = run_latte_on_matrix(matrix_file)
        log(f"Result from latte for cube {i+1}: {result}", 2)
        final_sum += result

    return final_sum