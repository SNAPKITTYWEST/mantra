from runtime.types import AssertionFailure, Boolean

def assert_eq(a, b):
    av = a.value if isinstance(a, Boolean) else a
    bv = b.value if isinstance(b, Boolean) else b
    if av != bv:
        raise AssertionFailure(f"assert_eq failed: {av!r} != {bv!r}")

def assert_true(v):
    val = v.value if isinstance(v, Boolean) else bool(v)
    if not val:
        raise AssertionFailure(f"assert_true failed: {v!r}")

def assert_false(v):
    val = v.value if isinstance(v, Boolean) else bool(v)
    if val:
        raise AssertionFailure(f"assert_false failed: {v!r}")
