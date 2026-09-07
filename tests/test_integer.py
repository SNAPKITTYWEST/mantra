from runtime.types import Integer
from runtime.stdlib.integer import add_checked, sub_checked, mul_checked, div, mod, powi
from runtime.types import IntegerOverflow, DivisionByZero
import pytest

def test_add():
    assert add_checked(Integer(2), Integer(3)).value == 5

def test_add_overflow():
    with pytest.raises(IntegerOverflow):
        add_checked(Integer(200), Integer(200), width=8, signed=False)

def test_sub():
    assert sub_checked(Integer(10), Integer(3)).value == 7

def test_mul():
    assert mul_checked(Integer(6), Integer(7)).value == 42

def test_div():
    assert div(Integer(10), Integer(3)).value == 3

def test_div_zero():
    with pytest.raises(DivisionByZero):
        div(Integer(5), Integer(0))

def test_mod():
    assert mod(Integer(10), Integer(3)).value == 1

def test_pow():
    assert powi(Integer(2), Integer(10)).value == 1024
