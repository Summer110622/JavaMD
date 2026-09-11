#!/usr/bin/env python3
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

# The page has two layers:
# 1) a compact core reference that should be read top-to-bottom;
# 2) a detailed guide that revisits the same subjects in more depth.
# Keep the numbering systems separate so the reader never has to guess which
# "5" or "10" a sidebar item refers to.
core_sections = [
    ("overview", 1, "Java / JVM / JDK"),
    ("syntax", 2, "基本構文・変数・型"),
    ("control", 3, "if / switch / loop"),
    ("oop", 4, "クラス・interface"),
    ("inheritance", 5, "継承を詳しく"),
    ("exception", 6, "例外・Generics"),
    ("collections", 7, "Collection全体像"),
    ("list", 8, "List"),
    ("set", 9, "Set / TreeSet"),
    ("map", 10, "Map / HashMap"),
    ("queue", 11, "Queue / Deque"),
    ("lambda", 12, "ラムダ式"),
    ("functional", 13, "関数型interface"),
    ("stream", 14, "Stream API"),
    ("datetime", 15, "Date / Time・Files"),
    ("thread", 16, "Thread API"),
    ("cheat", 17, "チートシート"),
    ("quiz", 18, "Java検定チェック"),
]

deep_sections = [
    ("deep-jvm", 1, "Java / JVM / JDK", "Javaがどう動くか"),
    ("deep-syntax", 2, "変数・型・演算子", "値・参照・評価順序"),
    ("deep-control", 3, "条件分岐・ループ", "if / switch / for / while"),
    ("deep-oop", 4, "クラス・this・static", "オブジェクト指向の土台"),
    ("deep-exception", 5, "例外・Generics", "例外処理と型安全"),
    ("deep-collections", 6, "Collection全体", "データ構造の選び方"),
    ("deep-list", 7, "List", "順序・添字・remove"),
    ("deep-set-map", 8, "Set / Map", "重複・順序・key"),
    ("deep-lambda", 9, "ラムダ式", "処理を値として扱う"),
    ("deep-functional", 10, "関数型interface", "Predicate / Function / Consumer / Supplier"),
    ("deep-stream", 11, "Stream API", "filter / map / reduce / 遅延評価"),
    ("deep-datetime", 12, "Date / Time・Path / Files", "日時とファイルI/O"),
    ("deep-thread", 13, "Thread", "start / join / synchronized"),
    ("deep-summary", 14, "コード読解手順", "全分野を横断して確認"),
]

required_ids = [sid for sid, *_ in core_sections + deep_sections] + ["deep-guide"]
missing = [sid for sid in required_ids if f'id="{sid}"' not in html]
if missing:
    raise SystemExit("Missing sections required for site organization: " + ", ".join(missing))


def set_h2_prefix(document: str, sid: str, prefix: str) -> str:
    pattern = rf'(<section id="{re.escape(sid)}"[^>]*>.*?<h2>)(.*?)(</h2>)'
    match = re.search(pattern, document, flags=re.S)
    if not match:
        raise SystemExit(f"Could not find h2 for {sid}")
    title = re.sub(r'^(?:D\d+|\d+)\.\s*', '', match.group(2))
    return document[:match.start(2)] + prefix + title + document[match.end(2):]


# Normalize the compact reference to one continuous 1–18 sequence.
for sid, number, _ in core_sections:
    html = set_h2_prefix(html, sid, f"{number}. ")

# Give the detailed guide its own D1–D14 sequence. This prevents duplicate
# numbers such as a core "12. ラムダ式" and a detailed "12. ...".
for sid, number, *_ in deep_sections:
    html = set_h2_prefix(html, sid, f"D{number}. ")

# Remove previously generated navigation helpers if this script is re-run.
html = re.sub(r'<section id="site-map">.*?</section>\s*', '', html, flags=re.S)
html = re.sub(r'<section id="learning-order">.*?</section>\s*', '', html, flags=re.S)

