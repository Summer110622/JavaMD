#!/usr/bin/env python3
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
page = repo / "_site" / "index.html"
fragment = repo / "content" / "inheritance.html"

html = page.read_text(encoding="utf-8")
section = fragment.read_text(encoding="utf-8").strip()
start = html.find('<section id="inheritance">')
end = html.find('<section id="exception">', start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate generated inheritance section")

html = html[:start] + section + "\n" + html[end:]
page.write_text(html, encoding="utf-8")

required = (
    "動的ディスパッチ",
    "アップキャスト",
    "ダウンキャスト",
    "ClassCastException",
    "メソッド隠蔽",
    "field hiding",
    "abstract class",
    "interfaceメソッド実装ではpublicが必要",
    "Object はclass階層の頂点",
    "null instanceof",
    "継承よりコンポジション",
)
for text in required:
    if text not in html:
        raise SystemExit(f"Detailed inheritance content missing: {text}")

print("Expanded inheritance guide published into _site/index.html")
