from runtime.types import ListValue, DictValue, Integer, InvalidArgument

def list_len(lst: ListValue) -> Integer:
    return Integer(len(lst.items))

def list_get(lst: ListValue, idx: Integer):
    i = idx.value
    if i < 0 or i >= len(lst.items):
        raise InvalidArgument("list index out of range")
    return lst.items[i]

def list_append(lst: ListValue, item) -> ListValue:
    return ListValue(items=lst.items + [item])

def dict_get(d: DictValue, key: str):
    if key not in d.fields:
        raise InvalidArgument(f"key {key!r} not found in dict")
    return d.fields[key]
