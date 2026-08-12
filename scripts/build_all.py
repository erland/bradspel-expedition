#!/usr/bin/env python3
"""Manifest-driven build for the Expedition print-and-play project."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import platform
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(root: Path) -> list[Path]:
    roots = [
        root / "data",
        root / "schemas",
        root / "templates",
        root / "assets",
        root / "scripts",
        root / "docs",
        root / ".github",
    ]
    top_level = [
        root / "README.md",
        root / "PROJECT_STATUS.md",
        root / "CHANGELOG.md",
        root / "PLAN.md",
        root / "requirements.txt",
        root / "PROJECT_MANIFEST.json",
    ]
    files: list[Path] = []
    for folder in roots:
        if folder.exists():
            files.extend(p for p in folder.rglob("*") if p.is_file())
    files.extend(p for p in top_level if p.exists())
    return sorted(set(files))


def clean_outputs(root: Path, paths: list[str]) -> list[str]:
    cleaned: list[str] = []
    for relative in paths:
        target = (root / relative).resolve()
        if root not in target.parents:
            raise ValueError(f"Osäker clean-sökväg utanför projektet: {relative}")
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            cleaned.append(relative)
        target.mkdir(parents=True, exist_ok=True)
    return cleaned


def run_module(script: Path, root: Path, strict: bool = False) -> dict[str, Any]:
    if not script.exists():
        raise FileNotFoundError(f"Buildskript saknas: {script}")

    module_name = f"_build_{script.stem}_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Kunde inte ladda buildskript: {script}")

    module = importlib.util.module_from_spec(spec)
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    old_argv = sys.argv[:]
    argv = [str(script), "--root", str(root)]
    if strict and script.name == "validate_project.py":
        argv.append("--strict")

    started = time.perf_counter()
    status = "success"
    return_code = 0
    error_text = ""

    try:
        sys.argv = argv
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            spec.loader.exec_module(module)
            if not hasattr(module, "main"):
                raise AttributeError(f"{script.name} saknar main().")
            result = module.main()
            if result not in (None, 0):
                return_code = int(result)
                status = "failed"
    except SystemExit as exc:
        return_code = int(exc.code or 0)
        if return_code != 0:
            status = "failed"
    except Exception:
        return_code = 1
        status = "failed"
        error_text = traceback.format_exc()
    finally:
        sys.argv = old_argv

    duration = round(time.perf_counter() - started, 4)
    stderr = stderr_buffer.getvalue()
    if error_text:
        stderr += error_text

    return {
        "status": status,
        "return_code": return_code,
        "duration_seconds": duration,
        "stdout": stdout_buffer.getvalue().strip(),
        "stderr": stderr.strip(),
    }


def verify_step_outputs(root: Path, step: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    empty: list[str] = []
    files: list[dict[str, Any]] = []

    for relative in step.get("outputs", []):
        path = root / relative
        if not path.exists():
            missing.append(relative)
            continue
        if not path.is_file() or path.stat().st_size == 0:
            empty.append(relative)
            continue
        files.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    glob_results: list[dict[str, Any]] = []
    for pattern in step.get("output_globs", []):
        matches = sorted(p for p in root.glob(pattern) if p.is_file())
        expected = step.get("expected_glob_count")
        glob_results.append({
            "pattern": pattern,
            "count": len(matches),
            "expected_count": expected,
        })
        if expected is not None and len(matches) != expected:
            missing.append(f"{pattern} (förväntat antal {expected}, hittat {len(matches)})")
        for path in matches:
            files.append({
                "path": str(path.relative_to(root)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            })

    return {
        "ok": not missing and not empty,
        "missing": missing,
        "empty": empty,
        "files": files,
        "globs": glob_results,
    }


def enabled_target_ids(build: dict[str, Any]) -> set[str]:
    return {item["id"] for item in build["targets"] if item["enabled"]}


def write_report(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Buildrapport",
        "",
        f"- Projekt: **{manifest['project']['name']}**",
        f"- Version: `{manifest['project']['version']}`",
        f"- Buildstatus: **{manifest['status']}**",
        f"- Start: `{manifest['started_at']}`",
        f"- Slut: `{manifest['finished_at']}`",
        f"- Total tid: `{manifest['duration_seconds']}` sekunder",
        f"- Rensade outputsökvägar: `{len(manifest['cleaned_paths'])}`",
        f"- Källfiler: `{len(manifest['sources'])}`",
        f"- Genererade filer: `{len(manifest['outputs'])}`",
        "",
        "## Byggsteg",
        "",
        "| Steg | Mål | Status | Tid (s) | Output |",
        "|---|---|---:|---:|---:|",
    ]
    for step in manifest["steps"]:
        lines.append(
            f"| `{step['id']}` | `{step['target']}` | {step['status']} | "
            f"{step['duration_seconds']} | {len(step['verification']['files'])} |"
        )

    lines.extend(["", "## Genererad print-output", ""])
    pdfs = [item for item in manifest["outputs"] if item["path"].endswith(".pdf")]
    for item in pdfs:
        lines.append(f"- `{item['path']}` ({item['bytes']} byte)")

    lines.extend(["", "## Varningar", ""])
    if manifest["warnings"]:
        lines.extend(f"- {warning}" for warning in manifest["warnings"])
    else:
        lines.append("- Inga.")

    lines.extend(["", "## Fel", ""])
    if manifest["errors"]:
        lines.extend(f"- {error}" for error in manifest["errors"])
    else:
        lines.append("- Inga.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Projektets rotmapp.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Tvinga rensning även om project.yaml inte begär det.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Hoppa över rensning.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Behandla validatorvarningar som fel.",
    )
    parser.add_argument(
        "--target",
        action="append",
        help="Bygg endast valt mål. Kan anges flera gånger.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    project_path = root / "data/project.yaml"
    project_data = load_yaml(project_path)
    build = project_data["build"]
    configured_targets = enabled_target_ids(build)
    selected_targets = set(args.target or configured_targets)
    unknown_targets = selected_targets - {item["id"] for item in build["targets"]}
    if unknown_targets:
        print(f"Okända buildmål: {', '.join(sorted(unknown_targets))}", file=sys.stderr)
        return 2

    started_dt = datetime.now(timezone.utc)
    started_clock = time.perf_counter()
    warnings: list[str] = []
    errors: list[str] = []
    log_lines: list[str] = []

    do_clean = build["clean_generated_before_build"] or args.clean
    if args.no_clean:
        do_clean = False
    cleaned = clean_outputs(root, build["clean_paths"]) if do_clean else []

    source_entries = [
        {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in source_files(root)
    ]

    step_results: list[dict[str, Any]] = []
    all_outputs: dict[str, dict[str, Any]] = {}

    for step in build["steps"]:
        if not step["enabled"] or step["target"] not in selected_targets:
            continue

        print(f"[BUILD] {step['id']} ({step['target']})")
        run_result = run_module(root / step["script"], root, strict=args.strict)
        verification = verify_step_outputs(root, step)

        stdout = run_result["stdout"]
        stderr = run_result["stderr"]
        if stdout:
            print(stdout)
            log_lines.append(f"## {step['id']} stdout\n{stdout}")
        if stderr:
            print(stderr, file=sys.stderr)
            log_lines.append(f"## {step['id']} stderr\n{stderr}")

        warnings.extend(
            line.removeprefix("VARNING:").strip()
            for line in stdout.splitlines()
            if line.startswith("VARNING:")
        )

        status = run_result["status"]
        if status == "success" and not verification["ok"]:
            status = "failed"
            errors.extend(
                [f"{step['id']}: saknad output {item}" for item in verification["missing"]]
                + [f"{step['id']}: tom output {item}" for item in verification["empty"]]
            )
        if run_result["return_code"] != 0:
            errors.append(
                f"{step['id']} misslyckades med kod {run_result['return_code']}."
            )

        result_entry = {
            "id": step["id"],
            "target": step["target"],
            "script": step["script"],
            "status": status,
            "duration_seconds": run_result["duration_seconds"],
            "return_code": run_result["return_code"],
            "verification": verification,
        }
        step_results.append(result_entry)

        for item in verification["files"]:
            all_outputs[item["path"]] = item

        if status == "failed":
            break

    finished_dt = datetime.now(timezone.utc)
    status = "success" if not errors and all(s["status"] == "success" for s in step_results) else "failed"

    manifest = {
        "schema_version": 1,
        "project": {
            "id": project_data["project"]["id"],
            "name": project_data["project"]["name"],
            "version": project_data["project"]["project_version"],
        },
        "status": status,
        "started_at": started_dt.isoformat(),
        "finished_at": finished_dt.isoformat(),
        "duration_seconds": round(time.perf_counter() - started_clock, 4),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "selected_targets": sorted(selected_targets),
        "cleaned_paths": cleaned,
        "sources": source_entries,
        "steps": step_results,
        "outputs": sorted(all_outputs.values(), key=lambda item: item["path"]),
        "warnings": sorted(set(warnings)),
        "errors": errors,
    }

    manifest_path = root / build["manifest_path"]
    report_path = root / build["report_path"]
    log_path = root / build["log_path"]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(report_path, manifest)
    log_path.write_text("\n\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Buildstatus: {status}")
    print(f"Manifest: {manifest_path.relative_to(root)}")
    print(f"Rapport: {report_path.relative_to(root)}")
    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
