import subprocess
from literal_mapping import LiteralMapping
from utils import log

def run_cvc5_on_smt_file(smt_file):
    log("Executing cvc5...", 2)
    result = subprocess.run(["cvc5", smt_file], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"cvc5 error: {result.stderr}")
    log(f"cvc5 output: {result.stdout}", 3)
    return result.stdout

def parse_cvc5_output(output):
    mapping = LiteralMapping()
    cnf_lines = []
    for line in output.splitlines():
        if line.startswith('c '):
            parts = line.split(':')
            literal = int(parts[0][2:])
            inequality = parts[1].strip()
            if '~' in parts[0]:
                literal = -literal
            mapping.add_mapping(literal, inequality)
        elif line.startswith('p cnf') or line.startswith(' '):
            cnf_lines.append(line)
    cnf_content = "\n".join(cnf_lines)
    log(f"Parsed CNF content: {cnf_content}", 2)
    return mapping, cnf_content
