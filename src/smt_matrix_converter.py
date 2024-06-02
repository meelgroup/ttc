from .utils import log
import numpy as np


class SMTToMatrixConverter:
    def __init__(self, smt_transformer):
        self.smt_transformer = smt_transformer

    def convert(self):
        log("Converting SMT to matrix", 2)
        variables = sorted(self.smt_transformer.variables)
        num_constraints = len(self.smt_transformer.constraints)
        num_variables = len(variables) + 1  # +1 for the constant terms
        matrix = [[0] * num_variables for _ in range(num_constraints)]

        for i, constraint in enumerate(self.smt_transformer.constraints):
            for var, coef in constraint.items():
                if var == 'const':
                    matrix[i][-1] = coef
                else:
                    var_idx = variables.index(var)
                    matrix[i][var_idx] = coef

        return num_constraints, num_variables, matrix


def write_matrix_to_file(matrix, output_file):
    log(f"Writing matrix to file: {output_file}", 2)
    matrix = np.array([list(map(int, row.split())) for row in matrix])
    # Get the size of the matrix
    num_constraints, num_variables = matrix.shape
    with open(output_file, 'w') as f:
        f.write(f"{num_constraints} {num_variables}\n")
        for row in matrix:
            f.write(" ".join(map(str, row)) + "\n")
