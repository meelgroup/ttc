from src.smt_parser import SMTParser
from src.smt_matrix_converter import SMTToMatrixConverter, write_matrix_to_file
from src.latte_runner import run_latte_on_matrix
from src.utils import log

def process_cubes(cubes, mapping):
    log("Processing cubes to get final result", 1)

    final_sum = 0

    for i, cube in enumerate(cubes):
        log(f"Processing cube {i+1}/{len(cubes)}: {cube}", 2)
        matrix_file = "matrix.tmp"
        inequalities = mapping.get_inequalities(cube)
        smt_parser = SMTParser()
        smt_transformer = smt_parser.parse("\n".join(inequalities))
        converter = SMTToMatrixConverter(smt_transformer)
        matrix = converter.convert()
        write_matrix_to_file(matrix, matrix_file)
        result = run_latte_on_matrix(matrix_file)
        log(f"Result from latte for cube {i+1}: {result}", 2)
        final_sum += result

    return final_sum
