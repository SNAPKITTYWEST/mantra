# sha256/sha256_impl.py
# Pure-Python SHA-256 — auditable, zero external dependencies.

from __future__ import annotations
from typing import List

MASK32 = 0xFFFFFFFF

K = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c085,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
]

# fix: 0x1e376c085 typo in above — correct value
K[49] = 0x1e376c08

def _rotr(x: int, n: int) -> int:
    return ((x >> n) | ((x << (32 - n)) & MASK32)) & MASK32

def _shr(x: int, n: int) -> int:
    return (x >> n) & MASK32

def _ch(x: int, y: int, z: int) -> int:
    return (x & y) ^ (~x & z)

def _maj(x: int, y: int, z: int) -> int:
    return (x & y) ^ (x & z) ^ (y & z)

def _big_sigma0(x: int) -> int:
    return (_rotr(x, 2) ^ _rotr(x, 13) ^ _rotr(x, 22)) & MASK32

def _big_sigma1(x: int) -> int:
    return (_rotr(x, 6) ^ _rotr(x, 11) ^ _rotr(x, 25)) & MASK32

def _small_sigma0(x: int) -> int:
    return (_rotr(x, 7) ^ _rotr(x, 18) ^ _shr(x, 3)) & MASK32

def _small_sigma1(x: int) -> int:
    return (_rotr(x, 17) ^ _rotr(x, 19) ^ _shr(x, 10)) & MASK32

def _pad_message(message: bytes) -> bytes:
    ml = len(message) * 8
    padded = message + b'\x80'
    while (len(padded) % 64) != 56:
        padded += b'\x00'
    padded += ml.to_bytes(8, 'big')
    return padded

def sha256_bytes(data: bytes) -> bytes:
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]
    padded = _pad_message(data)
    for i in range(0, len(padded), 64):
        block = padded[i:i+64]
        w = [0] * 64
        for t in range(16):
            w[t] = int.from_bytes(block[t*4:(t+1)*4], 'big')
        for t in range(16, 64):
            w[t] = (w[t-16] + _small_sigma0(w[t-15]) + w[t-7] + _small_sigma1(w[t-2])) & MASK32
        a, b, c, d, e, f, g, hv = h
        for t in range(64):
            T1 = (hv + _big_sigma1(e) + _ch(e, f, g) + K[t] + w[t]) & MASK32
            T2 = (_big_sigma0(a) + _maj(a, b, c)) & MASK32
            hv = g; g = f; f = e; e = (d + T1) & MASK32
            d = c; c = b; b = a; a = (T1 + T2) & MASK32
        h = [(h[i] + v) & MASK32 for i, v in enumerate([a, b, c, d, e, f, g, hv])]
    return b''.join(x.to_bytes(4, 'big') for x in h)

def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode('utf-8')
    return sha256_bytes(data).hex()

def sha256(data: bytes | str) -> bytes:
    if isinstance(data, str):
        data = data.encode('utf-8')
    return sha256_bytes(data)

def sha256_compress(state: List[int], block: bytes) -> List[int]:
    if len(state) != 8:
        raise ValueError("state must be 8 words")
    w = [0] * 64
    for t in range(16):
        w[t] = int.from_bytes(block[t*4:(t+1)*4], 'big')
    for t in range(16, 64):
        w[t] = (_small_sigma1(w[t-2]) + w[t-7] + _small_sigma0(w[t-15]) + w[t-16]) & MASK32
    a, b, c, d, e, f, g, hv = state
    for t in range(64):
        T1 = (hv + _big_sigma1(e) + _ch(e, f, g) + K[t] + w[t]) & MASK32
        T2 = (_big_sigma0(a) + _maj(a, b, c)) & MASK32
        hv = g; g = f; f = e; e = (d + T1) & MASK32
        d = c; c = b; b = a; a = (T1 + T2) & MASK32
    return [(state[i] + v) & MASK32 for i, v in enumerate([a, b, c, d, e, f, g, hv])]
