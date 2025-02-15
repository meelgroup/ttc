import numpy as np
import polytope as pc
from z3 import *
from z3.z3util import is_bv_value
import argparse
import subprocess
from .utils import log

# TODO get simplified insatnce of polytope from Latte

class Polytope:
    def __init__(self, A, b):
        self.A = A
        self.b = b
        self.optbw = False
        self.shift = None
        self.smtfilename = "temp.smt2"
        self.vertices = None
        self.count = None
        self.max_coords = []

    @staticmethod
    def from_file(filepath, optbw=True, shift=True):
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
        # TODO potential error -- wrong variables are taken?
        x = [BitVec(f'x{i}', bitwidth) for i in range(n)]
        for i in range(len(self.b)):
            constraint = sum(self.A[i][j] * x[j]
                                  for j in range(n)) <= self.b[i]
            solver.add(constraint)
            log(f"c [ttc->tobv] Adding constraint: {constraint} \n for {self.A[i]} and {self.b[i]}",3)
        for i in range(len(self.max_coords)):
            solver.add(x[i] <= self.max_coords[i])
            solver.add(x[i] > 0)
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
        if pc.is_empty(p):
          log(f"c [ttc->tobv] Polytope {self.A,self.b} is empty", 3)
          return None
        vertices = pc.extreme(p)
        return vertices

    def get_chebyshev_center(self):
        p = pc.Polytope(self.A, self.b)
        return p.chebXc

    def get_radius(self):
        p = pc.Polytope(self.A, self.b)
        return p.chebR

    def shift_to_positive_coordinates(self):
        # TODO this is not yet correct
        vertices = self.get_vertices()
        log(f"Vertices of the polytope before shifting: {vertices}", 5)
        min_coords = np.floor(np.min(vertices, axis=0))
        log("Minimum coordinate values for each dimension: {min_coords}", 5)

        shift_vector = min_coords - 1
        # print("Shift vector to move all coordinates to positive space:", shift_vector)
        # print("b vector before shifting:", self.b)
        # print("shift vector:", shift_vector)
        p = pc.Polytope(self.A, self.b)
        vertices = pc.extreme(p)
        # print("vertices before shifting:", vertices)
        p = p.translation(- shift_vector)
        vertices = pc.extreme(p)
        # print("vertices after shifting:", vertices)

        self.b = self.b - np.dot(self.A, shift_vector)
        p = pc.Polytope(self.A, self.b)
        vertices = pc.extreme(p)
        log(f"c [ttc->tobv] vertices after our shifting: {vertices}", 5)
        log(f"shifted polytope {self.A} {self.b}", 5)
        if vertices is not None:
            self.max_coords = np.ceil(np.max(vertices, axis=0))
        else:
            self.max_coords = None
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
        log("c [ttc->tobv] Vertices ranges for each coordinate:", 4)
        for i in range(vertices.shape[1]):
            coord_values = vertices[:, i]
            log(f"c [ttc->tobv] Coordinate {i}: min = {np.min(coord_values)}, max = {np.max(coord_values)}", 4)
        log("c [ttc->tobv] Maximum absolute value among all vertices coordinates: {max_value}", 4)
        log("c [ttc->tobv] Determined bitwidth: {bitwidth}", 4)
        return bitwidth

    def count_lattice_points(self):
        # polytope = Polytope.from_file(args.input_file, args.optbw, args.shift)
        if self.get_vertices() is None:
          log("c [ttc->tobv] Polytope is empty",3)
          return 0
        self.shift_to_positive_coordinates()
        self.to_smt2_file(self.smtfilename)

        def run_csb_and_get_count(filename):
          script_dir = os.path.dirname(os.path.abspath(__file__))
          parent_dir = os.path.dirname(script_dir)
          bin_dir = os.path.join(parent_dir, 'bin')
          csb_path = os.path.join(bin_dir, 'csb')
          result = subprocess.run(
              [csb_path, '-c', filename], capture_output=True, text=True)
          output_lines = result.stdout.splitlines()
          for line in output_lines:
            if line.startswith("s mc"):
              return int(line.split()[2])
          raise ValueError("Count not found in the output")

        count = run_csb_and_get_count(self.smtfilename)
        print("Lattice point count:", count)
        return count


    def check_equivalence(self):
        solver = self.to_smt_bitvector()
        n = self.A.shape[1]
        bitwidth = self.determine_bitwidth()
        x = [BitVec(f'x{i}', bitwidth) for i in range(n)]

        # Convert bitvector constraints back to polytope
        constraints = solver.assertions()
        A_bv = []
        b_bv = []
        for constraint in constraints:
            lhs = constraint.arg(0)
            rhs = constraint.arg(1)
            A_row = []
            b_value = -simplify(rhs).as_long()
            for i in range(n):
                arg = lhs.arg(i)
                if is_bv_value(arg):
                    coeff = arg.as_long()
                elif is_bv_mul(arg):
                    coeff = arg.arg(0).as_long()
                else:
                    print(f"Non-numeric argument encountered: {arg}")
                    coeff = 0
                A_row.append(coeff)
            A_bv.append(A_row)
            b_bv.append(b_value)

        A_bv = np.array(A_bv)
        b_bv = np.array(b_bv)
        polytope_bv = pc.Polytope(A_bv, b_bv)

        # Compare the original polytope with the one obtained from bitvector constraints
        original_polytope = pc.Polytope(self.A, self.b)
        return original_polytope == polytope_bv

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
    chebyshev_radius = polytope.get_radius()
    print("Vertices:", vertices)
    print("Chebyshev Center:", chebyshev_center)
    print("Chebyshev Radius (outscribe):", chebyshev_radius)
    polytope.to_smt2_file(args.output_file)
    print(f"SMT2 file {args.output_file} generated.")
    count = polytope.count_lattice_points()
    print(f"Lattice point count: {count}")

    # equivalent = polytope.check_equivalence()
    # print(
    #     f"Bitvector constraints are equivalent to the input polytope: {equivalent}")
