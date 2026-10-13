"""Binary-to-DNA codec with RS(255,253) single-symbol correction.

Wire format: DNA dinucleotides (AC, CA, GT, TG) encode two bits each.
The byte stream contains successive systematic Reed–Solomon blocks. The
uncoded payload is b"DSR1" + uint32 length + SHA-256 digest + raw bytes.

Each block has two RS parity bytes and corrects one unknown erroneous byte.
This implementation is not a fountain code or a sequencing pipeline.
"""
from __future__ import annotations

import hashlib
import hmac

MAGIC = b"DSR1"
MAX_PAYLOAD_BYTES = 16 * 1024 * 1024
DATA_BYTES_PER_BLOCK = 253
CODE_BYTES_PER_BLOCK = 255
_PAIR = ("AC", "CA", "GT", "TG")
_REVERSE = {pair: n for n, pair in enumerate(_PAIR)}

_EXP = [0] * 512
_LOG = [0] * 256
_value = 1
for _index in range(255):
    _EXP[_index] = _value
    _LOG[_value] = _index
    _value <<= 1
    if _value & 0x100:
        _value ^= 0x11D
for _index in range(255, 512):
    _EXP[_index] = _EXP[_index - 255]


class CodecError(ValueError):
    """Invalid DNA sequence, damaged block, or failed integrity check."""


def _multiply(a: int, b: int) -> int:
    return 0 if not a or not b else _EXP[_LOG[a] + _LOG[b]]


def _syndromes(block: bytes | bytearray) -> tuple[int, int]:
    s0 = s1 = 0
    for value in block:
        s0 ^= value
        s1 = _multiply(s1, 2) ^ value
    return s0, s1


def _encode_block(block: bytes) -> bytes:
    if not 1 <= len(block) <= DATA_BYTES_PER_BLOCK:
        raise CodecError("Invalid block length")
    # Generator polynomial (x + 1)(x + 2) = x^2 + 3x + 2
    work = bytearray(block) + bytearray(2)
    for i, value in enumerate(block):
        if value:
            work[i + 1] ^= _multiply(value, 3)
            work[i + 2] ^= _multiply(value, 2)
    return block + bytes(work[-2:])


def _decode_block(block: bytes) -> tuple[bytes, bool]:
    if not 3 <= len(block) <= CODE_BYTES_PER_BLOCK:
        raise CodecError("Malformed Reed–Solomon block length")
    corrected = bytearray(block)
    s0, s1 = _syndromes(corrected)
    if s0 == 0 and s1 == 0:
        return bytes(corrected[:-2]), False
    if s0 == 0 or s1 == 0:
        raise CodecError("Uncorrectable Reed–Solomon block")
    # For one error of magnitude e in polynomial position j:
    # syndrome(1) = e, syndrome(2) = e * 2^j.
    position_exponent = (_LOG[s1] - _LOG[s0]) % 255
    index = len(corrected) - 1 - position_exponent
    if not 0 <= index < len(corrected):
        raise CodecError("Uncorrectable Reed–Solomon block")
    corrected[index] ^= s0
    if _syndromes(corrected) != (0, 0):
        raise CodecError("Uncorrectable Reed–Solomon block")
    return bytes(corrected[:-2]), True


def _to_dna(raw: bytes) -> str:
    return "".join(
        _PAIR[(value >> shift) & 3]
        for value in raw
        for shift in (6, 4, 2, 0)
    )


def _from_dna(sequence: str) -> bytes:
    if not isinstance(sequence, str):
        raise CodecError("DNA sequence must be text")
    sequence = "".join(sequence.split()).upper()
    if len(sequence) % 8:
        raise CodecError("DNA length must be a multiple of eight nucleotides")
    if len(sequence) > (MAX_PAYLOAD_BYTES + 40 + 2 * ((MAX_PAYLOAD_BYTES + 292) // 253)) * 8:
        raise CodecError("DNA sequence exceeds supported size")
    result = bytearray()
    for i in range(0, len(sequence), 8):
        number = 0
        for j in (0, 2, 4, 6):
            try:
                digit = _REVERSE[sequence[i + j:i + j + 2]]
            except KeyError as exc:
                raise CodecError(f"Invalid dinucleotide near position {i + j + 1}") from exc
            number = (number << 2) | digit
        result.append(number)
    return bytes(result)


def encode_bytes(payload: bytes) -> str:
    """Encode up to 16 MiB; outputs exactly 50% GC and run lengths <= 2."""
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise CodecError("Payload exceeds the 16 MiB limit")
    frame = MAGIC + len(payload).to_bytes(4, "big") + hashlib.sha256(payload).digest() + payload
    protected = b"".join(
        _encode_block(frame[i:i + DATA_BYTES_PER_BLOCK])
        for i in range(0, len(frame), DATA_BYTES_PER_BLOCK)
    )
    return _to_dna(protected)


def decode_bytes_with_report(sequence: str) -> tuple[bytes, int]:
    """Recover original bytes and report corrected erroneous codeword bytes."""
    protected = _from_dna(sequence)
    if not protected:
        raise CodecError("Empty DNA sequence")
    blocks = []
    corrected_count = 0
    for i in range(0, len(protected), CODE_BYTES_PER_BLOCK):
        data, corrected = _decode_block(protected[i:i + CODE_BYTES_PER_BLOCK])
        blocks.append(data)
        corrected_count += int(corrected)
    frame = b"".join(blocks)
    if len(frame) < 40 or frame[:4] != MAGIC:
        raise CodecError("Invalid DNA storage frame")
    expected_length = int.from_bytes(frame[4:8], "big")
    payload = frame[40:]
    if expected_length > MAX_PAYLOAD_BYTES or len(payload) != expected_length:
        raise CodecError("Payload size mismatch")
    if not hmac.compare_digest(frame[8:40], hashlib.sha256(payload).digest()):
        raise CodecError("SHA-256 integrity check failed")
    return payload, corrected_count


def decode_bytes(sequence: str) -> bytes:
    """Decode DNA to original bytes; raise CodecError on corruption."""
    return decode_bytes_with_report(sequence)[0]
