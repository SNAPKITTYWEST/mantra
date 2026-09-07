from runtime.types import Bytes, Integer, String
from runtime.stdlib.bytes import concat_bytes, len_bytes, slice_bytes
from runtime.stdlib.hex import bytes_to_hex, hex_to_bytes

def test_concat():
    a = Bytes(b'\x01\x02')
    b = Bytes(b'\x03\x04')
    assert concat_bytes(a, b).data == b'\x01\x02\x03\x04'

def test_len():
    assert len_bytes(Bytes(b'hello')).value == 5

def test_slice():
    b = Bytes(b'\x00\x01\x02\x03\x04')
    assert slice_bytes(b, Integer(1), Integer(3)).data == b'\x01\x02'

def test_hex_roundtrip():
    original = Bytes(b'\xde\xad\xbe\xef')
    hex_str = bytes_to_hex(original)
    assert hex_str.text == 'deadbeef'
    back = hex_to_bytes(hex_str)
    assert back.data == original.data

def test_hex_input():
    result = hex_to_bytes(String('0000000000000000000000000000000000000000000000000000000000000000'))
    assert len(result.data) == 32
    assert result.data == b'\x00' * 32
