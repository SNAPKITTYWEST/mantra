from runtime.types import Bytes, Integer, InvalidArgument

def bytes_from_list(lst) -> Bytes:
    return Bytes(bytes([x.value if isinstance(x, Integer) else int(x) for x in lst]))

def len_bytes(b: Bytes) -> Integer:
    return Integer(len(b.data))

def get_byte(b: Bytes, idx: Integer) -> Integer:
    if idx.value < 0 or idx.value >= len(b.data):
        raise InvalidArgument("byte index out of range")
    return Integer(b.data[idx.value])

def slice_bytes(b: Bytes, start: Integer, end: Integer) -> Bytes:
    return Bytes(b.data[start.value:end.value])

def concat_bytes(*parts) -> Bytes:
    result = b''
    for p in parts:
        if isinstance(p, Bytes):
            result += p.data
        else:
            raise InvalidArgument("concat expects Bytes")
    return Bytes(result)
