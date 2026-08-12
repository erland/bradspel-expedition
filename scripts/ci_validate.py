#!/usr/bin/env python3
"""CI-oriented integrity validation for Expedition."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REQUIRED_PATHS = (
    "README.md",
    "PROJECT_STATUS.md",
    "CHANGELOG.md",
    "PROJECT_MANIFEST.json",
    "requirements.txt",
    "data",
    "schemas",
    "templates",
    "scripts",
    "tests",
    ".github/workflows/01-validate.yml",
    ".github/workflows/02-build-preview.yml",
    ".github/workflows/03-release.yml",
)

REQUIRED_WORKFLOWS = {
    "01-validate.yml",
    "02-build-preview.yml",
    "03-release.yml",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)
    print(f"ERROR: {message}", file=sys.stderr)


def run(command: list[str], root: Path, label: str, errors: list[str]) -> None:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        fail(errors, f"{label} misslyckades med kod {result.returncode}.")
        if detail:
            print(detail, file=sys.stderr)


def validate_versions(root: Path, errors: list[str]) -> str:
    project = yaml.safe_load((root / "data/project.yaml").read_text(encoding="utf-8"))
    project_version = str(project["project"]["project_version"]).strip()
    if not project_version:
        fail(errors, "data/project.yaml saknar project.project_version.")
    return project_version


def validate_build_config(root: Path, errors: list[str]) -> None:
    project = yaml.safe_load((root / "data/project.yaml").read_text(encoding="utf-8"))
    build = project["build"]
    target_ids = [item["id"] for item in build["targets"]]
    if len(target_ids) != len(set(target_ids)):
        fail(errors, "Duplicerade build target-id:n.")

    step_ids: set[str] = set()
    for step in build["steps"]:
        step_id = step["id"]
        if step_id in step_ids:
            fail(errors, f"Duplicerat buildsteg: {step_id}")
        step_ids.add(step_id)

        if step["target"] not in target_ids:
            fail(errors, f"Buildsteg {step_id} hänvisar till okänt target {step['target']}.")

        script = root / step["script"]
        if step.get("enabled", True) and not script.is_file():
            fail(errors, f"Buildsteg {step_id} saknar script: {step['script']}")

        for output in step.get("outputs", []):
            if not str(output).startswith("output/"):
                fail(errors, f"Buildsteg {step_id} har output utanför output/: {output}")

        for pattern in step.get("output_globs", []):
            if not str(pattern).startswith("output/"):
                fail(errors, f"Buildsteg {step_id} har output-glob utanför output/: {pattern}")


def validate_workflows(root: Path, errors: list[str]) -> None:
    folder = root / ".github/workflows"
    actual = {p.name for p in folder.glob("*.yml")} if folder.exists() else set()
    missing = REQUIRED_WORKFLOWS - actual
    for name in sorted(missing):
        fail(errors, f"GitHub Actions-workflow saknas: .github/workflows/{name}")


def validate_built_output(root: Path, project_version: str, errors: list[str]) -> None:
    build_manifest_path = root / "output/build-manifest.json"
    if not build_manifest_path.is_file():
        fail(errors, "Buildmanifest saknas efter build.")
        return

    build_manifest = json.loads(build_manifest_path.read_text(encoding="utf-8"))
    if build_manifest.get("status") != "success":
        fail(errors, f"Buildmanifest har status {build_manifest.get('status')!r}.")
    if str(build_manifest.get("project", {}).get("version")) != project_version:
        fail(errors, "Buildmanifestets projektversion matchar inte källversionen.")

    package_manifest_path = root / "output/print-package/PRINT_PACKAGE_MANIFEST.json"
    if not package_manifest_path.is_file():
        fail(errors, "PRINT_PACKAGE_MANIFEST.json saknas.")
        return

    package = json.loads(package_manifest_path.read_text(encoding="utf-8"))
    if str(package.get("version")) != project_version:
        fail(errors, "Printpaketets version matchar inte projektversionen.")

    entries = package.get("files", [])
    if not entries:
        fail(errors, "Printpaketmanifestet innehåller inga printfiler.")

    package_names: set[str] = set()
    for entry in entries:
        source = root / entry["source"]
        package_file = root / entry["package_file"]
        if not source.is_file() or source.stat().st_size == 0:
            fail(errors, f"Printkälla saknas eller är tom: {entry['source']}")
        if not package_file.is_file() or package_file.stat().st_size == 0:
            fail(errors, f"Paketerad printfil saknas eller är tom: {entry['package_file']}")
        name = package_file.name
        if name in package_names:
            fail(errors, f"Duplicerat filnamn i printpaketet: {name}")
        package_names.add(name)

    combined = root / package.get("combined_pdf", "")
    if not combined.is_file() or combined.stat().st_size == 0:
        fail(errors, "Kombinerad printpakets-PDF saknas eller är tom.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--built",
        action="store_true",
        help="Verifiera även genererad build- och printpaketsoutput.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Hoppa över pytest; avsett för efterkontroll när tester redan körts före build.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            fail(errors, f"Obligatorisk projektsökväg saknas: {relative}")

    if errors:
        return 1

    project_version = validate_versions(root, errors)
    validate_build_config(root, errors)
    validate_workflows(root, errors)

    run(
        [sys.executable, "scripts/validate_project.py", "--root", ".", "--strict"],
        root,
        "Strikt YAML/schema-validering",
        errors,
    )
    if not args.skip_tests:
        run(
            [sys.executable, "-m", "pytest", "-q"],
            root,
            "Pytest",
            errors,
        )

    if args.built:
        validate_built_output(root, project_version, errors)

    if errors:
        print(f"\nCI-validering misslyckades: {len(errors)} fel.", file=sys.stderr)
        return 1

    mode = "inklusive genererad printoutput" if args.built else "källor och tester"
    print(f"OK: CI-validering godkänd för v{project_version} ({mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
