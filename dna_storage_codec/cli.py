"""
Command-Line Interface for DNA-Storage: Fountain Code & Reed-Solomon Base-4 DNA Codec Agent.
"""
import argparse
import csv
import math
import sys
from pathlib import Path
from .models import FrontierPayload
from .agents import DNAStorageCoordinator
from .codec import CodecError, encode_bytes, decode_bytes

coordinator = DNAStorageCoordinator()


def _parse_bool(value):
    """Accept explicit CSV booleans; never interpret 'False' as truthy."""
    if isinstance(value, bool):
        return value
    token = str(value).strip().lower()
    if token in ("true", "1", "yes"):
        return True
    if token in ("false", "0", "no", ""):
        return False
    raise ValueError(f"invalid boolean flag: {value!r}")


def _inside_directory(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def main(argv=None):
    parser = argparse.ArgumentParser(prog="dna-storage-codec-reed-solomon", description="DNA-Storage: Fountain Code & Reed-Solomon Base-4 DNA Codec Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Actual binary/DNA codec, independent of legacy threshold audits.
    p_encode = subparsers.add_parser("encode", help="Encode a binary file as DNA text")
    p_encode.add_argument("-i", "--input", required=True, help="Input binary file")
    p_encode.add_argument("-o", "--output", required=True, help="Output .dna file")
    p_decode = subparsers.add_parser("decode", help="Decode a DNA text file to binary")
    p_decode.add_argument("-i", "--input", required=True, help="Input .dna file")
    p_decode.add_argument("-o", "--output", required=True, help="Output binary file")

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single task evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="TARGET-GEN-01")
    p_audit.add_argument("--primary", type=float, default=29.4)
    p_audit.add_argument("--secondary", type=float, default=15.1)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command in ("encode", "decode"):
        source = Path(args.input)
        destination = Path(args.output)
        if source.resolve() == destination.resolve():
            print("Error: input and output must be different files", file=sys.stderr)
            return 1
        try:
            if args.command == "encode":
                destination.write_text(encode_bytes(source.read_bytes()), encoding="ascii")
            else:
                destination.write_bytes(decode_bytes(source.read_text(encoding="ascii")))
        except (OSError, UnicodeError, CodecError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(f"{args.command.title()} complete: {destination}")
        return 0

    if args.command == "audit":
        # Input validation
        if not args.task_id or not args.task_id.strip():
            print("Error: --task-id cannot be empty")
            return 1
        if not args.target or not args.target.strip():
            print("Error: --target cannot be empty")
            return 1
        if not isinstance(args.primary, (int, float)) or math.isnan(args.primary) or math.isinf(args.primary):
            print("Error: --primary must be a valid finite number")
            return 1
        if not isinstance(args.secondary, (int, float)) or math.isnan(args.secondary) or math.isinf(args.secondary):
            print("Error: --secondary must be a valid finite number")
            return 1
        payload = FrontierPayload(
            task_id=args.task_id.strip(),
            target_identifier=args.target.strip(),
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = coordinator.process(payload)
        print("=" * 80)
        print(f"  DNA-STORAGE: FOUNTAIN CODE & REED-SOLOMON BASE-4 DNA CODEC AGENT")
        print(f"  Domain: DNA Data Storage | Standard: DNA Data Storage Alliance Guidelines")
        print(f"  Task: {dossier['task_id']} | Status: [{dossier['overall_status']}] | Total Alerts: {dossier['total_alerts']}")
        print("=" * 80)
        for a in dossier["alerts"]:
            print(f"\n  [{a['status']}] from {a['origin_agent']}:")
            print(f"  Summary: {a['summary']}")
            print(f"  Details: {a['technical_details']}")
            print(f"  Action:  {a['actionable_remediation']}")
        print("\n" + "=" * 80)
        return 0

    if args.command == "chat":
        ans = coordinator.query_supervisory_chat(" ".join(args.query))
        print(f"\n[DNAStorageCoordinator]:\n{ans}\n")
        return 0

    if args.command == "batch":
        # Path traversal protection
        input_path = Path(args.input).resolve()
        output_path = Path(args.output).resolve()
        cwd = Path.cwd().resolve()
        if not _inside_directory(input_path, cwd):
            print(f"Error: Input path must be within the project directory: {cwd}")
            return 1
        if not _inside_directory(output_path, cwd):
            print(f"Error: Output path must be within the project directory: {cwd}")
            return 1
        if input_path == output_path:
            print("Error: Input and output CSV paths must be different")
            return 1
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}")
            return 1
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        out_fields = fieldnames + ["overall_status", "total_alerts", "critical_count", "consensus_summary"]
        out_rows = []
        for line_number, r in enumerate(rows, start=2):
            try:
                payload = FrontierPayload(
                task_id=r.get("task_id", "TASK-01"),
                target_identifier=r.get("target_identifier", "TARGET-01"),
                primary_metric=float(r.get("primary_metric", 15.0)),
                secondary_metric=float(r.get("secondary_metric", 5.0)),
                status_descriptor=r.get("status_descriptor", "NOMINAL"),
                is_critical_flag=_parse_bool(r.get("is_critical_flag", False)),
            )
            except (ValueError, TypeError) as exc:
                print(f"Error: invalid CSV row {line_number}: {exc}", file=sys.stderr)
                return 1
            dossier = coordinator.process(payload)
            row_dict = dict(r)
            row_dict["overall_status"] = dossier["overall_status"]
            row_dict["total_alerts"] = dossier["total_alerts"]
            row_dict["critical_count"] = dossier["critical_count"]
            row_dict["consensus_summary"] = dossier["consensus_summary"]
            out_rows.append(row_dict)

        with open(output_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Processed {len(out_rows)} records -> {output_path}")
        return 0

    if args.command == "serve":
        try:
            import uvicorn
            from .server import create_app
            app = create_app()
            if app:
                print(f"Starting DNA-Storage: Fountain Code & Reed-Solomon Base-4 DNA Codec Agent on http://{args.host}:{args.port}")
                uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn'")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
