from lark import Lark, Transformer
from lark.tree import Tree
from .utils import log
import pandas as pd

# TODO what happens for free literals

grammar = """
    ?start: inequality

    inequality: "(" ">=" sum number ")"

    sum: "(" "+" product+ ")"

    product: "(" "*" number VAR ")" | VAR

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
            "right": items[0][1]
        }

    def sum(self, *items):
        return {
            "type": "sum",
            "terms": list(items)
        }

    def product(self, *items):
        log(f"product: {items}", 4)
        # Check if it's a standalone variable
        if len(items[0]) == 1 and isinstance(items[0][0], str):
            coefficient = 1
            variable = items[0][0]
            self.variables.add(variable)
        else:  # Otherwise, it's a product term like (* number VAR)
            coefficient = items[0][0]
            variable = items[0][1]
            self.variables.add(variable)
        return {
            "type": "product",
            "coefficient": coefficient,
            "variable": variable
        }

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


class ExpressionTransformer(Transformer, list):
    def __init__(self, variables):
        self.variables = variables
        self.constraints = pd.DataFrame(0,
                                        columns=variables, index=range(1))

    def inequality(self, *items):
        log(f"inequalityx: {items}", 4)
        # self.constraints = pd.DataFrame(0, columns=self.variables, index=range(1))
        self.constraints.loc[0, "const"] = - items[0][1].children[0]
        return self.constraints
        # return {
        #     "type": "inequality",
        #     "operator": ">=",
        #     "left": items[0][0],
        #     # Convert the number to int here
        #     "right": items[0][1]
        # }

    def sum(self, *items):
        return {
            "type": "sum",
            "terms": list(items)
        }

    def product(self, *items):
        log(f"product: {items}", 4)
        # Check if it's a standalone variable
        if len(items[0]) == 1 and isinstance(items[0][0], str):
            coefficient = 1
            variable = items[0]
            self.constraints.loc[0, variable] = coefficient
        else:  # Otherwise, it's a product term like (* number VAR)
            coefficient = items[0][0]
            variable = items[0][1]
            self.constraints.loc[0, variable] = coefficient.children[0]

        return {
            "type": "product",
            "coefficient": coefficient,
            "variable": variable
        }

    def signed_number(self, items):
        token = items[0]
        value = int(token.value)
        log(f"signed_number: {-1 * value}", 4)
        return -1 * value

    def unsigned_number(self, items):
        token = items[0]
        value = int(token.value)
        log(f"unsigned_number: {value}", 4)
        return value

    def VAR(self, item):
        return str(item)


class LiteralMapping:
    def __init__(self):
        self.mapping = {}
        self.variables = set()
        self.num_inequalities = 0
        # create empty dataframe for constraints
        self.constraint_matrix = pd.DataFrame()
        self.variable_creator_parser = Lark(grammar, parser='lalr',
                                            transformer=VariableCreator())
        self.parser = None  # will be initialized after we know all variables
        self.num_constraints_added = 0

    def get_variables(self, tree):
        variables = set()

        def traverse(node):
            if isinstance(node, dict):
                if 'variable' in node:
                    variables.add(node['variable'])
                if 'left' in node:
                    traverse(node['left'])
                if 'right' in node:
                    traverse(node['right'])
                if 'terms' in node:
                    for term in node['terms']:
                        if isinstance(term, list):
                            for subterm in term:
                                traverse(subterm)
                        else:
                            traverse(term)
            elif isinstance(node, Tree):
                for child in node.children:
                    traverse(child)

        traverse(tree)
        return variables

    def convert_to_latte(self, parsed_tree):
        if parsed_tree["type"] == "inequality":
            left = parsed_tree["left"]
            right = parsed_tree["right"].children[0]
            log(f"left: {left}, right: {right}", 4)
            lhs = left["terms"][0]
            coefficients = []
            for term in lhs:
                # get datatype of coefficient
                # Check if coefficient is a list
                if not isinstance(term["coefficient"], int):
                    coefficient = term["coefficient"].children[0]
                else:
                    coefficient = term["coefficient"]
                coefficients.append(coefficient)
            # coefficients = [term["coefficient"].children[0] for term in lhs]
            negated_coefficients = [-term for term in coefficients]

            coefficients.insert(0, -right)
            negated_coefficients.insert(0, right - 1)

            ineq = " ".join(map(str, [c for c in coefficients]))
            neg_ineq = " ".join(map(str, [c for c in negated_coefficients]))
            return ineq, neg_ineq

    def add_variable_in_constraint_matrix(self, ineq):
        parsed_tree = self.variable_creator_parser.parse(ineq)
        self.variables = self.variables.union(self.get_variables(parsed_tree))
        self.num_inequalities += 1

    def finalize_variable_matrix(self):
        self.variables = ["const"] + list(self.variables)
        self.constraint_matrix = pd.DataFrame(
            columns=self.variables, index=range(0))
        log(
            f"created constraint matrix of size {self.constraint_matrix.shape}", 2)
        one_constraint = pd.DataFrame(
            columns=self.variables, index=range(1))

    def negate_constraint(self, constraint_line):
        # negate the constraint line
        df = constraint_line.copy()
        df['const'] = -df['const'] - 1
        df.loc[:, df.columns != 'const'] = -df.loc[:, df.columns != 'const']
        return df

    def copy_constraint_matrix(self, constraint_line, literal):
        # copy constraint line to constraint matrix
        constraint_line.index = [literal]
        self.constraint_matrix.loc[literal] = constraint_line.iloc[0]

    def add_mapping(self, literal, inequality):
        if literal in [0, 1]:
            return  # Ignore literals 0 and 1
        log(f"now mapping literal: {literal}, inequality: {inequality}", 3)
        self.parser = Lark(grammar, parser='lalr',
                           transformer=ExpressionTransformer(self.variables))
        inequality_line = self.parser.parse(inequality)
        neg_inequality_line = self.negate_constraint(inequality_line)
        # ineq, neg_ineq = self.convert_to_latte(parsed_tree)
        self.copy_constraint_matrix(inequality_line, literal)
        self.copy_constraint_matrix(neg_inequality_line, -literal)
        # log(f"latte format: {ineq}\n \t neg: {neg_ineq}", 3)

        log(f"mapping now: {self.constraint_matrix}", 4)

    def get_inequalities(self, literals):
        inequalities = []
        for lit in literals:
            if lit in [0, 1]:
                continue  # Ignore literals 0 and 1
            inequality = self.constraint_matrix.loc(lit)
            if inequality:
                inequalities.append(inequality)
        log(f"inequalities: {inequalities}", 3)
        return inequalities

    def __str__(self):
        return str(self.constraint_matrix)
