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

# Enrich the deployed beginner document with detailed inheritance notes and certification practice links.
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
}</code></pre></div><p><code>Cat</code> は <code>Animal</code> を継承しているため、Animal 側のメソッドやメンバ変数を引き継いで利用できます。</p><h3>extends と implements の違い</h3><div class="tablewrap"><table><thead><tr><th>左側</th><th>右側</th><th>使う語</th><th>意味</th></tr></thead><tbody><tr><td>class</td><td>class</td><td><code>extends</code></td><td>クラスを継承する</td></tr><tr><td>class</td><td>interface</td><td><code>implements</code></td><td>interface の契約を実装する</td></tr><tr><td>interface</td><td>interface</td><td><code>extends</code></td><td>interface を継承する</td></tr></tbody></table></div><div class="callout"><strong>検定で重要:</strong> class → interface は <code>implements</code>、interface → interface は <code>extends</code> と判定します。</div><h3>オーバーライド</h3><p>サブクラスでは、スーパークラスから引き継いだメソッドを同じシグネチャで定義し直し、動作を変更できます。</p><div class="code"><div class="codehead"><span>override</span><button class="copy">コピー</button></div><pre><code>class Cat extends Animal {
    @Override
    void speak() {
        System.out.println("meow");
    }
}</code></pre></div><p>また、スーパークラス側のメソッドが <code>abstract</code> なら、具象サブクラスはそのメソッドを実装する必要があります。実装しない場合、そのサブクラス自身も抽象クラスとして宣言する必要があります。</p><h3>super とコンストラクタ</h3><p><code>super</code> はスーパークラスを指します。サブクラスのコンストラクタからスーパークラスのコンストラクタを呼ぶときは <code>super(...)</code> を使います。</p><div class="code"><div class="codehead"><span>super(...)</span><button class="copy">コピー</button></div><pre><code>class Animal {
    String name;
    Animal(String name) {
        this.name = name;
    }
}

class Cat extends Animal {
    Cat(String name) {
        super(name);
    }
}</code></pre></div><div class="callout warn"><strong>試験でよく出る点:</strong> サブクラスにコンストラクタを書かなければデフォルトコンストラクタが作られ、その中では暗黙に <code>super()</code> が呼ばれます。スーパークラスに引数なしコンストラクタが存在しない場合はコンパイルエラーになります。</div><h3>サブクラスをスーパークラス型で扱う</h3><div class="code"><div class="codehead"><span>アップキャスト</span><button class="copy">コピー</button></div><pre><code>Cat cat = new Cat("Mii");
Animal animal = cat;   // 明示的キャスト不要
animal.speak();</code></pre></div><p>サブクラス型のオブジェクト参照は、スーパークラス型の変数へ明示的なキャストなしで代入できます。</p><h3>interface の実装も継承される</h3><div class="code"><div class="codehead"><span>間接的なinterface実装</span><button class="copy">コピー</button></div><pre><code>interface Runner {
    void run();
}

class Animal implements Runner {
    public void run() {}
}

class Cat extends Animal {
    // implements Runner と書かなくても
    // Animal から実装関係を引き継ぐ
}</code></pre></div><p>スーパークラスがinterfaceを実装している場合、そのサブクラスもその実装関係を間接的に引き継ぎます。</p><h3>abstract と final</h3><div class="tablewrap"><table><thead><tr><th>指定</th><th>意味</th><th>継承との関係</th></tr></thead><tbody><tr><td><code>abstract class</code></td><td>未実装の抽象メソッドを持てる</td><td>サブクラスで実装を完成させる用途</td></tr><tr><td><code>abstract method</code></td><td>処理本体をサブクラスに委ねる</td><td>具象サブクラスではオーバーライドが必要</td></tr><tr><td><code>final class</code></td><td>継承禁止</td><td>サブクラスを作れない</td></tr></tbody></table></div><h3>検定での典型的な引っかけ</h3><div class="steps"><div class="step"><strong>final class を継承できる</strong> → 誤り。final class は継承できません。</div><div class="step"><strong>サブクラスをスーパークラス型へ代入するにはキャストが必要</strong> → 誤り。アップキャストは暗黙に可能です。</div><div class="step"><strong>interface を実装するclassは extends を使う</strong> → 誤り。<code>implements</code> を使います。</div><div class="step"><strong>デフォルトコンストラクタは何も呼ばない</strong> → 誤り。暗黙に <code>super()</code> を呼びます。</div><div class="step"><strong>abstract メソッドを継承した具象クラスが実装しなくてもよい</strong> → 誤り。実装しないならそのクラスもabstractにする必要があります。</div></div><div class="callout good"><strong>覚え方:</strong> 「何を引き継ぐか」「どのコンストラクタが呼ばれるか」「型としてどこまで上に見られるか」の3点で整理すると、継承問題を追いやすくなります。</div></section>'''
inherit_marker = '<section id="exception">'
if inherit_marker not in html:
    raise SystemExit("Could not find inheritance section insertion point")
html = html.replace(inherit_marker, inherit_section + '\n<section id="exception">', 1)

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
