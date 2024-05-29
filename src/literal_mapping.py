from lark import Lark, Transformer, v_args

grammar = """
    ?start: inequality

    inequality: "(" comparison expr expr ")"
    comparison: GEQ

    ?expr: term
         | "(" "+" expr+ ")"

    ?term: "(" "*" SIGNED_NUMBER VAR ")"
         | SIGNED_NUMBER
         | VAR

    VAR: /[a-zA-Z]+/
    GEQ: ">="

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""


@v_args(inline=True)
class ExpressionTransformer(Transformer):
    def comparison(self, token):
        print(f"comparison: {token}")
        return token

    def inequality(self, comp, expr1, expr2):
        print(f"comp: {comp} expr1: {expr1} expr2: {expr2}")
        if comp == ">=":
            return ['<=', self.negate(expr1), self.negate(expr2)]
        raise ValueError(f"Unsupported inequality type: {comp}")

    def negate(self, value):
        if isinstance(value, (int, float)):
            return -value
        elif isinstance(value, list) and value[0] == '*':
            return ['*', self.negate(value[1]), value[2]]
        elif isinstance(value, list) and value[0] == '+':
            return ['+', *[self.negate(v) for v in value[1:]]]
        raise ValueError(f"Unsupported term type: {value}")

    def increment(self, value):
        if isinstance(value, (int, float)):
            return value + 1
        raise ValueError(f"Unsupported term type: {value}")

    def term(self, items):
        print(f"term items: {items}")
        if len(items) == 1:
            return items[0]
        else:
            return ('*', items[0], items[1])

    def SIGNED_NUMBER(self, token):
        return float(token)

    def VAR(self, token):
        return str(token)

    def expr(self, *terms):
        if len(terms) == 1:
            return terms[0]
        return ['+', *terms]


class LiteralMapping:
    def __init__(self):
        self.mapping = {}
        self.parser = Lark(grammar, start='start', parser='lalr',
                           transformer=ExpressionTransformer())

    def add_mapping(self, literal, inequality):
        if literal in [0, 1]:
            return  # Ignore literals 0 and 1
        print(f"now mapping literal: {literal}, inequality: {inequality}")
        normalized_inequality = self.normalize_inequality(inequality)
        self.mapping[literal] = normalized_inequality

        negated_literal = -literal
        negated_inequality = self.negate_inequality(normalized_inequality)
        self.mapping[negated_literal] = negated_inequality
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

    def negate_inequality(self, inequality):
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
