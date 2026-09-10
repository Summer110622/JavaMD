#!/usr/bin/env python3
"""Validate the exact directory uploaded as the Pages artifact."""

import hashlib
from pathlib import Path
import struct
import sys
import zipfile


repo = Path(__file__).resolve().parent.parent
site = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "_site"
for asset in ("index.html", "threads.html", "README.md", "LICENSE", "favicon.svg", "favicon.ico"):
    path = site / asset
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit(f"Missing or empty Pages asset: {path}")
    if path.read_bytes() != (repo / asset).read_bytes():
        raise SystemExit(f"Pages asset differs from source: {asset}")

expected_digest, jar_name = (repo / "scripts/ecj.sha256").read_text().split()
jar = site / jar_name
if not jar.is_file():
    raise SystemExit(f"Missing compiler in Pages artifact: {jar}")
actual_digest = hashlib.sha256(jar.read_bytes()).hexdigest()
if actual_digest != expected_digest:
    raise SystemExit(f"ECJ checksum mismatch: {actual_digest}")

jars = {
    jar_name: "org/eclipse/jdt/internal/compiler/batch/Main.class",
    "vendor/playground-runner.jar": "javamd/PlaygroundRunner.class",
}
manifest = ""
for name, entry_point in jars.items():
    jar_path = site / name
    if not jar_path.is_file():
        raise SystemExit(f"Missing JAR in Pages artifact: {jar_path}")
    digest = hashlib.sha256(jar_path.read_bytes()).hexdigest()
    manifest += f"{digest}  {name}\n"
    with zipfile.ZipFile(jar_path) as archive:
        damaged = archive.testzip()
        if damaged:
            raise SystemExit(f"Damaged JAR ZIP member: {damaged}")
        if entry_point not in archive.namelist():
            raise SystemExit(f"Entry point missing: {entry_point}")
        classes = [member for member in archive.namelist() if member.endswith(".class")]
        for member in classes:
            header = archive.read(member)[:8]
            magic, _, major = struct.unpack(">IHH", header)
            if magic != 0xCAFEBABE or major > 61:
                raise SystemExit(f"Class incompatible with Java 17: {member} (major {major})")
    print(f"Verified {name}: entry point present; all {len(classes)} classes support Java 17.")

if (site / "vendor/checksums.sha256").read_text() != manifest:
    raise SystemExit("Pages JAR checksum manifest does not match the artifact")
print(f"Pinned ECJ SHA-256: {actual_digest}")
print("Source HTML, README, license, and both favicon formats are present unchanged.")
