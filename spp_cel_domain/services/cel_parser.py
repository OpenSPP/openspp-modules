from dataclasses import dataclass
from typing import Any


# AST Nodes
@dataclass
class Literal:
    value: Any


@dataclass
class Ident:
    name: str


@dataclass
class Attr:
    obj: Any
    name: str


@dataclass
class Call:
    func: Any  # Ident or Attr
    args: list[Any]


@dataclass
class And:
    left: Any
    right: Any


@dataclass
class Or:
    left: Any
    right: Any


@dataclass
class Not:
    expr: Any


@dataclass
class Compare:
    op: str
    left: Any
    right: Any


@dataclass
class InOp:
    left: Any
    items: list[Any]


class Token:
    def __init__(self, kind: str, value: Any, pos: int):
        self.kind = kind
        self.value = value
        self.pos = pos


KEYWORDS = {
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "true": True,
    "false": False,
}


class Lexer:
    def __init__(self, text: str):
        self.t = text
        self.i = 0

    def peek(self) -> str:
        return self.t[self.i : self.i + 1]

    def _ws(self):
        while self.peek() and self.peek().isspace():
            self.i += 1

    def number(self) -> Token:
        start = self.i
        while self.peek() and (self.peek().isdigit() or self.peek() == "."):
            self.i += 1
        return Token(
            "NUMBER",
            float(self.t[start : self.i]) if "." in self.t[start : self.i] else int(self.t[start : self.i]),
            start,
        )

    def ident(self) -> Token:
        start = self.i
        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            self.i += 1
        val = self.t[start : self.i]
        if val in KEYWORDS:
            kw = KEYWORDS[val]
            if kw in (True, False):
                return Token("BOOL", kw, start)
            return Token(kw, val, start)
        return Token("IDENT", val, start)

    def string(self) -> Token:
        quote = self.peek()
        self.i += 1
        start = self.i
        parts: list[str] = []
        while self.peek():
            ch = self.peek()
            if ch == quote:
                break
            if ch == "\\":
                parts.append(self.t[start : self.i])
                self.i += 1  # consume backslash
                esc = self.peek()
                if not esc:
                    raise SyntaxError(f"Unterminated escape at position {self.i}")
                parts.append(esc)
                self.i += 1
                start = self.i
            else:
                self.i += 1
        if not self.peek():
            raise SyntaxError(f"Unterminated string starting at position {start - 1}")
        parts.append(self.t[start : self.i])
        s = "".join(parts)
        self.i += 1  # closing quote
        return Token("STRING", s, start - 1)

    def tokens(self) -> list[Token]:
        out: list[Token] = []
        self._ws()
        while self.peek():
            ch = self.peek()
            if ch.isdigit():
                out.append(self.number())
            elif ch.isalpha() or ch == "_":
                out.append(self.ident())
            elif ch in ('"', "'"):
                out.append(self.string())
            elif ch == "(" or ch == ")" or ch == "," or ch == "." or ch == "[" or ch == "]":
                out.append(Token(ch, ch, self.i))
                self.i += 1
            elif ch == "=" and self.t[self.i : self.i + 2] == "==":
                out.append(Token("EQ", "==", self.i))
                self.i += 2
            elif ch == "!" and self.t[self.i : self.i + 2] == "!=":
                out.append(Token("NE", "!=", self.i))
                self.i += 2
            elif ch == ">" and self.t[self.i : self.i + 2] == ">=":
                out.append(Token("GE", ">=", self.i))
                self.i += 2
            elif ch == "<" and self.t[self.i : self.i + 2] == "<=":
                out.append(Token("LE", "<=", self.i))
                self.i += 2
            elif ch == ">":
                out.append(Token("GT", ">", self.i))
                self.i += 1
            elif ch == "<":
                out.append(Token("LT", "<", self.i))
                self.i += 1
            else:
                raise SyntaxError(f"Unknown character '{ch}' at position {self.i}")
            self._ws()
        out.append(Token("EOF", None, self.i))
        return out


class Parser:
    def __init__(self, text: str):
        self.tokens = Lexer(text).tokens()
        self.i = 0

    def cur(self) -> Token:
        return self.tokens[self.i]

    def eat(self, kind: str) -> Token:
        if self.cur().kind != kind:
            raise SyntaxError(f"Expected {kind} at {self.cur().pos}")
        t = self.cur()
        self.i += 1
        return t

    def parse(self) -> Any:
        return self.expr(0)

    PRECEDENCE = {
        "OR": 1,
        "AND": 2,
        "IN": 3,
        "EQ": 4,
        "NE": 4,
        "GT": 5,
        "GE": 5,
        "LT": 5,
        "LE": 5,
    }

    def lbp(self, tok: Token) -> int:
        if tok.kind in ("OR", "AND", "EQ", "NE", "GT", "GE", "LT", "LE"):
            return self.PRECEDENCE[tok.kind]
        if tok.kind == "IDENT" and tok.value == "in":
            return self.PRECEDENCE["IN"]
        return 0

    def nud(self, tok: Token) -> Any:
        if tok.kind in ("NUMBER", "STRING", "BOOL"):
            return Literal(tok.value)
        if tok.kind == "IDENT":
            left: Any = Ident(tok.value)
            while self.cur().kind == ".":
                self.eat(".")
                name = self.eat("IDENT").value
                left = Attr(left, name)
            if self.cur().kind == "(":
                self.eat("(")
                args: list[Any] = []
                if self.cur().kind != ")":
                    while True:
                        args.append(self.expr(0))
                        if self.cur().kind == ",":
                            self.eat(",")
                            continue
                        break
                self.eat(")")
                return Call(left, args)
            return left
        if tok.kind == "(":
            expr = self.expr(0)
            self.eat(")")
            return expr
        if tok.kind == "[":
            items: list[Any] = []
            if self.cur().kind != "]":
                while True:
                    items.append(self.expr(0))
                    if self.cur().kind == ",":
                        self.eat(",")
                        continue
                    break
            self.eat("]")
            return Literal([i.value if isinstance(i, Literal) else i for i in items])
        if tok.kind == "NOT":
            return Not(self.expr(6))
        raise SyntaxError(f"Unexpected token {tok.kind} at {tok.pos}")

    def led(self, left: Any, tok: Token) -> Any:
        if tok.kind == "AND":
            return And(left, self.expr(self.PRECEDENCE["AND"]))
        if tok.kind == "OR":
            return Or(left, self.expr(self.PRECEDENCE["OR"]))
        if tok.kind in ("EQ", "NE", "GT", "GE", "LT", "LE"):
            return Compare(tok.kind, left, self.expr(self.PRECEDENCE[tok.kind]))
        if tok.kind == "IDENT" and tok.value == "in":
            # left IN [list]
            right = self.expr(self.PRECEDENCE["IN"])
            if isinstance(right, Literal) and isinstance(right.value, list):
                return InOp(left, right.value)
            raise SyntaxError("Right operand of 'in' must be a list literal")
        raise SyntaxError(f"Unexpected infix token {tok.kind}")

    def expr(self, rbp: int) -> Any:
        t = self.cur()
        self.i += 1
        left = self.nud(t)
        while self.lbp(self.cur()) > rbp:
            t = self.cur()
            self.i += 1
            left = self.led(left, t)
        return left


def parse(text: str) -> Any:
    return Parser(text).parse()
