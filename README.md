# DNA Storage Codec Reed–Solomon

A small reference implementation for encoding binary data as DNA text and recovering it with per-block Reed–Solomon error correction. The browser interface works without a backend or network request.

## Features

- **Binary → DNA → binary**: encode arbitrary files and recover their original bytes.
- **Fixed DNA composition**: each two-bit symbol maps to one of `AC`, `CA`, `GT` or `TG`. Encoded sequences contain exactly 50% G/C bases and no homopolymer runs longer than two bases.
- **RS(255,253)**: two parity bytes per block, correcting **one unknown erroneous byte in each block**. Extra errors are not guaranteed recoverable.
- **Integrity**: SHA-256 digest verifies the recovered payload.
- **Local browser app**: encode/decode text or files, import/export `.dna` files, and view correction statistics. All codec processing stays in the browser.
- **Python CLI and library**: identical interoperable wire format in Python and JavaScript.
- **Legacy audit utilities**: the original metric-threshold evaluators, FastAPI endpoints and batch CSV commands are retained, separately from the DNA codec.

This is **not** a DNA fountain code or an experimentally validated DNA synthesis/sequencing workflow. The codec operates on deterministic digital sequences, not FASTQ reads. The legacy domain-threshold rules are illustrative and should not be treated as clinical or laboratory standards.

## Browser application

Open `web/index.html` via a local HTTP server or use the GitHub Pages site once deployed. Modern browsers need HTTPS or localhost for Web Crypto.

```bash
python -m http.server 8080 --directory web
# Open http://localhost:8080
```

Select text or a file and click **Encode to DNA**. Copy/save the DNA sequence, or paste/import a DNA sequence and click **Decode & verify**. Save decoded binary data when needed. The 16 MiB payload limit applies to both interfaces. Large DNA strings can consume substantially more memory than the original binary data.

## Python installation and CLI

Requires Python 3.10 or newer.

```bash
git clone https://github.com/abusuraihsakhri/dna-storage-codec-reed-solomon.git
cd dna-storage-codec-reed-solomon
python -m pip install -e .
dna-storage-codec-reed-solomon encode -i input.bin -o encoded.dna
dna-storage-codec-reed-solomon decode -i encoded.dna -o restored.bin
```

From Python:

```python
from dna_storage_codec.codec import encode_bytes, decode_bytes

sequence = encode_bytes(b"hello")
assert decode_bytes(sequence) == b"hello"
```

DNA strings can be copied between the Python and JavaScript implementations. Each protected byte is represented by eight nucleotides. A 40-byte header stores the magic, original byte count and SHA-256 digest; each RS codeword adds two parity bytes.

## Legacy threshold audit and REST API

The existing `cli.py`, `agents/`, `enrichment.py`, and `dna_storage_codec.cli audit/batch/chat` interfaces remain available. They are metric-rule or simulation utilities, **not molecular DNA coders**.

The legacy audit service requires `AUDIT_SECRET_KEY` (a random secret of at least 16 characters, preferably 32 random bytes) and API extras:

```bash
python -m pip install -e ".[api]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000
# Browse http://127.0.0.1:8000/
# API: /health, /api/audit, /api/chat, /api/audit/logs, /metrics
```

Docker Compose runs the backend on **localhost only**. Set `AUDIT_SECRET_KEY` in your environment (or in a local `.env` file based on `.env.example`), then run `docker compose up --build`. Never commit real secrets.

Audit records are held in process memory and chained using HMAC-SHA256; they do not survive a restart. The PHI regex guard is not comprehensive de-identification, and the development API has no authentication. Do not expose the audit API publicly or submit identifiable clinical data.

## Development and testing

```bash
python -m pip install -e ".[dev]"
export AUDIT_SECRET_KEY="test-only-long-audit-key-not-production"
python -m pytest -q
node --test web/test_codec.mjs  # Node.js 22 recommended
python -m build
```

CI runs Python tests on 3.10–3.13, Python/JavaScript interoperability checks, JavaScript codec tests, and wheel/sdist builds. The `.github/workflows/pages.yml` workflow publishes `web/` to GitHub Pages when Pages is enabled and configured to use GitHub Actions.

## Privacy, compatibility, and license

Browser encode/decode uses Web Crypto locally and does not transmit files to a server. The optional **Run server audit** control sends the entered metrics to the same-origin FastAPI server; it is unavailable on static GitHub Pages. Clipboard access depends on browser permissions. The browser app targets modern Chrome, Firefox, Safari and Edge, with no runtime third-party JavaScript dependencies.

Licensed under [MIT](LICENSE).
