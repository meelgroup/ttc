import os
import subprocess
from .literal_mapping import LiteralMapping
from .utils import log
from .global_storage import gbl


class CVC5Runner:
    def __init__(self, smt_file):
        self.smt_file = smt_file
        self.cvcoutput = None
        self.mapping = LiteralMapping()

    def run_cvc5_on_smt_file(self):
        log(f"Running cvc5 on {self.smt_file}", 1)
        # RUN my version of CVC5 which outputs mapping
        bin_dir = os.path.join(os.getcwd(), 'bin')
        cvc_path = os.path.join(bin_dir, 'cvc5')

        result = subprocess.run([cvc_path, '--newt', self.smt_file],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"cvc5 error: {result.stderr}")
        log(f"cvc5 output: {result.stdout}", 4)
        self.cvcoutput = result.stdout

    def populate_variable_list_in_mapping(self):
        forbidden_atom_starts = ['not', 'let', 'and', 'or']
        log("Parsing cvc5 output to get the variable list", 1)
        pcnfread = False
        for line in self.cvcoutput.splitlines():
            if not line.startswith('c '):
                continue
            parts = line.split(':')
            if 'skipit' in parts[1]:
                continue
            if any([x in parts[1] for x in forbidden_atom_starts]):
                print(f"cvc5 --newt was not supposed to output {line}")
                exit(1)

            inequality = parts[1].strip()
            literal = int(parts[0][2:])

            log(f"adding variable: {inequality} with literal: {literal}", 5)
            self.mapping.add_variable_in_constraint_matrix(inequality)
        self.mapping.finalize_variable_matrix()

    def parse_cvc5_output(self):
        self.populate_variable_list_in_mapping()
        log("Parsing cvc5 output", 1)
        cnf_lines = []
        pcnfread = False
        # cnffilename replace the last.smth2 with .cnf
        cnf_file_name = self.smt_file.split("/")[-1]
        cnf_file_name = cnf_file_name[:cnf_file_name.rfind('.')] + '.cnf'

        for line in self.cvcoutput.splitlines():
            if not line.startswith('c'):
                continue

            parts = line.split(':')
            if 'skipit' in parts[1]:
                continue

            literal = int(parts[0][2:])
            inequality = parts[1].strip()
            self.mapping.add_mapping(literal, inequality)
        #

        log(f"created CNF file: {cnf_file_name}")
        log(f"CNF literal to atoms Mapping: \n{self.mapping}", 2)
        return self.mapping, cnf_file_name
