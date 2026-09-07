# runtime/runtime.py — thin shell around evaluator, used by CLI
from parser.parser import parse
from runtime.evaluator import Evaluator

def run_source(code: str):
    prog = parse(code)
    ev = Evaluator()
    return ev.eval_program(prog)

def run_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    return run_source(code)
