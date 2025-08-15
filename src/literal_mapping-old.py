from .utils import log


class LiteralMapping:
    def __init__(self):
        self.mapping = {}

    def add_mapping(self, literal, inequality):
        if literal in [0, 1]:
            return  # Ignore literals 0 and 1
        normalized_inequality = self.normalize_inequality(inequality)
        self.mapping[literal] = normalized_inequality

        negated_literal = -literal
        negated_inequality = self.negate_inequality(normalized_inequality)
        self.mapping[negated_literal] = negated_inequality

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

    def normalize_inequality(self, inequality):
        """
        Normalize inequalities to the form Ax <= b.
        E.g., (>= (+ (* 2 x) (* 3 y)) 11) to (<= (+ (* -2 x) (* -3 y)) -11)
        """
        parts = self.split_inequality(inequality)
        if parts[0] == '>=':
            normalized = f"(<= {parts[1]} {self.negate_term(parts[2])})"
        elif parts[0] == '<=':
            normalized = inequality
        elif parts[0] == '=':
            normalized = f"(<= {parts[1]} {parts[2]})"
        else:
            raise ValueError(f"Unsupported inequality type: {parts[0]}")
        return normalized

    def negate_term(self, term):
        """
        Negate a term.
        E.g., 11 to -11 or (* 2 x) to (* -2 x)
        """
        term = term.strip()
        if term.isdigit() or (term.startswith('-') and term[1:].isdigit()):
            return f"-{term}" if not term.startswith('-') else term[1:]
        elif term.startswith('('):
            parts = self.split_expression(term)
            if parts[0] == '*':
                if len(parts) > 1 and (parts[1].isdigit() or (parts[1].startswith('-') and parts[1][1:].isdigit())):
                    parts[1] = f"-{parts[1]}" if not parts[1].startswith(
                        '-') else parts[1][1:]
                    return f"({' '.join(parts)})"
                else:
                    return f"({' '.join([parts[0]] + [self.negate_term(part) for part in parts[1:]])})"
        raise ValueError(f"Unsupported term type: {term}")

    def split_expression(self, expression):
        """
        Split an expression into its parts, correctly handling nested structures.
        """
        parts = []
        balance = 0
        current_part = []
        for char in expression.strip("()"):
            if char == ' ' and balance == 0:
                parts.append(''.join(current_part))
                current_part = []
            else:
                if char == '(':
                    balance += 1
                elif char == ')':
                    balance -= 1
                current_part.append(char)
        parts.append(''.join(current_part))
        return parts

    def negate_expression(self, expression):
        """
        Negate an expression.
        E.g., (+ (* 2 x) (* 3 y)) to (+ (* -2 x) (* -3 y))
        """
        parts = self.split_expression(expression)
        if parts[0] == '+':
            negated_parts = [parts[0]] + \
                [self.negate_term(term) for term in parts[1:]]
            return f"({' '.join(negated_parts)})"
        else:
            raise ValueError(f"Unsupported expression type: {parts[0]}")

    def negate_inequality(self, inequality):
        """
        Negate the inequality and keep it in the form Ax <= b.
        E.g., (<= (+ (* 2 x) (* 3 y)) 11) to (<= (+ (* -2 x) (* -3 y)) -12)
        """
        parts = self.split_inequality(inequality)
        if parts[0] == '<=':
            print(parts)
            negated_expression = self.negate_expression(parts[1])
            negated_term = self.increment_term(parts[2])
            negated = f"(<= {negated_expression} {negated_term})"
            print(negated)
        else:
            raise ValueError(f"Unsupported inequality type: {parts[0]}")
        return negated

    def split_inequality(self, inequality):
        """
        Split an inequality into its parts.
        E.g., "(>= (+ (* 2 x) (* 3 y)) 11)" becomes ['>=', '(+ (* 2 x) (* 3 y))', '11']
        """
        parts = []
        balance = 0
        current_part = []
        for char in inequality.strip("()"):
            if char == ' ' and balance == 0:
                parts.append(''.join(current_part))
                current_part = []
            else:
                if char == '(':
                    balance += 1
                elif char == ')':
                    balance -= 1
                current_part.append(char)
        parts.append(''.join(current_part))
        return parts

    def negate_term(self, term):
        """
        Negate a term.
        E.g., 11 to -11 or (* 2 x) to (* -2 x)
        """
        if term.isdigit() or (term.startswith('-') and term[1:].isdigit()):
            return f"-{term}" if not term.startswith('-') else term[1:]
        elif term.startswith('('):
            parts = term.strip("()").split()
            if parts[0] == '*':
                if parts[1].isdigit() or (parts[1].startswith('-') and parts[1][1:].isdigit()):
                    parts[1] = f"-{parts[1]}" if not parts[1].startswith(
                        '-') else parts[1][1:]
                    return f"({' '.join(parts)})"
        else:
            raise ValueError(f"Unsupported term type: {term}")

    def increment_term(self, term):
        """
        Increment a term by 1.
        E.g., 11 to 12
        """
        if term.isdigit() or (term.startswith('-') and term[1:].isdigit()):
            return str(int(term) + 1)
        else:
            raise ValueError(f"Unsupported term type: {term}")

    def __str__(self):
        return str(self.mapping)
