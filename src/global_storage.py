class GlobalStorage:
    cnf_file = ""
    dnf_file = ""
    filename = ""
    matrix_file = ""
    verbosity = 0
    decompose_lim = 0
    # tool_list = ['cvc5', 'hall', 'latte']
    tool_list = ['cvc5']
    dnfizer = "hall"
    cube_and_exit = False
    arg = None
    logic = ""
    usebv = False
    volesti_algo = "coolinggauss"
    volesti_algo = "coolingball"
    # volesti_algo = "--seqball"
    volesti_walk_length = 5

    def set_logic(self):
        with open(self.filename, 'r') as file:
            for line in file:
                if line.startswith("(set-logic"):
                    if "QF_LRA" in line:
                        self.logic = "lra"
                    elif "QF_LIA" in line:
                        self.logic = "lia"
                    else:
                        print(f"logic {line.strip()} is not supported yet")
                        exit(1)
                    break

    # defining the class constructor
    def initialize(self, _arg):
        self.arg = _arg
        self.verbosity = _arg.verbosity
        self.filename = _arg.smt_file
        self.set_logic()
        if not _arg.hall:
            self.dnfizer = "cnftranslate"
        self.decompose_lim = _arg.decomposelim
        self.cube_and_exit = _arg.cubes
        self.usebv = _arg.intbv
        if self.verbosity > 0:
            print(f"c [ttc] logic set to: {self.logic}")


gbl = GlobalStorage()