# A compact map appears before chapter 1 so a first-time reader immediately
# understands where to start and where the detailed material lives.
site_map = '''<section id="site-map"><div class="kicker">Start Here</div><h2>学習マップ — まず基礎編、次に詳説編</h2><p>このページは<strong>基礎編 → 詳説編 → 検定チェック</strong>の3段階です。初めて学ぶ場合は1から順に、復習なら左の目次や下のカードから直接移動してください。</p><div class="cards"><a class="card" href="#overview" style="text-decoration:none;color:inherit"><strong>① 基礎編 1–6</strong><p>Javaの仕組み → 型 → 制御構文 → クラス → 継承 → 例外</p></a><a class="card" href="#collections" style="text-decoration:none;color:inherit"><strong>② 基礎編 7–14</strong><p>Collection → List / Set / Map → ラムダ → 関数型interface → Stream</p></a><a class="card" href="#datetime" style="text-decoration:none;color:inherit"><strong>③ 基礎編 15–17</strong><p>Date / Time・Files → Thread → チートシート</p></a><a class="card" href="#learning-order" style="text-decoration:none;color:inherit"><strong>④ 詳説編 D1–D14</strong><p>基礎編の各テーマを、理由・注意点・コード読解まで掘り下げる</p></a><a class="card" href="#quiz" style="text-decoration:none;color:inherit"><strong>⑤ 検定チェック</strong><p>最後にオリジナル問題で理解度を確認</p></a></div><div class="callout good"><strong>おすすめ:</strong> 初学者は 1 → 18 の基礎編を一周してから、D1 → D14 の詳説編へ進むと迷いにくくなります。</div></section>'''
core_marker = '<section id="overview">'
if core_marker not in html:
    raise SystemExit("Could not find core guide insertion point")
html = html.replace(core_marker, site_map + '\n' + core_marker, 1)

# Build the detailed learning route. Inheritance is already a full core section,
# so STEP 2 points back to #inheritance between D4 and D5 instead of inventing a
# second detailed inheritance section.
phases = [
    ("STEP 1 · Javaの土台", [
        ("deep-jvm", "D1", "Java / JVM / JDK", "実行の仕組み"),
        ("deep-syntax", "D2", "変数・型・演算子", "値と参照"),
        ("deep-control", "D3", "条件分岐・ループ", "評価順序"),
    ]),
    ("STEP 2 · オブジェクト指向", [
        ("deep-oop", "D4", "クラス・this・static", "クラス設計の基本"),
        ("inheritance", "5", "継承・interface", "extends / super / override"),
        ("deep-exception", "D5", "例外・Generics", "失敗処理と型安全"),
    ]),
    ("STEP 3 · データ構造", [
        ("deep-collections", "D6", "Collection全体", "まず使い分け"),
        ("deep-list", "D7", "List", "順序と添字"),
        ("deep-set-map", "D8", "Set / Map", "重複・key・順序"),
    ]),
    ("STEP 4 · 関数型", [
        ("deep-lambda", "D9", "ラムダ式", "構文と型推論"),
        ("deep-functional", "D10", "関数型interface", "4つの基本型"),
        ("deep-stream", "D11", "Stream API", "処理パイプライン"),
    ]),
    ("STEP 5 · 実用API", [
        ("deep-datetime", "D12", "Date / Time・Files", "日時とI/O"),
        ("deep-thread", "D13", "Thread", "並行処理の基本"),
    ]),
    ("STEP 6 · 総仕上げ", [
        ("deep-summary", "D14", "コード読解手順", "全分野を横断"),
        ("quiz", "18", "検定チェック", "問題で確認"),
    ]),
]

phase_cards = []
for phase, items in phases:
    links = ''.join(
        f'<a href="#{sid}" style="display:block;margin:6px 0;text-decoration:none"><strong>{label}. {title}</strong><span style="display:block;color:var(--muted);font-size:.82rem">{desc}</span></a>'
        for sid, label, title, desc in items
    )
    phase_cards.append(f'<div class="card"><div class="kicker">{phase}</div>{links}</div>')

