import argparse
import z3
import os
import random


def parse_variables(smt_file_content):
    """Parse integer variables from the SMT-LIB file content using Z3."""
    solver = z3.Solver()
    smt_formula = z3.parse_smt2_string(smt_file_content)
    solver.add(smt_formula)
    variables = set()

    # Iterate over the declarations in the SMT formula
    for assertion in smt_formula:
        # Collect all the variables in the assertion
        for var in z3.z3util.get_vars(assertion):
            if var.sort() == z3.IntSort():
                variables.add(var.decl().name())

    return list(variables)


def add_constraints(variables, bound):
    """Create constraints for the given variables with the specified bound."""
    constraints = []
    for var in variables:
        constraints.append(f"(assert (> {var} {-bound}))")
        constraints.append(f"(assert (< {var} {bound}))")
    return "\n".join(constraints)


def process_file(input_file, output_file, bound):
    """Process the input SMT-LIB file and write the bounded constraints to the output file."""
    with open(input_file, 'r') as f:
        smt_content = f.read()

    variables = parse_variables(smt_content)
    new_constraints = add_constraints(variables, bound)

    # Insert the new constraints before the final (check-sat) statement
    smt_content = smt_content.replace(
        '(check-sat)', f'{new_constraints}\n(check-sat)')

    with open(output_file, 'w') as f:
        f.write(smt_content)


# def process_file(input_file, output_file, bound):
#     # Placeholder for file processing logic
#     with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
#         for line in infile:
#             outfile.write(line.replace('VAR_BOUND', str(bound)))
#     print(f"Processed file saved as {output_file}")


def process_list(file_list, bounds):
    bounded_folder = 'bounded'
    os.makedirs(bounded_folder, exist_ok=True)

    if len(file_list) > 10:
        file_list = random.sample(file_list, 10)

    for file in file_list:
        for bound in bounds:
            output_file = os.path.join(
                bounded_folder, f"{os.path.basename(file)}_bounded_{bound}.smt2")
            process_file(file, output_file, bound)


def main():
    parser = argparse.ArgumentParser(
        description='Add constraints to SMT-LIB file.')
    parser.add_argument('--bound', type=int,
                        help='The bound for the variables.')
    parser.add_argument('--list', type=str,
                        help='File containing list of SMT-LIB files.')
    parser.add_argument('filename', type=str, nargs='?',
                        help='The input SMT-LIB file.')

    args = parser.parse_args()

    if args.list:
        with open(args.list, 'r') as list_file:
            file_list = [line.strip() for line in list_file if line.strip()]
        bounds = [5, 10, 20, 30, 50, 60, 100]
        process_list(file_list, bounds)
    elif args.filename and args.bound is not None:
        input_file = args.filename
        bound = args.bound
        output_file = f"{input_file}_bounded_{bound}.smt2"
        process_file(input_file, output_file, bound)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
