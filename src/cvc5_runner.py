import os
import subprocess
from .literal_mapping import LiteralMapping
from .utils import log
from .global_storage import gbl

class CVC5Runner:
    def __init__(self, smt_file):
        self.smt_file = smt_file
        self.cvcoutput = None

    def run_cvc5_on_smt_file(self):
        log(f"Running cvc5 on {self.smt_file}", 1)
        # RUN my version of CVC5 which outputs mapping
        result = subprocess.run(["cvc5", self.smt_file],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"cvc5 error: {result.stderr}")
        log(f"cvc5 output: {result.stdout}", 4)
        self.cvcoutput = result.stdout

    def parse_cvc5_output(self):
        log("Parsing cvc5 output", 1)
        mapping = LiteralMapping()
        cnf_lines = []
        for line in self.cvcoutput.splitlines():
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
            elif line.startswith('unsat'):
                continue
            # TODO what is this c? This should have been handled by the first if
            elif line.startswith('p cnf') or (not line.startswith('c')):
                cnf_lines.append(line)
        cnf_content = "\n".join(cnf_lines)
        log(f"Parsed CNF content: \n{cnf_content} \n cnf end", 3)
        cnf_file_name = self.smt_file.split("/")[-1].replace(".smt2", ".cnf")
        with open(cnf_file_name, 'w') as f:
            f.write(cnf_content)
        log(f"created CNF file: {cnf_file_name}")
        log(f"CNF literal to atoms Mapping: {mapping}", 2)
        return mapping, cnf_file_name
