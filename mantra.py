#!/usr/bin/env python3
# mantra.py — MANTRA CLI
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from runtime.runtime import run_file, run_source
from sha256.sha256_impl import sha256_hex

def cmd_run(path):
    result = run_file(path)
    if result is not None:
        from runtime.evaluator import Evaluator
        ev = Evaluator()
        print(ev._display(result))

def cmd_hash(data: str):
    print(sha256_hex(data))

def cmd_eval(expr: str):
    result = run_source(expr)
    if result is not None:
        from runtime.evaluator import Evaluator
        ev = Evaluator()
        print(ev._display(result))

def cmd_test():
    import subprocess
    sys.exit(subprocess.call([sys.executable, '-m', 'pytest', 'tests/', '-v']))

def usage():
    print("MANTRA language interpreter")
    print()
    print("Usage:")
    print("  mantra run <file.m>      run a MANTRA source file")
    print("  mantra eval <expr>       evaluate an expression")
    print("  mantra hash <string>     SHA-256 hex of a string")
    print("  mantra test              run test suite")

def main():
    if len(sys.argv) < 2:
        usage()
        return
    cmd = sys.argv[1]
    if cmd == 'run'  and len(sys.argv) >= 3: cmd_run(sys.argv[2])
    elif cmd == 'eval' and len(sys.argv) >= 3: cmd_eval(sys.argv[2])
    elif cmd == 'hash' and len(sys.argv) >= 3: cmd_hash(sys.argv[2])
    elif cmd == 'test': cmd_test()
    else: usage()

if __name__ == '__main__':
    main()
