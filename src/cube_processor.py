from .latte_runner import run_latte_on_matrix
from .utils import *
import pandas as pd
import sys
from .global_storage import gbl


def process_cubes(cubes, mapping):
    log("Processing cubes to get final result", 1)
    final_sum = 0
    for i, cube in enumerate(cubes):
        log(f"Processing cube {i+1}/{len(cubes)}: {cube}", 2)
        # matrix_file = "matrix.tmp"
        latte_file_name = gbl.filename.split("/")[-1]
        latte_file_name = latte_file_name[:latte_file_name.rfind(
            '.')] + '.latte'
        
        # TODO good file name is not often accepted by latte!!
        # e.g., prime-cone_prime_cone_sat_5
        latte_file_name = "matrix.tmp"
        dfd = pd.DataFrame(columns=mapping.constraint_matrix.columns)
        for literal in cube:
            if literal in [0, 1, -2]:
                continue
            # if lit is not in constraint_matrix, then show warning and exit
            if literal not in mapping.constraint_matrix.index:
                log(f"Literal {literal} not found in constraint matrix", 3)
                continue
            dfd = dfd._append(mapping.constraint_matrix.loc[literal])
        # drop index
        write_matrix_to_file(dfd, latte_file_name)
        result = run_latte_on_matrix(latte_file_name)
        log(f"Result from latte for cube {i+1}: {result}", 2)
        final_sum += result

    return final_sum
