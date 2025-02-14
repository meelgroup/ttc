from .latte_runner import run_latte_on_matrix, run_volesti_on_matrix, run_bvcount_on_matrix
from .decompose_polytope import decompose_polytope
from .utils import *
import pandas as pd
import sys
from .global_storage import gbl


def process_cubes(cubes, mapping):
    log("Processing cubes to get final result", 1)
    final_sum = 0
    result = 0
    for i, cube in enumerate(cubes):
        log(f"Processing cube {i+1}/{len(cubes)}: {cube}", 2)
        # matrix_file = "matrix.tmp"
        latte_file_name = gbl.filename.split("/")[-1]
        latte_file_name = latte_file_name[:latte_file_name.rfind(
            '.')] + '.latte'

        # TODO good file name is not often accepted by latte!!
        # e.g., prime-cone_prime_cone_sat_5
        latte_file_name = f"matrix{i+1}.tmp"
        dfd = pd.DataFrame(columns=mapping.constraint_matrix.columns)
        for literal in cube:
            if literal in [0, 1, -2]:
                continue
            # if lit is not in constraint_matrix, then show warning and exit
            if literal not in mapping.constraint_matrix.index:
                log(f"Literal {literal} not found in constraint matrix", 3)
                continue
            temp_row = mapping.constraint_matrix.loc[[literal]]
            if dfd.empty:
                dfd = temp_row
            dfd = pd.concat([dfd, temp_row])
        # drop index
        write_matrix_to_file(dfd, latte_file_name)
        if gbl.decompose_lim > 0:
            latte_filenames = decompose_polytope(
                latte_file_name, gbl.decompose_lim)
            if latte_filenames is not None:
                for latte_file_name in latte_filenames:
                    run_volesti_on_matrix(latte_file_name)
                    result = run_latte_on_matrix(latte_file_name)
                    final_sum += result
        else:
            if gbl.logic == "lra":
                assert (gbl.logic == "lra")
                result = run_volesti_on_matrix(latte_file_name)
            else:
                assert (gbl.logic == "lia")
                if gbl.usebv:
                    result = run_bvcount_on_matrix(latte_file_name)
                else:
                    result = run_latte_on_matrix(latte_file_name)
        log(f"Result from latte for cube {i+1}: {result}", 2)
        final_sum += result

    return final_sum
