#!/usr/bin/env python3
"""Attach the Java Playground turbo compiler to the built Pages document."""

from pathlib import Path
import sys

path = Path(sys.argv[1])
html = path.read_text(encoding="utf-8")
script = '<script src="turbo-compile.js"></script>'
if script not in html:
    marker = '</body></html>'
    if marker not in html:
        raise SystemExit('Could not find JavaMD closing body marker for turbo compiler')
    html = html.replace(marker, script + '\n' + marker, 1)
    path.write_text(html, encoding="utf-8")
