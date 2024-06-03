from lark import Lark, Transformer, v_args
from .utils import log
import pandas as pd

# TODO sum can be of multiple products
# TODO what happens for free literals
# TODO check well for correctness of the converted constraints

grammar = """
    ?start: inequality

    inequality: "(" ">=" sum number ")"

    sum: "(" "+" product product ")"

    product: "(" "*" number VAR ")"

    VAR: /[a-zA-Z]+/

    number: signed_number | unsigned_number
    signed_number: "(" "-" UNSIGNED_NUMBER ")"
    unsigned_number: UNSIGNED_NUMBER

    %import common.SIGNED_NUMBER
    %import common.INT -> UNSIGNED_NUMBER
    %import common.WS
    %ignore WS
"""


class VariableCreator(Transformer):
    def __init__(self):
        self.variables = set()

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
        # append to set variables the item[0][1]
        self.variables.add(items[0][1])

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
        log(f"signed_number: {-1 * value}", 4)
        return -1 * value

    def VAR(self, item):
        return str(item)


class ExpressionTransformer(Transformer):

    def inequality(self, *items):
        log(f"inequalityx: {items}", 4)
        return {
            "type": "inequality",
            "operator": ">=",
            "left": items[0][0],
            # Convert the number to int here
            "right": items[0][1]
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
            "coefficient": items[0][0],
            "variable": items[0][1]
        }

    # def number(self, item):
    #     print(f"number: {item}")
    #     token = item[0]
    #     value = int(token.value)
    #     sign = -1 if value < 0 else 1
    #     log(f"signed_number: {sign * value}", 4)
    #     return sign * value

    def signed_number(self, items):
        # items is a list containing one token, e.g., [Token('SIGNED_NUMBER', '-2')]
        token = items[0]
        value = int(token.value)
        log(f"signed_number: {-1 * value}", 4)
        return -1 * value

    def unsigned_number(self, items):
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
        # create empty dataframe for constraints
        self.constraint_matrix = pd.DataFrame()
        self.variable_creator_parser = Lark(grammar, parser='lalr',
                                            transformer=VariableCreator())
        self.parser = Lark(grammar, parser='lalr',
                           transformer=ExpressionTransformer())

    def convert_to_latte(self, parsed_tree):
        if parsed_tree["type"] == "inequality":
            left = parsed_tree["left"]
            right = parsed_tree["right"].children[0]
            log(f"left: {left}, right: {right}", 4)
            lhs = left["terms"][0]

            coefficients = [term["coefficient"].children[0] for term in lhs]
            coefficients.insert(0, -right)  # Append the negated constant term

            negated_coefficients = [-term["coefficient"].children[0]
                                    for term in lhs]
            negated_coefficients.insert(0, right - 1)
            ineq = " ".join(map(str, [c for c in coefficients]))
            neg_ineq = " ".join(map(str, [c for c in negated_coefficients]))
            return ineq, neg_ineq

    def create_constraint_matrix(self, inequalities):
        self.variables = set()

        for ineq in inequalities:
            variable_set = self.variable_creator_parser.parse(ineq)
            self.variables = self.variables.union(variable_set.variables)

        # create empty dataframe with columns as variables, and number of inequalities many rows
        self.constraint_matrix = pd.DataFrame(
            columns=self.variables, index=range(len(inequalities)))

    def add_mapping(self, literal, inequality):
        if literal in [0, 1]:
            return  # Ignore literals 0 and 1
        log(f"now mapping literal: {literal}, inequality: {inequality}", 3)
        parsed_tree = self.parser.parse(inequality)
        ineq, neg_ineq = self.convert_to_latte(parsed_tree)
        log(f"latte format: {ineq}\n \t neg: {neg_ineq}", 3)

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
