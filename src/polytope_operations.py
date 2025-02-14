import cdd
from .utils import log
from pprint import pprint

"""
This module provides functions to read, write, and canonicalize H-representations of polytopes.

Functions:
  read_h_representation(file_name):
    Reads an H-representation from a file in latte format.
    Args:
      file_name (str): The name of the file to read from.
    Returns:
      list: A list of lists representing the H-representation.

  write_h_representation(file_name, array):
    Writes an H-representation to a file in latte format.
    Args:
      file_name (str): The name of the file to write to.
      array (list): A list of lists representing the H-representation.

  canonicalize(input_file):

"""
from pprint import pprint

def read_h_representation(file_name):
    with open(file_name, 'r') as file:
        array = []
        rows, cols = 0, 0
        for line in file:
            if line.strip() and line.split()[0].replace('-', '', 1).replace('.', '', 1).isdigit():
              if rows == 0 and cols == 0:
                  rows, cols = map(int, line.split())
              else:
                  array.append([float(num) for num in line.split()])
    if len(array) != rows:
        print(f"Warning: expected {rows} rows from input, got {len(array)} rows")
    if len(array[0]) != cols:
        print(f"Warning: expected {cols} columns from input, got {len(array[0])} columns")
    log(f"c [ttc] canonicalizing array of size \
            {len(array)}x{len(array[0])} using cddlib", 2)
    return array

def write_h_representation(file_name, array, lin_set):
    if len(lin_set) > 0:
        log(f"Warning: exists {len(lin_set)} equalities, d-dim volume is zero for this polytope", 1)
        return 0
    with open(file_name, 'w') as file:
      file.write("H-representation\n")
      file.write("begin\n")
      file.write(f"{len(array)} {len(array[0])} rational\n")
      for row in array:
          file.write(' '.join(map(str, row)) + '\n')
      file.write("end\n")


def canonicalize(input_file):
    """
    Canonicalizes an H-representation read from a file in latte format and writes the result to a file in ine format. Uses cddlib for this purpose.
    If there exists any equality constraints in the input H-representation, the function will return 0 and print a warning message. In future, we may add support for handling equality constraints.
    Args:
        input_file (str): The name of the input file containing the H-representation in latte format.
    Returns:
        str: The name of the output file containing the canonicalized H-representation in ine format.
    """
    array = read_h_representation(input_file)
    mat = cdd.matrix_from_array(array, rep_type=cdd.RepType.INEQUALITY)
    # mat.rep_type = cdd.RepType.INEQUALITY

    cdd.matrix_canonicalize(mat)

    log(f"c [ttc] canonicalized array of size \
            {len(mat.array)}x{len(mat.array[0])} using cddlib", 2)

    output_file = input_file.split('.')[0] + '.ine'
    result = write_h_representation(output_file, mat.array, mat.lin_set)
    if result == 0:
        return 0
    return output_file

# Example usage:
# canonicalize_h_representation('input.txt', 'output.txt')