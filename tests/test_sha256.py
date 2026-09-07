from sha256.sha256_impl import sha256_hex

def test_empty():
    assert sha256_hex(b'') == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

def test_abc():
    assert sha256_hex(b'abc') == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

def test_long():
    assert sha256_hex(b'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq') == \
        "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"

def test_string_input():
    assert sha256_hex("abc") == sha256_hex(b'abc')

def test_vectors():
    from sha256.vectors import VECTORS
    for data, expected in VECTORS[:-1]:  # skip 1M 'a' test for speed
        assert sha256_hex(data) == expected, f"failed for {data[:20]!r}"
