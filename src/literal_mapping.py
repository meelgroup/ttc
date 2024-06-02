from lark import Lark, Transformer, v_args
from .utils import log
# TODO sum can be of multiple products
# TODO what happens for free literals
# TODO check well for correctness of the converted constraints

grammar = """
    ?start: inequality

    inequality: "(" ">=" sum number ")"

    sum: "(" "+" product product ")"

    product: "(" "*" signed_number VAR ")"

    VAR: /[a-zA-Z]+/

    number: SIGNED_NUMBER
    signed_number: ["(" "-"] SIGNED_NUMBER [")"]

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""


class ExpressionTransformer(Transformer):

    def inequality(self, *items):
        log(f"inequalityx: {items}", 4)
        return {
            "type": "inequality",
            "operator": ">=",
            "left": items[0][0],
            # Convert the number to int here
            "right": int(items[0][1])
        }

    def sum(self, *items):
        return {
            "type": "sum",
            "terms": list(items)
        }

    def product(self, *items):
        log(f"product: {items}", 4)
        return {
            "type": "product",
            # Convert the coefficient to int
            "coefficient": int(items[0][0]),
            "variable": items[0][1]
        }

    def number(self, item):
        log(f"number: {item}", 4)
        token = item[0]
        value = int(token.value)
        sign = -1 if value < 0 else 1
        log(f"signed_number: {sign * value}", 4)
        return sign * value

    def signed_number(self, items):
        # items is a list containing one token, e.g., [Token('SIGNED_NUMBER', '-2')]
        token = items[0]
        value = int(token.value)
        sign = -1 if value < 0 else 1
        log(f"signed_number: {sign * value}", 4)
        return sign * value

    def VAR(self, item):
        return str(item)


class LiteralMapping:
    def __init__(self):
        self.mapping = {}
        self.parser = Lark(grammar, parser='lalr',
                           transformer=ExpressionTransformer())

    def convert_to_latte(self, parsed_tree):
        if parsed_tree["type"] == "inequality":
            left = parsed_tree["left"]
            right = parsed_tree["right"]
            log(f"left: {left}, right: {right}", 4)
            lhs = left["terms"][0]
            coefficients = [term["coefficient"] for term in lhs]
            negated_coefficients = [-c for c in coefficients]
            coefficients.append(-right)  # Append the negated constant term
            negated_coefficients.append(right - 1)
            ineq = " ".join(map(str, [-c for c in coefficients]))
            neg_ineq = " ".join(map(str, [-c for c in negated_coefficients]))
            return ineq, neg_ineq

    def add_mapping(self, literal, inequality):
        if literal in [0, 1]:
            return  # Ignore literals 0 and 1
        log(f"now mapping literal: {literal}, inequality: {inequality}", 3)
        parsed_tree = self.parser.parse(inequality)
        ineq, neg_ineq = self.convert_to_latte(parsed_tree)
        log(f"latte format: {ineq} {neg_ineq}", 3)

        self.mapping[literal] = ineq
        self.mapping[-literal] = neg_ineq

        log(f"mapping now: {self.mapping}", 4)

    def get_inequalities(self, literals):
        inequalities = []
        for lit in literals:
            if lit in [0, 1]:
                continue  # Ignore literals 0 and 1
            inequality = self.mapping.get(lit, None)
            if inequality:
                inequalities.append(inequality)
        log(f"inequalities: {inequalities}", 3)
        return inequalities

    def __str__(self):
        return str(self.mapping)
