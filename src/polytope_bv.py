import numpy as np
from z3 import *

# TODO get simplified insatnce of polytope from Latte


class Polytope:
    def __init__(self, A, b):
        self.A = A
        self.b = b

    @staticmethod
    def from_file(filepath):
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
            f.ctx, "benchmark", "QF_BV", "unknown", "", 0, None, f)
        with open(filepath, 'w') as file:
            file.write(smt2_str)


# Example usage
if __name__ == "__main__":
    polytope = Polytope.from_file('/home/arijit/solvers/ttc/matrix8.tmp')
    polytope.to_smt2_file('/home/arijit/solvers/ttc/polytope_constraints.smt2')
    print("SMT2 file generated.")
