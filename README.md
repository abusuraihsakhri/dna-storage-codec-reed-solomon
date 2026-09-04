# DNA Storage Codec Reed Solomon

> **Domain:** DNA Data Storage & Clinical Decision Support  
> **Standards:** DNA Data Storage Alliance Guidelines, CAP / CLSI / ISO Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

DNA Storage Codec Reed Solomon is a dual-domain platform combining:

1. **DNA Storage Codec Engine** (`dna_storage_codec/`): Fountain Code & Reed-Solomon Base-4 DNA Codec Agent for encoding binary data into DNA sequences with error correction, homopolymer avoidance, and GC content balancing.

2. **Clinical Decision Support System** (`agents/`): Enterprise distributed component platform with PHI outbound protection, HMAC-SHA256 tamper-evident audit trails, and multi-worker consensus evaluation.

3. **Enrichment Suite** (`enrichment.py`): Advanced DNA storage optimization engines including ECC optimization, PCR amplification simulation, and information density metrics.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### DNA Storage Codec (`dna_storage_codec/`)
- **BinaryToBase4CodecAgent**: Primary parameter & integrity auditor
- **HomopolymerRunLimiterAgent**: Critical kinetics & security safeguard
- **ReedSolomonECCGeneratorAgent**: Protocol conformance & anomaly triage
- **DNAStorageCoordinator**: Executive coordinator with air-gapped supervisory intelligence

### Clinical Decision Support (`agents/`)
- **InvariantQCWorker**: Primary mathematical & protocol boundary auditor
- **SafetyEscalationWorker**: Safety boundary, toxicity & emergency interlock
- **ProtocolConformanceWorker**: Spec conformance, anomaly triage & discordance checker
- **SystemSupervisor**: Master distributed component coordinator

### Security & Audit
- **PHIGuard**: Zero-PHI outbound interceptor blocking SSNs, MRNs, phone numbers, emails
- **AuditTrail**: Cryptographic tamper-evident HMAC-SHA256 chained audit logs
- **Path Traversal Protection**: Batch processing validates file paths within project directory

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/dna-storage-codec-reed-solomon.git
cd dna-storage-codec-reed-solomon

# Install dependencies
pip install -e .

# For development (testing)
pip install pytest fastapi uvicorn pydantic
```

---

## 💻 CLI Quickstart & Usage

### 1. Audit Single Task
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 6. DNA Storage Codec CLI
```bash
python -m dna_storage_codec.cli audit --task-id DNA-001 --target TARGET-GEN-01 --primary 29.4 --secondary 15.1
python -m dna_storage_codec.cli batch -i sample.csv -o dna_results.csv
python -m dna_storage_codec.cli serve --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (required, non-empty)
- `--target`: Entity or target identifier (required, non-empty)
- `--primary`: Primary measurement value (must be finite number)
- `--secondary`: Secondary measurement value (must be finite number)
- `--critical`: Emergency escalation flag
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT_ANOMALY)

---

## 🛡️ Security Configuration

### Required Environment Variable
The audit trail requires a secure secret key:

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"

# Set the environment variable
export AUDIT_SECRET_KEY="your-secure-key-here"  # Linux/Mac
set AUDIT_SECRET_KEY=your-secure-key-here        # Windows
```

### Security Features
- **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
- **Path Traversal Protection:** Batch processing validates all file paths remain within project directory
- **Input Validation:** All numeric inputs validated as finite numbers; string inputs sanitized

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
# Set audit key for tests
export AUDIT_SECRET_KEY="test-audit-secret-key-2026-secure"

# Run all tests
pytest -v

# Run specific test modules
pytest tests/test_security.py -v
pytest tests/test_dna_storage_codec.py -v
pytest tests/test_dna_storage_codec_reed_solomon.py -v
pytest tests/test_enrichment.py -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t dna-storage-codec-reed-solomon .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key dna-storage-codec-reed-solomon
```

---

## 📁 Project Structure

```
dna-storage-codec-reed-solomon/
├── agents/                      # Clinical Decision Support System
│   ├── __init__.py
│   ├── api.py                   # FastAPI REST endpoints
│   ├── base.py                  # PHI Guard, Audit Trail, Security
│   ├── learning.py              # Bayesian Calibration Engine
│   ├── llm_factory.py           # LLM Provider Factory
│   ├── metrics.py               # Prometheus Metrics Collector
│   ├── models.py                # Pydantic Data Models
│   ├── streamer.py              # WebSocket Telemetry Streamer
│   ├── supervisor.py            # Master Orchestrator
│   └── workers.py               # Specialized Domain Workers
├── dna_storage_codec/           # DNA Storage Codec Engine
│   ├── __init__.py
│   ├── agents.py                # DNA Codec Sub-Agents
│   ├── cli.py                   # DNA Codec CLI
│   ├── engine.py                # Core Algorithmic Engine
│   ├── models.py                # DNA Codec Data Models
│   └── server.py                # DNA Codec FastAPI Server
├── tests/                       # Test Suite
│   ├── test_dna_storage_codec.py
│   ├── test_dna_storage_codec_reed_solomon.py
│   ├── test_enrichment.py
│   └── test_security.py
├── cli.py                       # Main CLI Entry Point
├── enrichment.py                # DNA Storage Enrichment Engines
├── simulator.py                 # High-Throughput Simulator
├── pyproject.toml               # Project Configuration
├── Dockerfile                   # Container Definition
└── docker-compose.yml           # Multi-Container Orchestration
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
