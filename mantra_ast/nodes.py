# ast/nodes.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    modules: List['Module']

@dataclass
class Module(Node):
    name: str
    items: List[Node]

@dataclass
class Annotation(Node):
    name: str
    args: Optional[str]

@dataclass
class ConstDecl(Node):
    name: str
    value: Node
    annotations: List[Annotation] = field(default_factory=list)

@dataclass
class LetDecl(Node):
    name: str
    value: Node
    annotations: List[Annotation] = field(default_factory=list)

@dataclass
class FunctionDecl(Node):
    name: str
    params: List[str]
    body: List[Node]
    annotations: List[Annotation] = field(default_factory=list)

@dataclass
class Return(Node):
    expr: Node

@dataclass
class If(Node):
    cond: Node
    then_branch: List[Node]
    else_branch: Optional[List[Node]]

@dataclass
class While(Node):
    cond: Node
    body: List[Node]

@dataclass
class For(Node):
    var: str
    iterable: Node
    body: List[Node]

@dataclass
class Assert(Node):
    expr: Node

@dataclass
class BinaryExpr(Node):
    op: str
    left: Node
    right: Node

@dataclass
class UnaryExpr(Node):
    op: str
    operand: Node

@dataclass
class Call(Node):
    callee: str
    args: List[Node]

@dataclass
class FieldAccess(Node):
    obj: Node
    field: str

@dataclass
class Identifier(Node):
    name: str

@dataclass
class IntegerLiteral(Node):
    value: int

@dataclass
class HexLiteral(Node):
    raw: str

    @property
    def value(self) -> int:
        return int(self.raw, 16)

@dataclass
class BoolLiteral(Node):
    value: bool

@dataclass
class StringLiteral(Node):
    value: str

@dataclass
class BytesLiteral(Node):
    value: bytes

@dataclass
class ListLiteral(Node):
    items: List[Node]

@dataclass
class DictLiteral(Node):
    pairs: List[tuple]  # (key_str, Node)

@dataclass
class OptionLiteral(Node):
    tag: str   # 'some' or 'none'
    value: Optional[Node]
