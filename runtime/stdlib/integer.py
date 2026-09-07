from runtime.types import Integer, IntegerOverflow, InvalidArgument, DivisionByZero

def add_checked(a: Integer, b: Integer, width: int = None, signed: bool = True) -> Integer:
    res = a.value + b.value
    if width is not None:
        _check_range(res, width, signed, "add")
    return Integer(res)

def add_unchecked(a: Integer, b: Integer) -> Integer:
    return Integer(a.value + b.value)

def sub_checked(a: Integer, b: Integer, width: int = None, signed: bool = True) -> Integer:
    res = a.value - b.value
    if width is not None:
        _check_range(res, width, signed, "sub")
    return Integer(res)

def mul_checked(a: Integer, b: Integer, width: int = None, signed: bool = True) -> Integer:
    res = a.value * b.value
    if width is not None:
        _check_range(res, width, signed, "mul")
    return Integer(res)

def div(a: Integer, b: Integer) -> Integer:
    if b.value == 0:
        raise DivisionByZero("division by zero")
    return Integer(a.value // b.value)

def mod(a: Integer, b: Integer) -> Integer:
    if b.value == 0:
        raise DivisionByZero("mod by zero")
    return Integer(a.value % b.value)

def powi(a: Integer, b: Integer) -> Integer:
    if b.value < 0:
        raise InvalidArgument("negative exponent for integer pow")
    return Integer(pow(a.value, b.value))

def _check_range(val, width, signed, op):
    if signed:
        lo, hi = -(1 << (width - 1)), (1 << (width - 1)) - 1
    else:
        lo, hi = 0, (1 << width) - 1
    if not (lo <= val <= hi):
        raise IntegerOverflow(f"{op} overflow: {val} not in [{lo},{hi}]")
