from lark import Lark, Transformer, v_args

# TODO sum can be of multiple products
# TODO what happens for free literals

grammar = """
    ?start: inequality

    inequality: "(" ">=" sum number ")"

    sum: "(" "+" product product ")"

    product: "(" "*" SIGNED_NUMBER VAR ")"

    VAR: /[a-zA-Z]+/

    number: SIGNED_NUMBER

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""


class ExpressionTransformer(Transformer):
    def inequality(self, items):
        return {
            "type": "inequality",
            "operator": ">=",
            "left": items[0],
            "right": float(items[1])  # Convert the number to float here
        }

    def sum(self, items):
        return {
            "type": "sum",
            "terms": items
        }

    def product(self, items):
        return {
            "type": "product",
            "coefficient": float(items[0]),  # Convert the coefficient to float
            "variable": items[1]
        }

    def number(self, item):
        return - float(item[0])

    def VAR(self, item):
        return str(item[0])


class LiteralMapping:
    def __init__(self):
        self.mapping = {}
        self.parser = Lark(grammar, parser='lalr',
                           transformer=ExpressionTransformer())

    def convert_to_latte(self, parsed_tree):
        if parsed_tree["type"] == "inequality":
            left = parsed_tree["left"]
            right = parsed_tree["right"]
            coefficients = [term["coefficient"] for term in left["terms"]]
            negated_coefficients = [-c for c in coefficients]
            coefficients.append(-right)  # Append the negated constant term
            negated_coefficients.append(right - 1)
            ineq = " ".join(map(str, [-c for c in coefficients]))
            neg_ineq = " ".join(map(str, [-c for c in negated_coefficients]))
            return ineq, neg_ineq

    def add_mapping(self, literal, inequality):
        if literal in [0, 1]:
            return  # Ignore literals 0 and 1
        print(f"now mapping literal: {literal}, inequality: {inequality}")
        parsed_tree = self.parser.parse(inequality)
        ineq, neg_ineq = self.convert_to_latte(parsed_tree)
        print(f"latte format: {ineq} {neg_ineq}")

        self.mapping[literal] = ineq
        self.mapping[-literal] = neg_ineq

        print(f"mapping now: {self.mapping}")

    def get_inequalities(self, literals):
        inequalities = []
        for lit in literals:
            if lit in [0, 1]:
                continue  # Ignore literals 0 and 1
            inequality = self.mapping.get(lit, None)
            if inequality:
                inequalities.append(inequality)
        print(f"inequalities: {inequalities}")
        return inequalities

    def normalize_inequality(self, inequality):
        """
        Normalize inequalities to the form Ax <= b.
        E.g., (>= (+ (* 2 x) (* 3 y)) 11) to (<= (+ (* -2 x) (* -3 y)) -11)
        """
        tree = self.parser.parse(inequality)
        return tree.children

    def negate_inequality_in_latte(self, inequality):
        """
        Negate the inequality and keep it in the form Ax <= b.
        E.g., (<= (+ (* 2 x) (* 3 y)) 11) to (<= (+ (* -2 x) (* -3 y)) -12)
        """
        tree = self.parser.parse(inequality)
        negated_expr = self.parser.transformer.negate(tree.children[1])
        incremented_term = self.parser.transformer.increment(tree.children[2])
        return ['<=', negated_expr, incremented_term]

    def __str__(self):
        return str(self.mapping)
