import subprocess
from utils import log

def run_hall_on_cnf_content(cnf_content):
    log("Running hall...", 2)
    result = subprocess.run(["hall"], input=cnf_content, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"hall error: {result.stderr}")
    log(f"hall output: {result.stdout}", 3)
    return result.stdout

def parse_dnf_content(dnf_content):
    cubes = []
    for line in dnf_content.splitlines():
        if line.strip() and not line.startswith('p'):
            cubes.append([int(lit) for lit in line.strip().split() if lit != '0'])
    log(f"Parsed DNF content: {cubes}", 2)
    return cubes
