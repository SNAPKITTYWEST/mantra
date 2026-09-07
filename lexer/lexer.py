# lexer/lexer.py
from __future__ import annotations
import re
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

TOKEN_SPEC = [
    ('HEX',      r'0x[0-9A-Fa-f]+'),
    ('NUMBER',   r'\d+'),
    ('ANNOT',    r'@[A-Za-z_][A-Za-z0-9_]*(\([^\)]*\))?'),
    ('IDENT',    r'[A-Za-z_][A-Za-z0-9_]*'),
    ('STRING',   r'"([^"\\]|\\.)*"'),
    ('BYTES',    r"b'([^'\\]|\\.)*'"),
    ('POW',      r'\*\*'),
    ('LSH',      r'<<'),
    ('RSH',      r'>>'),
    ('EQ',       r'=='),
    ('NEQ',      r'!='),
    ('LE',       r'<='),
    ('GE',       r'>='),
    ('LT',       r'<'),
    ('GT',       r'>'),
    ('ASSIGN',   r'='),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COMMA',    r','),
    ('COLON',    r':'),
    ('DOT',      r'\.'),
    ('SEMICOL',  r';'),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('STAR',     r'\*'),
    ('SLASH',    r'/'),
    ('PERCENT',  r'%'),
    ('AMP',      r'&'),
    ('PIPE',     r'\|'),
    ('CARET',    r'\^'),
    ('TILDE',    r'~'),
    ('COMMENT',  r'#[^\n]*'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t\r]+'),
    ('MISMATCH', r'.'),
]

TOK_REGEX = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))

KEYWORDS = {
    'const', 'let', 'define', 'return', 'if', 'else', 'while', 'for',
    'match', 'begin', 'end', 'assert', 'module', 'import', 'true', 'false',
    'bytes', 'byte', 'option', 'result', 'some', 'none', 'ok', 'err',
    'len', 'slice', 'concat', 'and', 'or', 'not', 'in',
}

def tokenize(code: str):
    line = 1
    col = 1
    for mo in TOK_REGEX.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NEWLINE':
            line += 1
            col = 1
            continue
        if kind in ('SKIP', 'COMMENT'):
            col += len(value)
            continue
        if kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected {value!r} at {line}:{col}')
        if kind == 'IDENT' and value in KEYWORDS:
            kind = value.upper()
        yield Token(kind, value, line, col)
        col += len(value)
