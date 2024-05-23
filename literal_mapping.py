class LiteralMapping:
    def __init__(self):
        self.mapping = {}

    def add_mapping(self, literal, inequality):
        self.mapping[literal] = inequality

    def get_inequalities(self, literals):
        inequalities = []
        for lit in literals:
            if lit < 0:
                inequality = self.mapping.get(-lit, None)
                if inequality:
                    inequalities.append(f"(not {inequality})")
            else:
                inequality = self.mapping.get(lit, None)
                if inequality:
                    inequalities.append(inequality)
        return inequalities
