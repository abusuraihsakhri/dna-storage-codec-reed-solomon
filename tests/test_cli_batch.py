"""CLI regression cases for codecs and batch parsing."""
from pathlib import Path

import pytest

from dna_storage_codec.cli import main as codec_cli
from cli import main as legacy_cli

@pytest.mark.parametrize("data", [b"", b"hello", bytes(range(256)), b"\x00\xff\x81"*100])
def test_codec_cli_round_trip(tmp_path, data):
    original = tmp_path / "data.bin"
    dna = tmp_path / "data.dna"
    recovered = tmp_path / "restored.bin"
    original.write_bytes(data)
    assert codec_cli(["encode", "-i", str(original), "-o", str(dna)]) == 0
    assert dna.read_text().strip("ACGT") == ""
    assert codec_cli(["decode", "-i", str(dna), "-o", str(recovered)]) == 0
    assert recovered.read_bytes() == data

def test_codec_cli_rejects_same_path(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_bytes(b"keep")
    assert codec_cli(["encode", "-i", str(file), "-o", str(file)]) == 1
    assert file.read_bytes() == b"keep"

@pytest.mark.parametrize("main", [codec_cli, legacy_cli])
def test_batch_boolean_flags_false_and_true(tmp_path, monkeypatch, main):
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
                        "ONE,K1,1,1,False,NOMINAL\nTWO,K2,1,1,True,NOMINAL\n")
    assert main(["batch", "-i", "in.csv", "-o", "out.csv"]) == 0
    import csv
    with (tmp_path / "out.csv").open() as handle:
        results = list(csv.DictReader(handle))
    assert results[0].get("overall_urgency", results[0].get("overall_status")) in ("ROUTINE", "NOMINAL_OPTIMAL")
    assert results[1].get("overall_urgency", results[1].get("overall_status")) in ("CRITICAL_STAT_PANIC", "CRITICAL_INTERVENTION_REQUIRED")
    assert main(["batch", "-i", "in.csv", "-o", "in.csv"]) == 1

@pytest.mark.parametrize("main", [codec_cli, legacy_cli])
def test_batch_invalid_flag_fails_without_writing_output(tmp_path, monkeypatch, main):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.csv").write_text("task_id,primary_metric,secondary_metric,is_critical_flag\nA,1,1,maybe\n")
    assert main(["batch", "-i", "in.csv", "-o", "out.csv"]) == 1
    assert not (tmp_path / "out.csv").exists()
