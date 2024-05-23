from lark import Lark, Transformer
from src.utils import log

class SMTTransformer(Transformer):
    def __init__(self):
        self.variables = []
        self.constraints = []

    def start(self, items):
        for item in items:
            self.constraints.append(item)
        return self.constraints

    def expr(self, items):
        op, left, right = items
        left_coeffs = self.get_coefficients(left)
        right_coeffs = self.get_coefficients(right)

        if op in ["<=", ">=", "="]:
            for var in right_coeffs:
                right_coeffs[var] = -right_coeffs[var]
            combined_coeffs = {var: left_coeffs.get(var, 0) + right_coeffs.get(var, 0) for var in set(left_coeffs) | set(right_coeffs)}

            if op == "<=":
                combined_coeffs['const'] = combined_coeffs.get('const', 0) * -1
                self.constraints.append(combined_coeffs)
            elif op == ">=":
                self.constraints.append(combined_coeffs)
            elif op == "=":
                self.constraints.append(combined_coeffs)
                combined_coeffs['const'] = combined_coeffs.get('const', 0) * -1
                self.constraints.append(combined_coeffs)

        return (op, left, right)

    def get_coefficients(self, term):
        if isinstance(term, int):
            return {'const': term}
        elif isinstance(term, str):
            return {term: 1}
        else:
            op, left, right = term
            left_coeffs = self.get_coefficients(left)
            right_coeffs = self.get_coefficients(right)
            if op == "+":
                return {var: left_coeffs.get(var, 0) + right_coeffs.get(var, 0) for var in set(left_coeffs) | set(right_coeffs)}
            elif op == "-":
                return {var: left_coeffs.get(var, 0) - right_coeffs.get(var, 0) for var in set(left_coeffs) | set(right_coeffs)}
            elif op == "*":
                if isinstance(left, int):
                    return {var: left * coef for var, coef in right_coeffs.items()}
                elif isinstance(right, int):
                    return {var: right * coef for var, coef in left_coeffs.items()}
        return {}

    def var(self, token):
        return str(token)

    def INT(self, token):
        return int(token)

class SMTParser:
    def __init__(self):
        self.grammar = """
            ?start: expr+
            ?expr: "(" op term term ")"
            ?term: var
                 | INT
                 | "(" op term term ")"
            op: "+" | "-" | "*" | "<=" | ">=" | "="
            var: /[a-zA-Z_][a-zA-Z_0-9]*/
            %import common.INT
            %import common.WS
            %ignore WS
        """
        self.parser = Lark(self.grammar, parser='lalr', transformer=SMTTransformer())
        self.transformer = self.parser.options.transformer

    def parse(self, input_text):
        log("Parsing SMT input", 2)
        self.parser.parse(input_text)
        return self.transformer
