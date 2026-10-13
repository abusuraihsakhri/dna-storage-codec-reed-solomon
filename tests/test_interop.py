"""Language interoperability checks using Node when it is available."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from dna_storage_codec.codec import encode_bytes, decode_bytes

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")

@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_python_encoding_decodes_in_javascript():
    payload = bytes(range(256)) + b"\x00\xff\x01" * 40
    sequence = encode_bytes(payload)
    js = """
        import {decodeBytes} from './web/codec.mjs';
        const value = await decodeBytes(JSON.parse(process.argv[1]));
        process.stdout.write(Buffer.from(value.bytes).toString('hex'));
    """
    result = subprocess.run([NODE, "--input-type=module", "-e", js, json.dumps(sequence)],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    assert bytes.fromhex(result.stdout) == payload

@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_javascript_encoding_decodes_in_python():
    payload = bytes(range(256)) * 2
    js = """
        import {encodeBytes} from './web/codec.mjs';
        const bytes = Buffer.from(process.argv[1], 'hex');
        process.stdout.write(await encodeBytes(new Uint8Array(bytes)));
    """
    result = subprocess.run([NODE, "--input-type=module", "-e", js, payload.hex()],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    assert decode_bytes(result.stdout) == payload
