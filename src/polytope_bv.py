import numpy as np
from z3 import *
import argparse

# TODO get simplified insatnce of polytope from Latte



class Polytope:
    def __init__(self, A, b):
        self.A = A
        self.b = b
        self.optbw = False
        self.shift = None

    @staticmethod
    def from_file(filepath, optbw=False, shift=None):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            m, n = map(int, lines[0].strip().split())
            A = []
            b = []
            for line in lines[1:]:
                values = list(map(int, line.strip().split()))
                b.append(values[0])
                A.append(values[1:])
            A = np.array(A)
            b = np.array(b)
            return Polytope(A, b)

    def to_smt_bitvector(self):
        solver = Solver()
        n = self.A.shape[1]
        x = [BitVec(f'x{i}', 32) for i in range(n)]
        for i in range(len(self.b)):
            constraint = self.b[i] + sum(self.A[i][j] * x[j]
                                         for j in range(n)) <= 0
            solver.add(constraint)
        return solver

    def to_smt2_file(self, filepath):
        solver = self.to_smt_bitvector()
        f = And(solver.assertions())
        smt2_str = Z3_benchmark_to_smtlib_string(
            f.ctx_ref(), "benchmark", "QF_BV", "unknown", "", 0, None, f.as_ast())
        with open(filepath, 'w') as file:
            file.write(smt2_str)


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a polytope file.')
    parser.add_argument('input_file', type=str, help='Path to the input file')
    parser.add_argument('output_file', type=str, nargs='?', default='output.smt2',
                        help='Path to the output SMT2 file (default: output.smt2)')
    parser.add_argument('--shift', action='store_true',
                        help='Shift the polytope by given vector')
    parser.add_argument('--optbw', action='store_true',
                        help='Optimize bitwidth based on dimension range')

    args = parser.parse_args()

    polytope = Polytope.from_file(args.input_file, args.optbw, args.shift)

    if args.shift:
      shift_vector = np.array(args.shift)
      polytope.b = polytope.b - np.dot(polytope.A, shift_vector)

    polytope.to_smt2_file(args.output_file)
    print(f"SMT2 file {args.output_file} generated .")
