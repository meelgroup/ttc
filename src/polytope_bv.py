import numpy as np
import polytope as pc
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
        # TODO try balanced encoding
        solver = Solver()
        n = self.A.shape[1]
        bitwidth = self.determine_bitwidth()
        x = [BitVec(f'x{i}', bitwidth) for i in range(n)]
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

    def get_vertices(self):
        p = pc.Polytope(self.A, self.b)
        vertices = pc.extreme(p)
        return vertices

    def get_chebyshev_center(self):
        p = pc.Polytope(self.A, self.b)
        return p.chebXc

    def shift_to_positive_coordinates(self):
        # TODO this is not yet correct
        vertices = self.get_vertices()
        print("Vertices of the polytope before shifting:", vertices)
        min_coords = np.min(vertices, axis=0)
        print("Minimum coordinate values for each dimension:", min_coords)

        shift_vector = min_coords
        print("Shift vector to move all coordinates to positive space:", shift_vector)
        print("b vector before shifting:", self.b)

        self.b = self.b - np.dot(self.A, shift_vector)
        print("Updated b vector after shifting:", self.b)

        return shift_vector

    def determine_bitwidth(self):
        # TODO need to be careful about the bitwidth for the constant term
        vertices = self.get_vertices()
        if vertices is None:
            raise ValueError(
                "Vertices could not be determined by polytope library.")
        dimension = vertices.shape[1]
        max_value = np.max(np.abs(vertices))
        bitwidth = 2 * int(np.ceil(np.log2(max_value + 1))) + dimension
        print("Vertices ranges for each coordinate:")
        for i in range(vertices.shape[1]):
            coord_values = vertices[:, i]
            print(
                f"Coordinate {i}: min = {np.min(coord_values)}, max = {np.max(coord_values)}")
        print("Maximum absolute value among all vertices coordinates:", max_value)
        print("Determined bitwidth:", bitwidth)
        return bitwidth

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a polytope file.')
    parser.add_argument('input_file', type=str, help='Path to the input file')
    parser.add_argument('output_file', type=str, nargs='?', default='output.smt2',
                        help='Path to the output SMT2 file (default: output.smt2)')
    parser.add_argument('--shift',  action='store_true',
                        help='Shift the polytope by given vector')
    parser.add_argument('--optbw', action='store_true',
                        help='Optimize bitwidth based on dimension range')

    args = parser.parse_args()

    polytope = Polytope.from_file(args.input_file, args.optbw, args.shift)

    if args.shift:
        shift_vector = polytope.shift_to_positive_coordinates()
        print("Shift vector to positive coordinates:", shift_vector)

    vertices = polytope.get_vertices()
    chebyshev_center = polytope.get_chebyshev_center()
    print("Vertices:", vertices)
    print("Chebyshev Center:", chebyshev_center)

    polytope.to_smt2_file(args.output_file)
    print(f"SMT2 file {args.output_file} generated.")
