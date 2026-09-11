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

# Enrich the deployed beginner document with inheritance and certification practice entry points.
python3 - "$SITE_DIR/index.html" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
html = path.read_text(encoding="utf-8")

inherit_nav_marker = '<a href="#oop">クラス・継承・interface</a><a href="#exception">例外・Generics</a>'
inherit_nav_replacement = '<a href="#oop">クラス・継承・interface</a><a href="#inheritance">継承を詳しく</a><a href="#exception">例外・Generics</a>'
if inherit_nav_marker not in html:
    raise SystemExit("Could not find inheritance navigation insertion point")
html = html.replace(inherit_nav_marker, inherit_nav_replacement, 1)

inherit_section = '''<section id="inheritance"><div class="kicker">Object Oriented · Inheritance</div><h2>5. 継承を詳しく — extends / super / override</h2><p>継承は、既存クラスのメソッドやメンバ変数を引き継ぎ、その性質を利用しながら新しいクラスを作る仕組みです。継承される側を<strong>スーパークラス</strong>、継承する側を<strong>サブクラス</strong>と呼びます。</p><div class="code"><div class="codehead"><span>基本形</span><button class="copy">コピー</button></div><pre><code>class Animal {
    String name;
    void speak() {
        System.out.println("sound");
    }
}

class Cat extends Animal {
    void meow() {
        System.out.println("meow");
    }
}</code></pre></div><p><code>Cat</code> は <code>Animal</code> を継承しているため、Animal 側のメソッドやメンバ変数を引き継いで利用できます。</p></section>'''
inherit_marker = '<section id="exception">'
if inherit_marker not in html:
    raise SystemExit("Could not find inheritance section insertion point")
html = html.replace(inherit_marker, inherit_section + '\n<section id="exception">', 1)

nav_marker = '<a href="#cheat">チートシート</a></nav>'
nav_replacement = '<a href="#cheat">チートシート</a><div class="group">Practice</div><a href="#quiz">検定チェック</a></nav>'
if nav_marker not in html:
    raise SystemExit("Could not find navigation insertion point")
html = html.replace(nav_marker, nav_replacement, 1)

section = '''<section id="quiz"><div class="kicker">Certification Practice</div><h2>18. Java検定チェック</h2><p>Javaプログラミング能力認定試験2級で問われやすい論点を、オリジナル問題で確認できます。答えと解説は最初は隠してあります。</p><div class="cards"><a class="card" href="quiz.html" style="text-decoration:none;color:inherit"><strong>基本15問</strong><p>interface / static / this / Collection / 配列 / Thread など</p></a><a class="card" href="quiz-batch-001.html" style="text-decoration:none;color:inherit"><strong>追加20問 #1</strong><p>Q16〜Q35 · 基礎論点のコード読解</p></a><a class="card" href="quiz-batch-002.html" style="text-decoration:none;color:inherit"><strong>追加20問 #2</strong><p>Q36〜Q55 · コンパイル可否・出力結果</p></a><a class="card" href="quiz-batch-003.html" style="text-decoration:none;color:inherit"><strong>追加20問 #3</strong><p>Q56〜Q75 · 継承・Collection・Threadを横断</p></a><a class="card" href="quiz-batch-004.html" style="text-decoration:none;color:inherit"><strong>追加20問 #4</strong><p>Q76〜Q95 · 新しいコードトレースとコンパイル判定</p></a><a class="card" href="quiz-batch-005.html" style="text-decoration:none;color:inherit"><strong>追加20問 #5</strong><p>Q96〜Q115 · 継承・Collection・配列・Threadの総合確認</p></a><a class="card" href="quiz-batch-006.html" style="text-decoration:none;color:inherit"><strong>追加20問 #6</strong><p>Q116〜Q135 · 修飾子・初期化順・Mapビュー・Threadを総合確認</p></a><a class="card" href="quiz-batch-007.html" style="text-decoration:none;color:inherit"><strong>追加20問 #7</strong><p>Q136〜Q155 · interface・初期化・Collectionビュー・配列・Threadの総合確認</p></a></div></section>'''
footer_marker = '<footer>JavaMD — じゃばる！！</footer>'
if footer_marker not in html:
    raise SystemExit("Could not find footer insertion point")
html = html.replace(footer_marker, section + '\n' + footer_marker, 1)
path.write_text(html, encoding="utf-8")
PY

# Replace the short generated inheritance section and all core beginner sections with
# maintainable detailed fragments. These scripts also assert required teaching points.
python3 "$REPO_DIR/scripts/expand-inheritance.py"
python3 "$REPO_DIR/scripts/expand-core-guides.py"

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
