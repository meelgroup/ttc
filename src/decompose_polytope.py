import os
import subprocess
import sys


def read_vertices_file(file_path):
    """
    Reads a vertices file and calculates the range of values for each dimension.

    Parameters:
        file_path (str): Path to the vertices.txt file.

    Returns:
        list of tuples: Each tuple contains (min_value, max_value) for each dimension.
    """
    vertices = []

    try:
        with open(file_path, 'r') as file:
            is_reading_vertices = False

            for line in file:
                line = line.strip()

                # Begin reading vertices after "begin" keyword
                if line.lower() == "begin":
                    is_reading_vertices = True
                    continue

                # Stop reading vertices after "end" keyword
                if line.lower() == "end":
                    is_reading_vertices = False
                    break

                # Skip non-vertex data
                if not is_reading_vertices or line.startswith("*") or "rational" in line or "real" in line:
                    continue

                # Parse vertex lines
                if line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            vertices.append(list(map(float, parts[1:])))
                        except ValueError:
                            raise ValueError(
                                f"Invalid numeric data in line: {line}")

        if not vertices:
            raise ValueError("No vertices found in the file.")

        # Transpose the vertices to calculate ranges for each dimension
        dimensions = zip(*vertices)
        ranges = [(min(dim), max(dim)) for dim in dimensions]

        return ranges

    except Exception as e:
        print(f"Error reading the file: {e}")
        return []


def calculate_and_sort_ranges(ranges, decompose_lim):
    """
    Calculate the lengths of the ranges, sort dimensions by increasing length, and find dimensions with product of lengths < 100.

    Parameters:
        ranges (list of tuples): Each tuple contains (min_value, max_value) for each dimension.

    Returns:
        list: Dimensions sorted by increasing length whose product of lengths < 100.
    """
    lengths = [(i, r[1] - r[0]) for i, r in enumerate(ranges)]
    lengths.sort(key=lambda x: x[1])

    selected_dimensions = []
    product = 1

    for dim, length in lengths:
        if product * length < decompose_lim:
            # Dim + 1 for 1-based indexing
            selected_dimensions.append((dim + 1, length))
            product *= length
        else:
            break

    return selected_dimensions


def convert_latte_to_vertices(latte_filename):
    # run ~/latte/bin/latte2ext <  latte_filename > latte.ext
    cdd_output = None
    latte2ext_command = os.path.expanduser("~/latte/bin/latte2ext")
    latte_ext_filename = latte_filename[:latte_filename.rfind('.')] + '.ext'
    try:
        with open(latte_ext_filename, 'w') as f:
          cdd_output = subprocess.run([latte2ext_command], stdin=open(
              latte_filename, 'r'), stdout=f, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    # run cddexec --rep < latte.ext
    print("")
    cddexec_command = os.path.expanduser("cddexec")
    with open('cdd_output.txt', 'w') as cdd_output_file:
      cdd_output = subprocess.run(
          f"{cddexec_command} --rep < {latte_ext_filename}", shell=True, stdout=cdd_output_file, check=True, text=True)
    # cdd_output = subprocess.run([]
    #                             f"{cddexec_command} --rep < {latte_ext_filename}", shell=True, stdout=subprocess.PIPE, check=True, text=True)
    return 'cdd_output.txt'


def get_dimension_range_from_vertices(dimension_ranges, decompose_lim):
    for i, (min_val, max_val) in enumerate(dimension_ranges):
        print(f"Dimension {i + 1}: Min = {min_val}, Max = {max_val}")

    sorted_dimensions = calculate_and_sort_ranges(
        dimension_ranges, decompose_lim)
    print("\nDimensions sorted by length with product < 100:")
    for dim, length in sorted_dimensions:
        print(f"Dimension {dim}: Length = {length}")


def decompose_polytope(latte_filename, decompose_lim):
    vertices_file = convert_latte_to_vertices(latte_filename)
    dimension_ranges = read_vertices_file(vertices_file)
    get_dimension_range_from_vertices(dimension_ranges, decompose_lim)
