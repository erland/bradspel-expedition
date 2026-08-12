#!/usr/bin/env python3
"""Create the distributable Expedition print release from a verified build."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-version", default="")
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir.resolve()
    project = yaml.safe_load((root / "data/project.yaml").read_text(encoding="utf-8"))
    version = str(project["project"]["project_version"])

    if args.expected_version and args.expected_version != version:
        raise SystemExit(
            f"ERROR: väntad version {args.expected_version}, projektet anger {version}."
        )

    source_dir = root / "output/print-package"
    source_manifest = source_dir / "PRINT_PACKAGE_MANIFEST.json"
    if not source_manifest.is_file():
        raise SystemExit("ERROR: bygg först printpaketet; PRINT_PACKAGE_MANIFEST.json saknas.")

    manifest = json.loads(source_manifest.read_text(encoding="utf-8"))
    if str(manifest.get("version")) != version:
        raise SystemExit("ERROR: printpaketets version matchar inte projektversionen.")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    print_dir = output_dir / "print"
    print_dir.mkdir()

    files: list[dict[str, object]] = []
    package_sources = [source_manifest]
    for entry in manifest.get("files", []):
        package_sources.append(root / entry["package_file"])

    combined = root / manifest["combined_pdf"]
    package_sources.append(combined)

    seen: set[str] = set()
    for source in package_sources:
        if not source.is_file() or source.stat().st_size == 0:
            raise SystemExit(f"ERROR: releasefil saknas eller är tom: {source}")
        if source.name in seen:
            continue
        seen.add(source.name)
        destination = print_dir / source.name
        shutil.copy2(source, destination)
        files.append(
            {
                "path": f"print/{destination.name}",
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    for name in ("README.md", "PROJECT_STATUS.md", "CHANGELOG.md"):
        source = root / name
        if source.is_file():
            shutil.copy2(source, output_dir / name)

    trace_files = {
        "output/build-manifest.json": "BUILD_MANIFEST.json",
        "output/build-report.md": "BUILD_REPORT.md",
    }
    for source_name, destination_name in trace_files.items():
        source = root / source_name
        if not source.is_file():
            raise SystemExit(f"ERROR: buildspårning saknas: {source_name}")
        shutil.copy2(source, output_dir / destination_name)

    release_manifest = {
        "schema_version": 1,
        "project": "Expedition",
        "version": version,
        "purpose": "print-and-play release",
        "recommended_print_format": "PDF",
        "files": sorted(files, key=lambda item: str(item["path"])),
    }
    release_manifest_path = output_dir / "RELEASE_MANIFEST.json"
    release_manifest_path.write_text(
        json.dumps(release_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    zip_path = output_dir / f"expedition-v{version}-print-release.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.relative_to(output_dir))

    print(f"OK: releasepaket skapat: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
