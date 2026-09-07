# MANTRA

A deterministic, auditable programming language for ledger operations, cryptographic sealing, and verified integer computation.

![Tests](https://img.shields.io/badge/tests-23%2F23_passing-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![Dependencies](https://img.shields.io/badge/dependencies-zero-success?style=flat-square)
![SHA-256](https://img.shields.io/badge/SHA--256-pure_python-orange?style=flat-square)
![MUMPS](https://img.shields.io/badge/gateway-MUMPS%2FIBMi-purple?style=flat-square)
![License](https://img.shields.io/badge/license-Apache--2.0%20%7C%20MIT%20%7C%20Sovereign--Source--1.0-black?style=flat-square)

**Zero external dependencies. Pure Python. Auditable SHA-256. MUMPS gateway.**

---

## License

MANTRA is trilicensed. Choose the license that fits your use case:

| License | SPDX | Use Case |
|---|---|---|
| Apache-2.0 | `Apache-2.0` | Commercial use, patent protection, enterprise deployments |
| MIT | `MIT` | Open-source projects, academic research, minimal friction |
| Sovereign-Source-1.0 | `LicenseRef-Sovereign-Source-1.0` | Sovereign node deployments, SNAPKITTYWEST constellation |

All three licenses are in the `LICENSES/` directory. If in doubt, use Apache-2.0.

Authors: Ahmad Ali Parr, Jessica L. Williams (SNAPKITTYWEST)

---

## Project Layout

```
mantra/
├── mantra.py                   CLI entrypoint
├── lexer/lexer.py              Tokenizer (HEX, BYTES, annotations, keywords)
├── ast/nodes.py                AST node dataclasses
├── parser/parser.py            Pratt-style parser → AST
├── runtime/
│   ├── types.py                Integer, Boolean, Bytes, String, Option, Result, DictValue
│   ├── evaluator.py            Tree-walking evaluator with environment
│   ├── runtime.py              run_source / run_file
│   └── stdlib/
│       ├── integer.py          add/sub/mul/div/mod/pow with overflow checking
│       ├── bit.py              band/bor/bxor/bnot/shl/shr/rotl/rotr
│       ├── bytes.py            concat/slice/len/get_byte
│       ├── string.py           to_bytes/from_bytes/concat
│       ├── hex.py              bytes_to_hex/hex_to_bytes
│       ├── sha256.py           sha256/sha256_hex (wraps auditable impl)
│       ├── collections.py      list_len/list_get/dict_get
│       ├── result.py           ok/err/some/none
│       └── testing.py          assert_eq/assert_true/assert_false
├── sha256/
│   ├── sha256_impl.py          Pure-Python SHA-256 (auditable, no hashlib)
│   └── vectors.py              NIST canonical test vectors
├── gateway/
│   └── mumps_gateway.py        300-byte binary record pack/unpack/dispatch
├── compiler/                   (future compiler components)
├── tests/
│   ├── test_sha256.py
│   ├── test_integer.py
│   ├── test_bytes.py
│   └── test_evaluator.py
└── examples/
    ├── ledger.m                transaction seal
    └── treasury.m              multi-step ledger chain
```

---

## Language Quick Reference

```
# Constants and variables
const GENESIS = "0000000000000000000000000000000000000000000000000000000000000000"
let x = 42

# Functions with begin/end blocks
@deterministic
define seal(tx)
begin
    let id_bytes = integer_to_bytes(tx.id, 8)
    let payload  = concat(id_bytes, hex_to_bytes(tx.previous_hash))
    return sha256_hex(payload)
end

# Dict literals
const tx = {
    id: 12345,
    account: 98765,
    amount: 125000,
    previous_hash: GENESIS
}

const result = seal(tx)
```

### Types

| Type | Example |
|------|---------|
| Integer | `42`, `0xDEADBEEF` |
| Boolean | `true`, `false` |
| Bytes | `b'\xde\xad'` |
| String | `"hello"` |
| List | `{1, 2, 3}` or `[1, 2, 3]` |
| Dict | `{id: 1, amount: 100}` |
| Option | `some(x)`, `none` |
| Result | `ok(x)`, `err(msg)` |

### Built-in functions

| Function | Description |
|----------|-------------|
| `sha256(data)` | SHA-256 → Bytes |
| `sha256_hex(data)` | SHA-256 → hex String |
| `integer_to_bytes(n, len)` | Integer → Bytes (big-endian) |
| `bytes_to_integer(b)` | Bytes → Integer |
| `hex_to_bytes(s)` | hex String → Bytes |
| `bytes_to_hex(b)` | Bytes → hex String |
| `concat(a, b)` | Bytes ++ Bytes or String ++ String |
| `len(x)` | length of Bytes/String/List |
| `slice(b, start, end)` | sub-Bytes |

---

## CLI

```bash
python mantra.py run examples/ledger.m
python mantra.py eval 'const h = sha256_hex("abc")'
python mantra.py hash "hello world"
python mantra.py test
```

---

## SHA-256

`sha256/sha256_impl.py` is a self-contained pure-Python implementation — no `hashlib`, no `cryptography`. Every line is auditable. Used directly in the WORM seal path.

---

## MUMPS Gateway

`gateway/mumps_gateway.py` provides a 300-byte binary record contract for MUMPS integration:

```python
from gateway.mumps_gateway import pack_command, unpack_command

buf = pack_command("DEBIT", 1001, 9876, 50000, "USD", "D", "idem-key", "corr-id")
cmd = unpack_command(buf)
# → {'cmd_id': 'DEBIT', 'transaction_id': 1001, 'amount': 50000, ...}
```

---

## Run Tests

```bash
cd mantra
python -m pytest tests/ -v
```

---

## License

BSL 1.1 → MIT on 2029-01-01
