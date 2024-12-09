class GlobalStorage:
    cnf_file = ""
    dnf_file = ""
    filename = ""
    matrix_file = ""
    verbosity = 0
    # tool_list = ['cvc5', 'hall', 'latte']
    tool_list = ['cvc5']
    dnfizer = "hall"
    arg = None

    # defining the class constructor
    def initialize(self, _arg):
        self.arg = _arg
        self.verbosity = _arg.verbosity
        self.filename = _arg.smt_file
        if not _arg.hall:
            print("setting cnftranslate as dnfizer")
            self.dnfizer = "cnftranslate"


gbl = GlobalStorage()
