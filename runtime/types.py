# runtime/types.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional

# ── error hierarchy ────────────────────────────────────────────────────────

class MantraError(Exception): pass
class DivisionByZero(MantraError): pass
class InvalidShift(MantraError): pass
class InvalidWidth(MantraError): pass
class InvalidHex(MantraError): pass
class InvalidUtf8(MantraError): pass
class IntegerOverflow(MantraError): pass
class InvalidArgument(MantraError): pass
class InvalidType(MantraError): pass
class HashInputError(MantraError): pass
class AssertionFailure(MantraError): pass
class UndefinedName(MantraError): pass

# ── value types ────────────────────────────────────────────────────────────

@dataclass
class Integer:
    value: int

@dataclass
class Boolean:
    value: bool

@dataclass
class Byte:
    value: int   # 0..255

@dataclass
class Bytes:
    data: bytes

@dataclass
class String:
    text: str

@dataclass
class FunctionValue:
    name: str
    params: list
    body: list
    closure: dict   # captured env at definition time

@dataclass
class BuiltinValue:
    name: str
    fn: Any   # callable

@dataclass
class ListValue:
    items: list

@dataclass
class DictValue:
    fields: dict

@dataclass
class Option:
    tag: str   # 'some' | 'none'
    value: Optional[Any]

@dataclass
class Result:
    tag: str   # 'ok' | 'err'
    value: Any

# ── explicit conversions ───────────────────────────────────────────────────

def integer_to_u32(i: Integer) -> int:
    return i.value & 0xFFFFFFFF

def integer_to_u64(i: Integer) -> int:
    return i.value & 0xFFFFFFFFFFFFFFFF

def u32_to_integer(u: int) -> Integer:
    if u < 0 or u > 0xFFFFFFFF:
        raise InvalidArgument("u32 out of range")
    return Integer(u)

def integer_to_bytes(i: Integer, length: int, byteorder: str = 'big', signed: bool = False) -> Bytes:
    try:
        return Bytes(i.value.to_bytes(length, byteorder, signed=signed))
    except OverflowError:
        raise IntegerOverflow("integer does not fit in requested byte length")

def bytes_to_integer(b: Bytes, byteorder: str = 'big', signed: bool = False) -> Integer:
    return Integer(int.from_bytes(b.data, byteorder, signed=signed))

def hex_to_bytes(h: str) -> Bytes:
    h = h.removeprefix('0x')
    if len(h) % 2 != 0:
        raise InvalidHex("hex length must be even")
    try:
        return Bytes(bytes.fromhex(h))
    except Exception:
        raise InvalidHex("invalid hex string")

def bytes_to_hex(b: Bytes) -> String:
    return String(b.data.hex())
