#!/usr/bin/env python3
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

sections = [
    ("deep-jvm", "1", "Java / JVM / JDK", "まずJavaがどう動くかを理解"),
    ("deep-syntax", "2", "変数・型・演算子", "値・参照・評価順序の土台"),
    ("deep-control", "3", "条件分岐・ループ", "if / switch / for / while"),
    ("deep-oop", "4", "クラス・this・static", "オブジェクト指向の基本"),
    ("inheritance", "5", "継承・interface", "extends / implements / super / override"),
    ("deep-exception", "6", "例外・Generics", "安全な失敗処理と型安全"),
    ("deep-collections", "7", "Collection全体", "List / Set / Map / Queueの選び方"),
    ("deep-list", "8", "List", "順序・添字・removeの違い"),
    ("deep-set-map", "9", "Set / Map", "重複・順序・keyの扱い"),
    ("deep-lambda", "10", "ラムダ式", "処理を値として扱う"),
    ("deep-functional", "11", "関数型interface", "Predicate / Function / Consumer / Supplier"),
    ("deep-stream", "12", "Stream API", "filter / map / reduce / 遅延評価"),
    ("deep-datetime", "13", "Date / Time", "日時型と不変オブジェクト"),
    ("deep-files", "14", "Path / Files", "ファイルI/Oの基本"),
    ("deep-thread", "15", "Thread", "並行処理・start / join / synchronized"),
    ("deep-reading", "16", "コード読解手順", "最後に全分野を横断して確認"),
]

missing = [sid for sid, *_ in sections if f'id="{sid}"' not in html]
if missing:
    raise SystemExit("Missing deep-dive sections: " + ", ".join(missing))

# Number each detailed section so the reading order is visible while scrolling.
for sid, num, title, _ in sections:
    pattern = rf'(<section id="{re.escape(sid)}"[^>]*>.*?<h2>)(.*?)(</h2>)'
    match = re.search(pattern, html, flags=re.S)
    if not match:
        raise SystemExit(f"Could not find h2 for {sid}")
    old = match.group(2)
    if not re.match(r'^\d+\.\s', old):
        html = html[:match.start(2)] + f'{num}. {old}' + html[match.end(2):]

# Insert a compact learning path immediately before the detailed guide.
path_cards = []
phases = [
    ("STEP 1 · 基礎", sections[0:3]),
    ("STEP 2 · オブジェクト指向", sections[3:6]),
    ("STEP 3 · データ構造", sections[6:9]),
    ("STEP 4 · 関数型", sections[9:12]),
    ("STEP 5 · 実用API", sections[12:15]),
    ("STEP 6 · 総仕上げ", sections[15:16]),
]
for phase, items in phases:
    links = ''.join(
        f'<a href="#{sid}" style="display:block;margin:4px 0;text-decoration:none"><strong>{num}. {title}</strong><span style="display:block;color:var(--muted);font-size:.82rem">{desc}</span></a>'
        for sid, num, title, desc in items
    )
    path_cards.append(f'<div class="card"><div class="kicker">{phase}</div>{links}</div>')

learning_path = (
    '<section id="learning-order"><div class="kicker">Learning Path</div>'
    '<h2>おすすめ学習順 — 上から進めればOK</h2>'
    '<p>詳説は「基礎 → オブジェクト指向 → Collection → ラムダ/Stream → 実用API → 総合読解」の順に並べています。'
    '途中から復習したい場合は、下の項目から直接移動できます。</p>'
    '<div class="cards">' + ''.join(path_cards) + '</div>'
    '<div class="callout good"><strong>迷ったら:</strong> 1〜9を先に固めてから10のラムダ式へ進むと、関数型interfaceとStreamが理解しやすくなります。</div>'
    '</section>'
)
marker = '<section id="deep-guide">'
if marker not in html:
    raise SystemExit("Could not find deep-guide insertion point")
if 'id="learning-order"' not in html:
    html = html.replace(marker, learning_path + '\n' + marker, 1)

# Add a visible sidebar group in the same order, without overwhelming the existing short reference navigation.
nav_marker = '<div class="group">Practice</div>'
nav = (
    '<div class="group">詳説・学習順</div>'
    '<a href="#learning-order">学習順ガイド</a>'
    '<a href="#deep-jvm">1–3 基礎</a>'
    '<a href="#deep-oop">4–6 OOP・例外</a>'
    '<a href="#deep-collections">7–9 Collection</a>'
    '<a href="#deep-lambda">10–12 ラムダ・Stream</a>'
    '<a href="#deep-datetime">13–15 実用API</a>'
    '<a href="#deep-reading">16 コード読解</a>'
)
if nav_marker not in html:
    raise SystemExit("Could not find Practice navigation marker")
if 'href="#learning-order"' not in html:
    html = html.replace(nav_marker, nav + nav_marker, 1)

path.write_text(html, encoding="utf-8")
print("Organized detailed guide into 6 phases / 16 ordered sections.")
