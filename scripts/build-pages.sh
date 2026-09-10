#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SITE_DIR="$REPO_DIR/_site"
ECJ_JAR=ecj-3.44.0.jar
CLASSES_DIR="$(mktemp -d)"
trap 'rm -rf -- "$CLASSES_DIR"' EXIT

rm -rf -- "$SITE_DIR"
mkdir -p "$SITE_DIR/vendor"
for asset in index.html threads.html quiz.html README.md LICENSE favicon.svg favicon.ico; do
  cp "$REPO_DIR/$asset" "$SITE_DIR/$asset"
done
for quiz in "$REPO_DIR"/quiz-batch-*.html; do
  [[ -e "$quiz" ]] || continue
  cp "$quiz" "$SITE_DIR/$(basename "$quiz")"
done

# Add certification practice links to the deployed beginner document.
python3 - "$SITE_DIR/index.html" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
html = path.read_text(encoding="utf-8")
nav_marker = '<a href="#cheat">チートシート</a></nav>'
nav_replacement = '<a href="#cheat">チートシート</a><div class="group">Practice</div><a href="#quiz">検定チェック</a></nav>'
if nav_marker not in html:
    raise SystemExit("Could not find navigation insertion point")
html = html.replace(nav_marker, nav_replacement, 1)

section = '''<section id="quiz"><div class="kicker">Certification Practice</div><h2>17. Java検定チェック</h2><p>Javaプログラミング能力認定試験2級で問われやすい論点を、オリジナル問題で確認できます。答えと解説は最初は隠してあります。</p><div class="cards"><a class="card" href="quiz.html" style="text-decoration:none;color:inherit"><strong>基本15問</strong><p>interface / static / this / Collection / 配列 / Thread など</p></a><a class="card" href="quiz-batch-001.html" style="text-decoration:none;color:inherit"><strong>追加20問</strong><p>コンパイル可否・出力結果・コード読解を中心に確認</p></a></div></section>'''
footer_marker = '<footer>JavaMD — じゃばる！！</footer>'
if footer_marker not in html:
    raise SystemExit("Could not find footer insertion point")
html = html.replace(footer_marker, section + '\n' + footer_marker, 1)
path.write_text(html, encoding="utf-8")
PY

curl --fail --location --retry 3 --retry-all-errors \
  --connect-timeout 15 --max-time 120 \
  "https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.44.0/$ECJ_JAR" \
  --output "$SITE_DIR/vendor/$ECJ_JAR"

(cd "$SITE_DIR" && sha256sum --check "$REPO_DIR/scripts/ecj.sha256")
javac --release 17 -cp "$SITE_DIR/vendor/$ECJ_JAR" \
  -d "$CLASSES_DIR" "$REPO_DIR/src/javamd/PlaygroundRunner.java"
jar --create --file "$SITE_DIR/vendor/playground-runner.jar" \
  --no-manifest --date=2024-01-01T00:00:00Z -C "$CLASSES_DIR" .
(cd "$SITE_DIR" && sha256sum "vendor/$ECJ_JAR" vendor/playground-runner.jar > vendor/checksums.sha256)

python3 "$REPO_DIR/scripts/verify-pages.py" "$SITE_DIR"
