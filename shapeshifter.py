from src import *


def shapeshifter():
    parser = get_arg_parser()
    args = parser.parse_args()

    set_verbosity(args.verbosity)
    set_cnf_to_dnf_tool(args.hall)

    check_existence_of_smt_file(args.smt_file)
    check_existence_of_tools(gbl.tool_list)

    smt_output = run_cvc5_on_smt_file(args.smt_file)
    mapping, cnf_file = parse_cvc5_output(smt_output)

    dnf_file = run_hall_on_cnf_file(cnf_file)
    cubes = parse_dnf_file(dnf_file)

    final_result = process_cubes(cubes, mapping)

    print(f"Final count: {final_result}")


if __name__ == "__main__":
    shapeshifter()
