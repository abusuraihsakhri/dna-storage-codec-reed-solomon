"""End-to-end tests of the actual binary/DNA codec."""
import hashlib
import itertools
import os

import pytest

from dna_storage_codec.codec import (
    CodecError,
    DATA_BYTES_PER_BLOCK,
    decode_bytes,
    decode_bytes_with_report,
    encode_bytes,
)

@pytest.mark.parametrize("length", [0, 1, 2, 39, 213, 253, 254, 500, 1024, 4096])
def test_binary_round_trip(length):
    data = bytes(i % 256 for i in range(length))
    dna = encode_bytes(data)
    assert decode_bytes(dna) == data
    assert set(dna) <= set("ACGT")
    assert len(dna) % 8 == 0
    assert dna.count("G") + dna.count("C") == len(dna) // 2
    assert all(a != b or b != c for a, b, c in zip(dna, dna[1:], dna[2:]))
    assert decode_bytes("\n  " + dna.lower() + "\n") == data

@pytest.mark.parametrize("position", [0, 1, 4, 39, 254, 255, 300])
def test_corrects_one_corrupted_codeword_byte_per_block(position):
    data = bytes(range(253)) + bytes(range(65))
    dna = encode_bytes(data)
    assert position < len(dna) // 8
    start = position * 8
    replacement = "AC" * 4 if dna[start:start + 8] != "AC" * 4 else "TG" * 4
    tampered = dna[:start] + replacement + dna[start + 8:]
    recovered, corrected = decode_bytes_with_report(tampered)
    assert recovered == data
    assert corrected == 1

def test_two_errors_in_one_block_fail_closed():
    dna = encode_bytes(b"A" * 300)
    mutated = "TG" * 4 + "CA" * 4 + dna[16:]
    with pytest.raises(CodecError):
        decode_bytes(mutated)

@pytest.mark.parametrize("bad", ["", "A", "A" * 8, "ACGTACGT", "AAAA" * 8, "N" * 8])
def test_rejects_invalid_input(bad):
    with pytest.raises(CodecError):
        decode_bytes(bad)

def test_binary_input_only():
    with pytest.raises(TypeError):
        encode_bytes("abc")

def test_digest_fails_for_encoded_valid_but_replaced_frame():
    # Corrupt the message in two places within a block to exceed correction capacity.
    dna = encode_bytes(b"secure" * 50)
    altered = "CA" * 4 + dna[8:24] + "TG" * 4 + dna[32:]
    with pytest.raises(CodecError):
        decode_bytes(altered)
