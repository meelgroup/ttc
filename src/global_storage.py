import time

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
    usepact = False
    useoptcnt = False
    volesti_algo = "coolinggauss"
    volesti_algo = "coolingball"
    disjoint = False
    # volesti_algo = "--seqball"
    volesti_walk_length = 5
    starttime = 0
    tempfiles = []

    time_volumecomp = 0
    time_decompose = 0
    time_cvc5 = 0
    time_pepin = 0
    seed = 123
    dontdelete = False

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
        if _arg.nohall:
            self.dnfizer = "cnftranslate"
            self.tool_list.append('cnftranslate')
        else:
            self.tool_list.append('hall_tool')
        self.decompose_lim = _arg.decomposelim
        self.cube_and_exit = _arg.cubes
        self.usebv = _arg.intbv
        self.usepact = _arg.pact
        self.useoptcnt = _arg.optcnt
        if self.verbosity > 0:
            print(f"c [ttc] logic set to: {self.logic}")
        if self.logic == "lra":
            self.disjoint = _arg.disjoint
        self.starttime = time.time()
        self.seed = _arg.seed
        self.dontdelete = _arg.dontdelete

    def time(self):
        return f"[{(time.time() - self.starttime):.3f} s]"


gbl = GlobalStorage()
