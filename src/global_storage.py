
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

    # defining the class constructor
    def initialize(self, _arg):
        self.arg = _arg
        self.verbosity = _arg.verbosity
        self.filename = _arg.smt_file
        if not _arg.hall:
            self.dnfizer = "cnftranslate"
        self.decompose_lim = _arg.decomposelim
        self.cube_and_exit = _arg.cubes


gbl = GlobalStorage()