learning_path = (
    '<section id="learning-order"><div class="kicker">Detailed Learning Path</div>'
    '<h2>詳説編の学習順 — D1からD14へ</h2>'
    '<p>詳説編では「Javaの土台 → オブジェクト指向 → データ構造 → 関数型 → 実用API → 総合読解」の順に進みます。'
    '継承は基礎編5がすでに詳細なので、その章へ戻る導線を入れています。</p>'
    '<div class="cards">' + ''.join(phase_cards) + '</div>'
    '<div class="callout"><strong>ラムダ式の前提:</strong> 型・クラス・Generics・Collectionを先に理解してからD9へ進むと、関数型interfaceとStreamまで一続きで理解できます。</div>'
    '</section>'
)

deep_marker = '<section id="deep-guide">'
if deep_marker not in html:
    raise SystemExit("Could not find deep-guide insertion point")
html = html.replace(deep_marker, learning_path + '\n' + deep_marker, 1)

# Replace the entire sidebar navigation with one consistent information
# architecture. The compact chapters are complete and sequential; the detailed
# guide is grouped by learning phase so the sidebar stays scannable.
nav = '''<nav id="nav"><div class="group">はじめに</div><a href="#site-map">学習マップ</a><div class="group">基礎・OOP · 1–6</div><a href="#overview">1. Java / JVM / JDK</a><a href="#syntax">2. 基本構文・型</a><a href="#control">3. 条件分岐・ループ</a><a href="#oop">4. クラス・interface</a><a href="#inheritance">5. 継承を詳しく</a><a href="#exception">6. 例外・Generics</a><div class="group">Collection · 7–11</div><a href="#collections">7. Collection全体像</a><a href="#list">8. List</a><a href="#set">9. Set / TreeSet</a><a href="#map">10. Map / HashMap</a><a href="#queue">11. Queue / Deque</a><div class="group">関数型 · 12–14</div><a href="#lambda">12. ラムダ式</a><a href="#functional">13. 関数型interface</a><a href="#stream">14. Stream API</a><div class="group">実用・参照 · 15–17</div><a href="#datetime">15. Date / Time・Files</a><a href="#thread">16. Thread API</a><a href="#cheat">17. チートシート</a><div class="group">詳説編</div><a href="#learning-order">詳説の学習順</a><a href="#deep-jvm">D1–D3 Javaの土台</a><a href="#deep-oop">D4–D5 OOP・例外</a><a href="#deep-collections">D6–D8 データ構造</a><a href="#deep-lambda">D9–D11 ラムダ・Stream</a><a href="#deep-datetime">D12–D13 実用API</a><a href="#deep-summary">D14 コード読解</a><div class="group">演習</div><a href="#quiz">18. Java検定チェック</a></nav>'''
nav_pattern = r'<nav id="nav">.*?</nav>'
if not re.search(nav_pattern, html, flags=re.S):
    raise SystemExit("Could not find sidebar navigation")
html = re.sub(nav_pattern, nav, html, count=1, flags=re.S)

# Sanity checks: duplicate IDs make navigation unpredictable, and every href in
# the generated sidebar must resolve to an existing section/helper.
ids = re.findall(r'\bid="([^"]+)"', html)
duplicates = sorted({item for item in ids if ids.count(item) > 1})
if duplicates:
    raise SystemExit("Duplicate HTML ids after organization: " + ", ".join(duplicates))

nav_match = re.search(nav_pattern, html, flags=re.S)
nav_targets = re.findall(r'href="#([^"]+)"', nav_match.group(0))
missing_targets = [target for target in nav_targets if f'id="{target}"' not in html]
if missing_targets:
    raise SystemExit("Sidebar targets missing from generated page: " + ", ".join(missing_targets))

path.write_text(html, encoding="utf-8")
print("Organized JavaMD: 18 core chapters, D1-D14 detailed guide, 6 learning phases, unified sidebar.")
