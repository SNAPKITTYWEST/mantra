# parser/parser.py
from __future__ import annotations
from lexer.lexer import tokenize, Token
from mantra_ast.nodes import *
from typing import List, Iterator

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i] if self.i < len(self.tokens) else Token('EOF', '', 0, 0)

    def peek2(self) -> Token:
        return self.tokens[self.i+1] if self.i+1 < len(self.tokens) else Token('EOF', '', 0, 0)

    def advance(self) -> Token:
        t = self.peek()
        self.i += 1
        return t

    def expect(self, typ: str) -> Token:
        t = self.advance()
        if t.type != typ:
            raise ParseError(f"Expected {typ} at {t.line}:{t.col}, got {t.type!r} ({t.value!r})")
        return t

    def match(self, *types) -> bool:
        return self.peek().type in types

    # ── top level ─────────────────────────────────────────────────────────

    def parse(self) -> Program:
        modules, items = [], []
        while not self.match('EOF'):
            if self.match('MODULE'):
                modules.append(self._parse_module())
            else:
                items.append(self._parse_item())
        if not modules:
            modules = [Module(name='main', items=items)]
        return Program(modules=modules)

    def _parse_module(self) -> Module:
        self.expect('MODULE')
        name = self.expect('IDENT').value
        self.expect('LBRACE')
        items = []
        while not self.match('RBRACE', 'EOF'):
            items.append(self._parse_item())
        self.expect('RBRACE')
        return Module(name=name, items=items)

    # ── item ──────────────────────────────────────────────────────────────

    def _parse_item(self) -> Node:
        ann = self._parse_annotations()
        t = self.peek()
        if t.type == 'CONST':
            return self._parse_const(ann)
        if t.type == 'LET':
            return self._parse_let(ann)
        if t.type == 'DEFINE':
            return self._parse_define(ann)
        if t.type == 'ASSERT':
            self.advance()
            return Assert(expr=self._parse_expr())
        # expression statement
        return self._parse_expr()

    def _parse_annotations(self) -> List[Annotation]:
        ann = []
        while self.match('ANNOT'):
            raw = self.advance().value
            if '(' in raw:
                name, rest = raw.split('(', 1)
                ann.append(Annotation(name=name[1:], args=rest.rstrip(')')))
            else:
                ann.append(Annotation(name=raw[1:], args=None))
        return ann

    def _parse_const(self, ann) -> ConstDecl:
        self.expect('CONST')
        name = self.expect('IDENT').value
        self.expect('ASSIGN')
        val = self._parse_expr()
        return ConstDecl(name=name, value=val, annotations=ann)

    def _parse_let(self, ann) -> LetDecl:
        self.expect('LET')
        name = self.expect('IDENT').value
        self.expect('ASSIGN')
        val = self._parse_expr()
        return LetDecl(name=name, value=val, annotations=ann)

    def _parse_define(self, ann) -> FunctionDecl:
        self.expect('DEFINE')
        name = self.expect('IDENT').value
        self.expect('LPAREN')
        params = []
        while not self.match('RPAREN', 'EOF'):
            params.append(self.expect('IDENT').value)
            if self.match('COMMA'):
                self.advance()
        self.expect('RPAREN')
        self.expect('BEGIN')
        body = []
        while not self.match('END', 'EOF'):
            if self.match('RETURN'):
                self.advance()
                body.append(Return(expr=self._parse_expr()))
            elif self.match('ASSERT'):
                self.advance()
                body.append(Assert(expr=self._parse_expr()))
            elif self.match('LET'):
                body.append(self._parse_let([]))
            elif self.match('CONST'):
                body.append(self._parse_const([]))
            else:
                body.append(self._parse_expr())
        self.expect('END')
        return FunctionDecl(name=name, params=params, body=body, annotations=ann)

    # ── expressions (Pratt-style precedence climbing) ─────────────────────

    def _parse_expr(self) -> Node:
        return self._parse_or()

    def _parse_or(self) -> Node:
        left = self._parse_and()
        while self.match('OR', 'PIPE'):
            op = self.advance().value
            left = BinaryExpr(op='or', left=left, right=self._parse_and())
        return left

    def _parse_and(self) -> Node:
        left = self._parse_equality()
        while self.match('AND', 'AMP'):
            op = self.advance().value
            left = BinaryExpr(op='and', left=left, right=self._parse_equality())
        return left

    def _parse_equality(self) -> Node:
        left = self._parse_relational()
        while self.match('EQ', 'NEQ'):
            op = self.advance().value
            left = BinaryExpr(op=op, left=left, right=self._parse_relational())
        return left

    def _parse_relational(self) -> Node:
        left = self._parse_shift()
        while self.match('LT', 'GT', 'LE', 'GE'):
            op = self.advance().value
            left = BinaryExpr(op=op, left=left, right=self._parse_shift())
        return left

    def _parse_shift(self) -> Node:
        left = self._parse_bitor()
        while self.match('LSH', 'RSH'):
            op = self.advance().value
            left = BinaryExpr(op=op, left=left, right=self._parse_bitor())
        return left

    def _parse_bitor(self) -> Node:
        left = self._parse_bitxor()
        while self.match('PIPE'):
            self.advance()
            left = BinaryExpr(op='|', left=left, right=self._parse_bitxor())
        return left

    def _parse_bitxor(self) -> Node:
        left = self._parse_bitand()
        while self.match('CARET'):
            self.advance()
            left = BinaryExpr(op='^', left=left, right=self._parse_bitand())
        return left

    def _parse_bitand(self) -> Node:
        left = self._parse_add()
        while self.match('AMP'):
            self.advance()
            left = BinaryExpr(op='&', left=left, right=self._parse_add())
        return left

    def _parse_add(self) -> Node:
        left = self._parse_mul()
        while self.match('PLUS', 'MINUS'):
            op = self.advance().value
            left = BinaryExpr(op=op, left=left, right=self._parse_mul())
        return left

    def _parse_mul(self) -> Node:
        left = self._parse_unary()
        while self.match('STAR', 'SLASH', 'PERCENT', 'POW'):
            op = self.advance().value
            left = BinaryExpr(op=op, left=left, right=self._parse_unary())
        return left

    def _parse_unary(self) -> Node:
        if self.match('MINUS', 'TILDE', 'NOT'):
            op = self.advance().value
            return UnaryExpr(op=op, operand=self._parse_unary())
        return self._parse_postfix()

    def _parse_postfix(self) -> Node:
        node = self._parse_primary()
        while self.match('DOT'):
            self.advance()
            field = self.expect('IDENT').value
            node = FieldAccess(obj=node, field=field)
        return node

    def _parse_primary(self) -> Node:
        t = self.peek()

        if t.type == 'NUMBER':
            self.advance()
            return IntegerLiteral(int(t.value))

        if t.type == 'HEX':
            self.advance()
            return HexLiteral(raw=t.value)

        if t.type in ('TRUE', 'FALSE'):
            self.advance()
            return BoolLiteral(t.type == 'TRUE')

        if t.type == 'STRING':
            self.advance()
            s = t.value[1:-1].encode('utf-8').decode('unicode_escape')
            return StringLiteral(s)

        if t.type == 'BYTES':
            self.advance()
            raw = t.value[2:-1]
            b = raw.encode('utf-8').decode('unicode_escape').encode('latin1')
            return BytesLiteral(b)

        if t.type == 'SOME':
            self.advance()
            self.expect('LPAREN')
            v = self._parse_expr()
            self.expect('RPAREN')
            return OptionLiteral(tag='some', value=v)

        if t.type == 'NONE':
            self.advance()
            return OptionLiteral(tag='none', value=None)

        # identifiers and keyword-named builtins (concat, len, slice, sha256_hex, etc.)
        _CALLABLE_KEYWORDS = {'CONCAT', 'LEN', 'SLICE', 'SOME', 'OK', 'ERR',
                               'BYTES', 'BYTE', 'OPTION', 'RESULT'}
        if t.type == 'IDENT' or t.type in _CALLABLE_KEYWORDS:
            name = self.advance().value
            if self.match('LPAREN'):
                self.advance()
                args = []
                while not self.match('RPAREN', 'EOF'):
                    args.append(self._parse_expr())
                    if self.match('COMMA'):
                        self.advance()
                self.expect('RPAREN')
                return Call(callee=name, args=args)
            return Identifier(name=name)

        if t.type == 'LPAREN':
            self.advance()
            expr = self._parse_expr()
            self.expect('RPAREN')
            return expr

        if t.type == 'LBRACE':
            return self._parse_dict_or_list()

        if t.type == 'LBRACKET':
            self.advance()
            items = []
            while not self.match('RBRACKET', 'EOF'):
                items.append(self._parse_expr())
                if self.match('COMMA'):
                    self.advance()
            self.expect('RBRACKET')
            return ListLiteral(items=items)

        raise ParseError(f"Unexpected token {t.type!r} ({t.value!r}) at {t.line}:{t.col}")

    def _parse_dict_or_list(self) -> Node:
        self.expect('LBRACE')
        # peek: if next is IDENT COLON → dict
        if self.peek().type == 'IDENT' and self.peek2().type == 'COLON':
            pairs = []
            while not self.match('RBRACE', 'EOF'):
                key = self.expect('IDENT').value
                self.expect('COLON')
                val = self._parse_expr()
                pairs.append((key, val))
                if self.match('COMMA'):
                    self.advance()
            self.expect('RBRACE')
            return DictLiteral(pairs=pairs)
        else:
            items = []
            while not self.match('RBRACE', 'EOF'):
                items.append(self._parse_expr())
                if self.match('COMMA'):
                    self.advance()
            self.expect('RBRACE')
            return ListLiteral(items=items)


def parse(code: str) -> Program:
    tokens = tokenize(code)
    return Parser(tokens).parse()
