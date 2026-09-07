from runtime.types import Bytes, String, InvalidType
from sha256.sha256_impl import sha256_bytes, sha256_hex as _sha256_hex

def sha256_fn(arg) -> Bytes:
    if isinstance(arg, Bytes):
        return Bytes(sha256_bytes(arg.data))
    if isinstance(arg, String):
        return Bytes(sha256_bytes(arg.text.encode('utf-8')))
    raise InvalidType(f"sha256 expects Bytes or String, got {type(arg).__name__}")

def sha256_hex_fn(arg) -> String:
    if isinstance(arg, Bytes):
        return String(_sha256_hex(arg.data))
    if isinstance(arg, String):
        return String(_sha256_hex(arg.text.encode('utf-8')))
    raise InvalidType(f"sha256_hex expects Bytes or String, got {type(arg).__name__}")
