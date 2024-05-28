import subprocess
from src.literal_mapping import LiteralMapping
from src.utils import log


def run_cvc5_on_smt_file(smt_file):
    log(f"Running cvc5 on {smt_file}", 1)
    # RUN my version of CVC5 which outputs mapping
    result = subprocess.run(["cvc5", smt_file], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"cvc5 error: {result.stderr}")
    log(f"cvc5 output: {result.stdout}", 3)
    return result.stdout


def parse_cvc5_output(output):
    log("Parsing cvc5 output", 1)
    mapping = LiteralMapping()
    cnf_lines = []
    for line in output.splitlines():
        if line.startswith('c '):
            parts = line.split(':')
            # TODO assert that ~ could be skipped
            if '~' in parts[0]:
                continue
            literal = int(parts[0][2:])
            inequality = parts[1].strip()
            if '~' in parts[0]:
                literal = -literal
            mapping.add_mapping(literal, inequality)
        # TODO skip unsat text
        elif line.startswith('p cnf') or (not line.startswith('c')) or (not line.startswith('u')):
            cnf_lines.append(line)
    cnf_content = "\n".join(cnf_lines)
    log(f"Parsed CNF content: \n{cnf_content} \n cnf end", 2)
    # TODO save cnf to a file and store the location in cnf_location, maybe temp
    cnf_content = "box.cnf"
    return mapping, cnf_content
