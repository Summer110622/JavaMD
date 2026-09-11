#!/usr/bin/env python3
"""Validate the exact directory uploaded as the Pages artifact."""

import hashlib
from pathlib import Path
import struct
import sys
import zipfile


repo = Path(__file__).resolve().parent.parent
site = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "_site"

# Assets that must be copied byte-for-byte.
for asset in ("threads.html", "quiz.html", "README.md", "LICENSE", "favicon.svg", "favicon.ico"):
    path = site / asset
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit(f"Missing or empty Pages asset: {path}")
    if path.read_bytes() != (repo / asset).read_bytes():
        raise SystemExit(f"Pages asset differs from source: {asset}")

# Every generated quiz batch must be included in the Pages artifact and contain exactly 20 questions.
quiz_batches = sorted(repo.glob("quiz-batch-*.html"))
if not quiz_batches:
    raise SystemExit("No quiz batch files found in repository")
for source in quiz_batches:
    source_text = source.read_text(encoding="utf-8")
    if source_text.count('<div class="q">') != 20:
        raise SystemExit(f"Quiz batch must contain exactly 20 questions: {source.name}")
    deployed = site / source.name
    if not deployed.is_file() or deployed.read_bytes() != source.read_bytes():
        raise SystemExit(f"Missing or altered quiz batch in Pages artifact: {source.name}")

# index.html is intentionally enhanced at build time with the practice section/navigation.
index = site / "index.html"
if not index.is_file() or not index.stat().st_size:
    raise SystemExit("Missing Pages index.html")
index_text = index.read_text(encoding="utf-8")
for required in ('id="quiz"', 'href="quiz.html"', 'href="quiz-batch-001.html"', 'href="quiz-batch-014.html"', 'href="quiz-batch-015.html"', '>検定チェック<'):
    if required not in index_text:
        raise SystemExit(f"Beginner document is missing certification link/content: {required}")

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
print(f"Published quiz pages: quiz.html + {len(quiz_batches)} batch file(s).")
print("Beginner document contains certification practice links.")
