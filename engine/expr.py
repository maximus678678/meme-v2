"""Tiny safe expression evaluator for scene conditions.

Grammar:
    expr       := or_expr
    or_expr    := and_expr ('or' and_expr)*
    and_expr   := not_expr ('and' not_expr)*
    not_expr   := 'not' not_expr | comparison
    comparison := atom (('>='|'<='|'=='|'!='|'>'|'<') atom)?
    atom       := NUMBER | STRING | IDENT | '(' expr ')'

Identifiers resolve against a vars dict; missing names evaluate to 0/False.
"""

import re

_TOKEN_RE = re.compile(
    r"\s*(?:(>=|<=|==|!=|>|<|\(|\))|\"([^\"]*)\"|'([^']*)'|(-?\d+)|([A-Za-z_]\w*))"
)


class ExprError(ValueError):
    pass


def tokenize(src):
    tokens = []
    pos = 0
    while pos < len(src):
        m = _TOKEN_RE.match(src, pos)
        if not m:
            if src[pos:].strip():
                raise ExprError("bad token in %r at %d" % (src, pos))
            break
        op, dq, sq, num, ident = m.groups()
        if op:
            tokens.append(("op", op))
        elif dq is not None or sq is not None:
            tokens.append(("str", dq if dq is not None else sq))
        elif num is not None:
            tokens.append(("num", int(num)))
        elif ident is not None:
            low = ident.lower()
            if low in ("and", "or", "not"):
                tokens.append(("kw", low))
            elif low == "true":
                tokens.append(("num", True))
            elif low == "false":
                tokens.append(("num", False))
            else:
                tokens.append(("ident", ident))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, tokens, src):
        self.tokens = tokens
        self.src = src
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        node = self.or_expr()
        if self.i != len(self.tokens):
            raise ExprError("trailing tokens in %r" % self.src)
        return node

    def or_expr(self):
        node = self.and_expr()
        while self.peek() == ("kw", "or"):
            self.take()
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.peek() == ("kw", "and"):
            self.take()
            node = ("and", node, self.not_expr())
        return node

    def not_expr(self):
        if self.peek() == ("kw", "not"):
            self.take()
            return ("not", self.not_expr())
        return self.comparison()

    def comparison(self):
        left = self.atom()
        kind, val = self.peek()
        if kind == "op" and val in (">=", "<=", "==", "!=", ">", "<"):
            self.take()
            return ("cmp", val, left, self.atom())
        return left

    def atom(self):
        kind, val = self.take()
        if kind == "num":
            return ("lit", val)
        if kind == "str":
            return ("lit", val)
        if kind == "ident":
            return ("var", val)
        if (kind, val) == ("op", "("):
            node = self.or_expr()
            if self.take() != ("op", ")"):
                raise ExprError("missing ) in %r" % self.src)
            return node
        raise ExprError("unexpected token %r in %r" % (val, self.src))


def parse(src):
    """Parse an expression; raises ExprError on bad syntax."""
    return _Parser(tokenize(src), src).parse()


def _as_number(v):
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        return v
    if v is None:
        return 0
    return v  # string


def _eval(node, vars):
    op = node[0]
    if op == "lit":
        return node[1]
    if op == "var":
        return vars.get(node[1], 0)
    if op == "not":
        return not _eval(node[1], vars)
    if op == "and":
        return bool(_eval(node[1], vars)) and bool(_eval(node[2], vars))
    if op == "or":
        return bool(_eval(node[1], vars)) or bool(_eval(node[2], vars))
    if op == "cmp":
        _, cmp_op, l, r = node
        lv, rv = _eval(l, vars), _eval(r, vars)
        if isinstance(lv, str) or isinstance(rv, str):
            lv, rv = str(lv), str(rv)
            if cmp_op == "==":
                return lv == rv
            if cmp_op == "!=":
                return lv != rv
            raise ExprError("ordered comparison on strings: %r" % cmp_op)
        lv, rv = _as_number(lv), _as_number(rv)
        return {
            ">=": lv >= rv, "<=": lv <= rv, "==": lv == rv,
            "!=": lv != rv, ">": lv > rv, "<": lv < rv,
        }[cmp_op]
    raise ExprError("bad node %r" % (node,))


def evaluate(src, vars):
    """Evaluate expression string against a vars dict. Missing vars are 0."""
    return bool(_eval(parse(src), vars))
