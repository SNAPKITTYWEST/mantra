from runtime.runtime import run_source
from runtime.types import Integer, String

def test_const():
    env = run_source('const x = 42')

def test_arithmetic():
    run_source('const r = 2 + 3 * 4')

def test_sha256_hex():
    run_source('''
const h = sha256_hex(hex_to_bytes("616263"))
''')

def test_ledger_example():
    import os
    path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'ledger.m')
    from runtime.runtime import run_file
    run_file(path)

def test_function():
    run_source('''
define double(x)
begin
    return x + x
end
const r = double(21)
''')
