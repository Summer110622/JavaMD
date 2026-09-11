#!/usr/bin/env python3
"""Replace the short beginner sections in the built page with detailed guides."""

from pathlib import Path
import re

repo = Path(__file__).resolve().parent.parent
page = repo / "_site" / "index.html"
fragment = repo / "content" / "core-guides.html"

html = page.read_text(encoding="utf-8")
fragments = fragment.read_text(encoding="utf-8")

section_pattern = re.compile(r'<section id="([^"]+)">.*?</section>', re.DOTALL)
sections = {match.group(1): match.group(0) for match in section_pattern.finditer(fragments)}

expected_ids = (
    "overview", "syntax", "control", "oop", "exception", "collections", "list",
    "set", "map", "queue", "lambda", "functional", "stream", "datetime", "thread", "cheat",
)

missing_fragments = [section_id for section_id in expected_ids if section_id not in sections]
if missing_fragments:
    raise SystemExit(f"Detailed guide fragments missing: {', '.join(missing_fragments)}")

for section_id in expected_ids:
    pattern = re.compile(rf'<section id="{re.escape(section_id)}">.*?</section>', re.DOTALL)
    html, count = pattern.subn(sections[section_id], html, count=1)
    if count != 1:
        raise SystemExit(f"Could not replace section: {section_id}")

required_text = (
    "プリミティブ型と参照型",
    "短絡評価",
    "アクセス修飾子",
    "try-with-resources",
    "PECS",
    "equals と hashCode",
    "remove(int) と remove(Object)",
    "NavigableSet",
    "computeIfAbsent と merge",
    "Queue / Deque",
    "effectively final",
    "ターゲット型が必要",
    "プリミティブ特殊化",
    "遅延評価",
    "Optional",
    "DateTimeFormatter",
    "synchronized",
    "コード読解の順番",
)
for text in required_text:
    if text not in html:
        raise SystemExit(f"Detailed Java content missing: {text}")

page.write_text(html, encoding="utf-8")
print(f"Expanded {len(expected_ids)} Java guide sections in _site/index.html")
