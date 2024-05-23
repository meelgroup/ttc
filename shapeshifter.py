import argparse
from cvc5_runner import run_cvc5_on_smt_file, parse_cvc5_output
from hall_runner import run_hall_on_cnf_content, parse_dnf_content
from cube_processor import process_cubes
from utils import check_existence, check_tools, set_verbosity, log
from global_storage import global_storage

def main():
    parser = argparse.ArgumentParser(description="Convert SMT-LIB 2 constraints to matrix form using cvc5.")
    parser.add_argument('smt_file', type=str, help='Path to the SMT-LIB 2 file.')
    parser.add_argument('-v', '--verbosity', type=int, default=0, help='Set verbosity level.')
    args = parser.parse_args()

    set_verbosity(args.verbosity)

    check_existence([{'name': 'SMT file', 'path': args.smt_file}])
    check_tools(['cvc5', 'hall', 'latte'])

    log(f"Running cvc5 on {args.smt_file}", 1)
    smt_output = run_cvc5_on_smt_file(args.smt_file)

    log("Parsing cvc5 output", 1)
    mapping, global_storage.cnf_content = parse_cvc5_output(smt_output)

    log("Running hall to convert CNF to DNF", 1)
    global_storage.dnf_content = run_hall_on_cnf_content(global_storage.cnf_content)

    log("Parsing DNF content", 1)
    cubes = parse_dnf_content(global_storage.dnf_content)

    log("Processing cubes to get final result", 1)
    final_result = process_cubes(cubes, mapping)

    print(f"Final result: {final_result}")

if __name__ == "__main__":
    main()
