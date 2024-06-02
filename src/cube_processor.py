from .latte_runner import run_latte_on_matrix
from .utils import *


def process_cubes(cubes, mapping):
    log("Processing cubes to get final result", 1)

    final_sum = 0

    for i, cube in enumerate(cubes):
        log(f"Processing cube {i+1}/{len(cubes)}: {cube}", 2)
        matrix_file = "matrix.tmp"
        inequalities = mapping.get_inequalities(cube)
        # smt_parser = SMTParser()
        # smt_transformer = smt_parser.parse("\n".join(inequalities))
        # log(f"Transformed SMT: {smt_transformer}", 3)
        # converter = SMTToMatrixConverter(smt_transformer)
        # matrix = converter.convert()
        write_matrix_to_file(inequalities, matrix_file)
        result = run_latte_on_matrix(matrix_file)
        log(f"Result from latte for cube {i+1}: {result}", 2)
        final_sum += result

    return final_sum
