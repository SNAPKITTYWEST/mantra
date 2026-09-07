# gateway/mumps_gateway.py
# Binary scaffold for MUMPS integration.
#
# Binary record layout (300 bytes):
#   [0:8]   command_id  — ASCII, null-padded
#   [8:16]  tx_id       — signed int64 big-endian
#   [16:24] account_id  — signed int64 big-endian
#   [24:40] amount      — signed int128 big-endian
#   [40:43] currency    — ASCII
#   [43:44] direction   — 'D' debit / 'C' credit
#   [44:172] idem_key   — UTF-8, null-padded (128 bytes)
#   [172:300] corr_id   — UTF-8, null-padded (128 bytes)

def pack_command(cmd_id: str, tx_id: int, acct_id: int, amount: int,
                 currency: str, direction: str, idem: str, corr: str) -> bytes:
    return b''.join([
        cmd_id.encode('ascii')[:8].ljust(8, b'\x00'),
        tx_id.to_bytes(8, 'big', signed=True),
        acct_id.to_bytes(8, 'big', signed=True),
        amount.to_bytes(16, 'big', signed=True),
        currency.encode('ascii')[:3].ljust(3, b'\x00'),
        direction.encode('ascii')[:1],
        idem.encode('utf-8')[:128].ljust(128, b'\x00'),
        corr.encode('utf-8')[:128].ljust(128, b'\x00'),
    ])

def unpack_command(buf: bytes) -> dict:
    if len(buf) < 300:
        raise ValueError(f"buffer too small: {len(buf)} < 300")
    return {
        'cmd_id':          buf[0:8].rstrip(b'\x00').decode('ascii'),
        'transaction_id':  int.from_bytes(buf[8:16],   'big', signed=True),
        'account_id':      int.from_bytes(buf[16:24],  'big', signed=True),
        'amount':          int.from_bytes(buf[24:40],  'big', signed=True),
        'currency':        buf[40:43].rstrip(b'\x00').decode('ascii'),
        'direction':       buf[43:44].decode('ascii'),
        'idempotency_key': buf[44:172].rstrip(b'\x00').decode('utf-8'),
        'correlation_id':  buf[172:300].rstrip(b'\x00').decode('utf-8'),
    }

def dispatch_to_runtime(buf: bytes, runtime_dispatch):
    """runtime_dispatch: callable(dict) -> dict"""
    return runtime_dispatch(unpack_command(buf))
