from runtime.types import Bytes, String, InvalidHex

def bytes_to_hex(b: Bytes) -> String:
    return String(b.data.hex())

def hex_to_bytes(s) -> Bytes:
    text = s.text if isinstance(s, String) else str(s)
    text = text.removeprefix('0x')
    if len(text) % 2 != 0:
        raise InvalidHex("hex length must be even")
    try:
        return Bytes(bytes.fromhex(text))
    except Exception:
        raise InvalidHex("invalid hex string")
