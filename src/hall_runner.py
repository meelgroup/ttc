import subprocess
import os
from .utils import log
from .global_storage import gbl


def run_hall_on_cnf_file(cnf_file):
    log("Running hall...", 2)
    bin_dir = os.path.join(os.getcwd(), 'bin')
    cnftranslate_path = os.path.join(bin_dir, 'cnftranslate')

    dnf_file = cnf_file[:-4] + ".dnf"

    command = [cnftranslate_path, cnf_file, dnf_file]

    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if gbl.verbosity > 3:
            print("Output from cnftranslate:")
            print(result.stdout.decode())
            print("Error from cnftranslate:")
            print(result.stderr.decode())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error occurred while running cnftranslate: {e.stderr.decode()}")
    # if gbl.verbosity >= 2 then print contents of the file dnf_file here
    if gbl.verbosity > 2:
        print(f"Contents of {dnf_file}:")
        with open(dnf_file, 'r') as f:
            print(f.read())

    return dnf_file


def parse_dnf_file(dnf_file):
    log("Parsing DNF content", 1)
    cubes = []
    for line in dnf_file.splitlines():
        if line.strip() and not line.startswith('p'):
            cubes.append([int(lit)
                         for lit in line.strip().split() if lit != '0'])
    log(f"Parsed DNF content: {cubes}", 2)
    return cubes
