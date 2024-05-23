import argparse
from src.cvc5_runner import run_cvc5_on_smt_file, parse_cvc5_output
from src.hall_runner import run_hall_on_cnf_content, parse_dnf_content
from src.cube_processor import process_cubes
from src.utils import check_existence, check_tools, set_verbosity, log
from src.global_storage import global_storage

def main():
    parser = argparse.ArgumentParser(description="Convert SMT-LIB 2 constraints to matrix form using cvc5.")
    parser.add_argument('smt_file', type=str, help='Path to the SMT-LIB 2 file.')
    parser.add_argument('-v', '--verbosity', type=int, default=0, help='Set verbosity level.')
    args = parser.parse_args()

    set_verbosity(args.verbosity)

    check_existence([{'name': 'SMT file', 'path': args.smt_file}])
    check_tools(['cvc5', 'hall', 'latte'])

    smt_output = run_cvc5_on_smt_file(args.smt_file)

    mapping, global_storage.cnf_content = parse_cvc5_output(smt_output)

    global_storage.dnf_content = run_hall_on_cnf_content(global_storage.cnf_content)

    cubes = parse_dnf_content(global_storage.dnf_content)

    final_result = process_cubes(cubes, mapping)

    print(f"Final count: {final_result}")


if __name__ == "__main__":
    main()
