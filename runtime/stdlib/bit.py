from runtime.types import Integer, InvalidShift

def band(a: Integer, b: Integer) -> Integer:
    return Integer(a.value & b.value)

def bor(a: Integer, b: Integer) -> Integer:
    return Integer(a.value | b.value)

def bxor(a: Integer, b: Integer) -> Integer:
    return Integer(a.value ^ b.value)

def bnot(a: Integer, width: int = None) -> Integer:
    if width is None:
        return Integer(~a.value)
    return Integer((~a.value) & ((1 << width) - 1))

def shl(a: Integer, n: Integer) -> Integer:
    if n.value < 0: raise InvalidShift("negative shift")
    return Integer(a.value << n.value)

def shr(a: Integer, n: Integer) -> Integer:
    if n.value < 0: raise InvalidShift("negative shift")
    return Integer(a.value >> n.value)

def rotl(x: Integer, n: Integer, width: int) -> Integer:
    if width <= 0: raise InvalidShift("invalid width")
    nmod = n.value % width
    mask = (1 << width) - 1
    v = x.value & mask
    return Integer(((v << nmod) & mask) | ((v >> (width - nmod)) & mask))

def rotr(x: Integer, n: Integer, width: int) -> Integer:
    if width <= 0: raise InvalidShift("invalid width")
    nmod = n.value % width
    mask = (1 << width) - 1
    v = x.value & mask
    return Integer(((v >> nmod) & mask) | ((v << (width - nmod)) & mask))
