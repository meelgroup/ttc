class GlobalStorage:
    cnf_file = ""
    dnf_file = ""
    filename = ""
    matrix_file = ""
    verbosity = 0
    # tool_list = ['cvc5', 'hall', 'latte']
    tool_list = ['cvc5']
    arg = None

    # defining the class constructor
    def initialize(self, _arg):
        self.arg = _arg
        self.verbosity = _arg.verbosity


gbl = GlobalStorage()
