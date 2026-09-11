#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit("Usage: expand-all-topics.py INDEX_HTML FRAGMENT_HTML")

index_path = Path(sys.argv[1])
fragment_path = Path(sys.argv[2])
html = index_path.read_text(encoding="utf-8")
fragment = fragment_path.read_text(encoding="utf-8").strip()

# Add a single navigation entry for the expanded reference area.
nav_marker = '<a href="#cheat">チートシート</a>'
nav_link = '<a href="#cheat">チートシート</a><a href="#deep-guide">全章詳説</a>'
if '#deep-guide' not in html:
    if nav_marker not in html:
        raise SystemExit("Could not find deep-guide navigation insertion point")
    html = html.replace(nav_marker, nav_link, 1)

# Put the expanded material before certification practice when present,
# otherwise before the footer. This keeps the original concise reference intact.
if 'id="deep-guide"' not in html:
    quiz_marker = '<section id="quiz">'
    footer_marker = '<footer>JavaMD — じゃばる！！</footer>'
    if quiz_marker in html:
        html = html.replace(quiz_marker, fragment + '\n' + quiz_marker, 1)
    elif footer_marker in html:
        html = html.replace(footer_marker, fragment + '\n' + footer_marker, 1)
    else:
        raise SystemExit("Could not find deep-guide insertion point")

required = [
    'id="deep-jvm"', 'id="deep-syntax"', 'id="deep-control"',
    'id="deep-oop"', 'id="deep-exception"', 'id="deep-collections"',
    'id="deep-list"', 'id="deep-set-map"', 'id="deep-lambda"',
    'id="deep-functional"', 'id="deep-stream"', 'id="deep-datetime"',
    'id="deep-thread"', 'effectively final', 'Predicate&lt;T&gt;',
    'Function&lt;T,R&gt;', 'Consumer&lt;T&gt;', 'Supplier&lt;T&gt;',
    'try-with-resources', 'short-circuit', 'synchronized'
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit("Missing expanded documentation markers: " + ", ".join(missing))

index_path.write_text(html, encoding="utf-8")
print("Injected detailed documentation for all beginner topics.")