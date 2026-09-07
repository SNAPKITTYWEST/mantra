# runtime/evaluator.py
from __future__ import annotations
from mantra_ast.nodes import *
from runtime.types import *
from runtime.stdlib import sha256 as _sha256_mod
from runtime.stdlib import integer as _int_mod
from runtime.stdlib import bit as _bit_mod
from runtime.stdlib import bytes as _bytes_mod
from runtime.stdlib import hex as _hex_mod
from runtime.stdlib import string as _str_mod
from runtime.stdlib import collections as _coll_mod
from runtime.stdlib import result as _res_mod
from runtime.stdlib import testing as _test_mod

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class Evaluator:

    def __init__(self):
        self.globals: dict = {}
        self._load_builtins()

    # ── builtins ──────────────────────────────────────────────────────────

    def _load_builtins(self):
        b = self.globals
        # sha256
        b['sha256']     = BuiltinValue('sha256',     lambda a: _sha256_mod.sha256_fn(a[0]))
        b['sha256_hex'] = BuiltinValue('sha256_hex', lambda a: _sha256_mod.sha256_hex_fn(a[0]))
        # integer conversions
        b['integer_to_bytes'] = BuiltinValue('integer_to_bytes',
            lambda a: integer_to_bytes(a[0], a[1].value if isinstance(a[1], Integer) else int(a[1])))
        b['bytes_to_integer'] = BuiltinValue('bytes_to_integer',
            lambda a: bytes_to_integer(a[0]))
        b['hex_to_bytes'] = BuiltinValue('hex_to_bytes',
            lambda a: _hex_mod.hex_to_bytes(a[0]))
        b['bytes_to_hex'] = BuiltinValue('bytes_to_hex',
            lambda a: _hex_mod.bytes_to_hex(a[0]))
        # bytes ops
        b['concat']     = BuiltinValue('concat', lambda a: _bytes_mod.concat_bytes(*a)
                          if all(isinstance(x, Bytes) for x in a)
                          else _str_mod.concat_strings(*a))
        b['len']        = BuiltinValue('len', lambda a:
                          _bytes_mod.len_bytes(a[0]) if isinstance(a[0], Bytes)
                          else _coll_mod.list_len(a[0]) if isinstance(a[0], ListValue)
                          else _str_mod.len_string(a[0]))
        b['slice']      = BuiltinValue('slice', lambda a: _bytes_mod.slice_bytes(a[0], a[1], a[2]))
        # option / result
        b['some']       = BuiltinValue('some', lambda a: _res_mod.some(a[0]))
        b['none']       = BuiltinValue('none', lambda _: _res_mod.none())
        b['ok']         = BuiltinValue('ok',   lambda a: _res_mod.ok(a[0]))
        b['err']        = BuiltinValue('err',  lambda a: _res_mod.err(a[0]))
        # testing
        b['assert_eq']  = BuiltinValue('assert_eq',  lambda a: _test_mod.assert_eq(a[0], a[1]))
        b['assert_true']= BuiltinValue('assert_true', lambda a: _test_mod.assert_true(a[0]))
        # print
        b['print']      = BuiltinValue('print', lambda a: print(*[self._display(x) for x in a]) or String(''))

    # ── eval entry points ─────────────────────────────────────────────────

    def eval_program(self, prog: Program):
        result = None
        for module in prog.modules:
            for item in module.items:
                result = self.eval_item(item, self.globals)
        return result

    def eval_item(self, node: Node, env: dict):
        if isinstance(node, ConstDecl):
            val = self.eval_expr(node.value, env)
            env[node.name] = val
            return val
        if isinstance(node, LetDecl):
            val = self.eval_expr(node.value, env)
            env[node.name] = val
            return val
        if isinstance(node, FunctionDecl):
            fn = FunctionValue(name=node.name, params=node.params,
                               body=node.body, closure=dict(env))
            env[node.name] = fn
            return fn
        if isinstance(node, Assert):
            val = self.eval_expr(node.expr, env)
            v = val.value if isinstance(val, Boolean) else bool(val)
            if not v:
                raise AssertionFailure(f"assert failed")
            return val
        return self.eval_expr(node, env)

    # ── expression evaluator ──────────────────────────────────────────────

    def eval_expr(self, node: Node, env: dict):
        if isinstance(node, IntegerLiteral):
            return Integer(node.value)
        if isinstance(node, HexLiteral):
            return Integer(node.value)
        if isinstance(node, BoolLiteral):
            return Boolean(node.value)
        if isinstance(node, StringLiteral):
            return String(node.value)
        if isinstance(node, BytesLiteral):
            return Bytes(node.value)
        if isinstance(node, ListLiteral):
            return ListValue([self.eval_expr(i, env) for i in node.items])
        if isinstance(node, DictLiteral):
            return DictValue({k: self.eval_expr(v, env) for k, v in node.pairs})
        if isinstance(node, OptionLiteral):
            v = self.eval_expr(node.value, env) if node.value else None
            return Option(tag=node.tag, value=v)
        if isinstance(node, Identifier):
            if node.name not in env:
                raise UndefinedName(f"undefined: {node.name!r}")
            return env[node.name]
        if isinstance(node, FieldAccess):
            obj = self.eval_expr(node.obj, env)
            if isinstance(obj, DictValue):
                if node.field not in obj.fields:
                    raise InvalidArgument(f"field {node.field!r} not found")
                return obj.fields[node.field]
            raise InvalidType(f"field access on non-dict {type(obj).__name__}")
        if isinstance(node, Call):
            return self.eval_call(node, env)
        if isinstance(node, BinaryExpr):
            return self.eval_binary(node, env)
        if isinstance(node, UnaryExpr):
            return self.eval_unary(node, env)
        if isinstance(node, ConstDecl) or isinstance(node, LetDecl):
            val = self.eval_expr(node.value, env)
            env[node.name] = val
            return val
        raise MantraError(f"Cannot eval node: {type(node).__name__}")

    def eval_call(self, node: Call, env: dict):
        fn = env.get(node.callee)
        if fn is None:
            raise UndefinedName(f"undefined function: {node.callee!r}")
        args = [self.eval_expr(a, env) for a in node.args]
        if isinstance(fn, BuiltinValue):
            return fn.fn(args) or String('')
        if isinstance(fn, FunctionValue):
            local = dict(fn.closure)
            local.update(self.globals)
            for p, a in zip(fn.params, args):
                local[p] = a
            try:
                result = None
                for stmt in fn.body:
                    if isinstance(stmt, Return):
                        raise ReturnSignal(self.eval_expr(stmt.expr, local))
                    elif isinstance(stmt, LetDecl) or isinstance(stmt, ConstDecl):
                        v = self.eval_expr(stmt.value, local)
                        local[stmt.name] = v
                    else:
                        result = self.eval_item(stmt, local)
                return result
            except ReturnSignal as r:
                return r.value
        raise InvalidType(f"{node.callee!r} is not callable")

    def eval_binary(self, node: BinaryExpr, env: dict):
        l = self.eval_expr(node.left, env)
        r = self.eval_expr(node.right, env)
        op = node.op
        if op == '+':
            if isinstance(l, Integer) and isinstance(r, Integer):
                return Integer(l.value + r.value)
            if isinstance(l, Bytes) and isinstance(r, Bytes):
                return Bytes(l.data + r.data)
            if isinstance(l, String) and isinstance(r, String):
                return String(l.text + r.text)
        if op == '-' and isinstance(l, Integer): return Integer(l.value - r.value)
        if op == '*' and isinstance(l, Integer): return Integer(l.value * r.value)
        if op == '/' and isinstance(l, Integer):
            if r.value == 0: raise DivisionByZero("division by zero")
            return Integer(l.value // r.value)
        if op == '%' and isinstance(l, Integer):
            if r.value == 0: raise DivisionByZero("mod by zero")
            return Integer(l.value % r.value)
        if op == '**' and isinstance(l, Integer): return Integer(l.value ** r.value)
        if op == '&'  and isinstance(l, Integer): return Integer(l.value & r.value)
        if op == '|'  and isinstance(l, Integer): return Integer(l.value | r.value)
        if op == '^'  and isinstance(l, Integer): return Integer(l.value ^ r.value)
        if op == '<<' and isinstance(l, Integer): return Integer(l.value << r.value)
        if op == '>>' and isinstance(l, Integer): return Integer(l.value >> r.value)
        if op == '==': return Boolean(self._eq(l, r))
        if op == '!=': return Boolean(not self._eq(l, r))
        if op == '<'  and isinstance(l, Integer): return Boolean(l.value < r.value)
        if op == '>'  and isinstance(l, Integer): return Boolean(l.value > r.value)
        if op == '<=' and isinstance(l, Integer): return Boolean(l.value <= r.value)
        if op == '>=' and isinstance(l, Integer): return Boolean(l.value >= r.value)
        if op in ('and', '&&'): return Boolean(self._truthy(l) and self._truthy(r))
        if op in ('or',  '||'): return Boolean(self._truthy(l) or  self._truthy(r))
        raise MantraError(f"Unknown binary op {op!r} on {type(l).__name__}")

    def eval_unary(self, node: UnaryExpr, env: dict):
        v = self.eval_expr(node.operand, env)
        if node.op == '-' and isinstance(v, Integer): return Integer(-v.value)
        if node.op == '~' and isinstance(v, Integer): return Integer(~v.value)
        if node.op in ('not', '!'): return Boolean(not self._truthy(v))
        raise MantraError(f"Unknown unary op {node.op!r}")

    def _eq(self, a, b) -> bool:
        if type(a) != type(b): return False
        if isinstance(a, Integer): return a.value == b.value
        if isinstance(a, Boolean): return a.value == b.value
        if isinstance(a, String):  return a.text  == b.text
        if isinstance(a, Bytes):   return a.data  == b.data
        return a == b

    def _truthy(self, v) -> bool:
        if isinstance(v, Boolean): return v.value
        if isinstance(v, Integer): return v.value != 0
        if isinstance(v, String):  return len(v.text) > 0
        if isinstance(v, Bytes):   return len(v.data) > 0
        if isinstance(v, Option):  return v.tag == 'some'
        if isinstance(v, Result):  return v.tag == 'ok'
        return bool(v)

    def _display(self, v) -> str:
        if isinstance(v, Integer): return str(v.value)
        if isinstance(v, Boolean): return str(v.value).lower()
        if isinstance(v, String):  return v.text
        if isinstance(v, Bytes):   return v.data.hex()
        if isinstance(v, Option):  return f"some({self._display(v.value)})" if v.tag == 'some' else 'none'
        if isinstance(v, Result):  return f"{v.tag}({self._display(v.value)})"
        return repr(v)
