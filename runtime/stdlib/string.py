from runtime.types import Bytes, String, InvalidUtf8, Integer

def to_bytes(s: String) -> Bytes:
    return Bytes(s.text.encode('utf-8'))

def from_bytes(b: Bytes) -> String:
    try:
        return String(b.data.decode('utf-8'))
    except UnicodeDecodeError:
        raise InvalidUtf8("invalid utf-8 bytes")

def len_string(s: String) -> Integer:
    return Integer(len(s.text))

def concat_strings(*parts) -> String:
    return String(''.join(p.text if isinstance(p, String) else str(p) for p in parts))
