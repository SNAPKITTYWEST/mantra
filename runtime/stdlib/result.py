from runtime.types import Result, Option

def ok(v) -> Result:
    return Result(tag='ok', value=v)

def err(e) -> Result:
    return Result(tag='err', value=e)

def some(v) -> Option:
    return Option(tag='some', value=v)

def none() -> Option:
    return Option(tag='none', value=None)
