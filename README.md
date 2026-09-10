# JavaMD
　
Javaの基礎からCollection Framework、ラムダ式、Stream API、スレッド・並行処理までを、比較表とコード例で体系的に学べる日本語ドキュメントです。

## 特徴

- 基礎から実務基礎まで参照可能
- 固定サイドバー + 目次検索
- ライト / ダークテーマ
- コード例のコピーボタン
- 右側に初心者向けJava実験場
- 実験場の横幅をドラッグで変更可能
- Monaco EditorによるJava補完
- モバイル対応

## Java実験場

メインドキュメントの右側に、`Main.java` をそのまま書いてコンパイル・実行できる実験場を用意しています。

- Powered by CheerpJ 4.3
- Java 17ランタイムをブラウザ内で起動
- Eclipse Java Compiler (ECJ) 3.44.0で `Main.java` をコンパイル
- コンパイル成功後に `Main.main(String[] args)` を実行
- `public class Main { ... }` の完全なクラス形式に対応
- import、メソッド、if / for、Collection、ラムダ式、Threadなど通常のJavaコードを記述可能
- コンパイルエラーと実行結果をOutputへ表示
- `pubric` など初心者によくあるタイプミスには追加ヒントを表示
- `Ctrl + Enter` / `Cmd + Enter` で実行
- Monaco Editorの文脈補完
- 実験場の左端をドラッグして320〜900pxで横幅変更、幅はブラウザに保存

初回実行時はCheerpJランタイムとECJ JARを読み込むため、その後の実行より時間がかかります。複数ファイル・Maven/Gradle依存関係を扱う完全なIDEではなく、単一の `Main.java` を学習用途でコンパイル・実行する環境です。

### 実行例

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");

        for (int i = 1; i <= 3; i++) {
            System.out.println(i);
        }
    }
}
```

## 内容

### Java / Language

- Java / JVM / JDK
- コンパイルと実行
- 変数、プリミティブ型、参照型、null、var、final、キャスト
- String / Wrapper / equals
- 演算子、if、switch、for、while
- class / constructor / record / enum
- 継承 / interface
- 例外処理
- Generics

### Collection Framework

- Collection / Map の全体像と選び方
- ArrayList / LinkedList
- HashSet / LinkedHashSet / TreeSet
- HashMap / LinkedHashMap / TreeMap
- Queue / Deque / ArrayDeque / PriorityQueue
- 主要実装の計算量比較

### Lambda / Functional / Stream

- ラムダ式
- メソッド参照
- Predicate / Function / Consumer / Supplier
- UnaryOperator / BinaryOperator
- Stream API
- filter / map / flatMap / sorted / reduce / collect
- Collectors.groupingBy

### Threads / Concurrency

メインページには初心者向けThread APIを掲載し、詳細版は `threads.html` に分離しています。

初心者向け:

- Thread / Runnable
- start / run の違い
- sleep / join
- getName / setName / currentThread
- 2スレッドを動かす基本例

詳細版:

- race condition / atomicity / visibility
- synchronized / volatile
- ReentrantLock / AtomicInteger
- ExecutorService / Future / CompletableFuture
- ConcurrentHashMap / BlockingQueue
- Virtual Threads
- interrupt / deadlock

### Practical

- java.time
- Files / NIO.2
- 用途別チートシート

## 公開サイトとローカル確認

- [JavaMD / Java実験場](https://summer110622.github.io/JavaMD/)
- [スレッド・並行処理](https://summer110622.github.io/JavaMD/threads.html)

Pages の Source は **GitHub Actions** を使用します。ワークフローは `main` の更新時に公開し、PR では同じ公開物のビルドと検証だけを行います。

```sh
bash scripts/build-pages.sh
npx --yes http-server _site -p 8000 -c-1
```

`http://localhost:8000/` を開いて Run を押すと、`Main.java` をコンパイルして実行できます。
ビルドには JDK 17、Bash、curl、Python 3、Node.js が必要です。ローカル配信には HTTP Range 対応のサーバーを使います（上の例は `http-server`）。初回実行には CheerpJ と Monaco の CDN への接続も必要です。
HTML 単体の htmlpreview や `file://` では、同梱した JAR を同一サイトから読み込めないため、Java実験場の実行確認には上記の公開サイトかビルド済み `_site` を使ってください。

### ECJ の配信パス

ECJ 3.44.0 はビルド時に取得し、SHA-256 とコンパイラーのクラスを検証して `_site/vendor/ecj-3.44.0.jar` に配置します。公開する HTML はリポジトリのソースと同一で、ビルド時の文字列置換は行いません。

| 用途 | パス |
| --- | --- |
| Pages 公開物内 | `vendor/ecj-3.44.0.jar` |
| 公開 URL | `https://summer110622.github.io/JavaMD/vendor/ecj-3.44.0.jar` |
| CheerpJ クラスパス | `/app/JavaMD/vendor/ecj-3.44.0.jar` |

[CheerpJ の `/app/` はオリジンのルートに対応](https://cheerpj.com/docs/explanation/File-System-support#app-mount-point)するため、プロジェクトサイトの `/JavaMD/` を含める必要があります。ページの URL からこのパスを組み立てることで、ローカルのルート配信と Pages のプロジェクト配信の両方に対応します。

PR #6 時点でも JAR は公開物に含まれていましたが、`/app/vendor/...` が `/JavaMD/` を省略し、サイト直下を読み込んで 404 になっていました。`ClassNotFoundException: org.eclipse.jdt.internal.compiler.batch.Main` が出る場合は、まず上記の JAR URL と Pages ワークフローの検証結果を確認してください。

favicon は `index.html` と `threads.html` の両方から相対 URL で読み込み、プロジェクトサイト内の `favicon.svg` / `favicon.ico` を配信します。

### CheerpJ と ECJ の Java 17 互換処理

`vendor/playground-runner.jar` は `src/javamd/PlaygroundRunner.java` からビルドします。CheerpJ 4.3 の Java 17 にはデスクトップ JDK の `release` と `lib/jrt-fs.jar` がありません。補助処理は、固定した ECJ 3.44.0 の内部キャッシュに現在の `jrt:/` ファイルシステムを設定し、CheerpJ が実際に提供する Java 17 の標準クラスでコンパイルします。ECJ 本体の JAR は変更しません。ECJ を更新する場合は、この互換処理と実ブラウザーでの実行を再検証してください。

`cheerpjRunMain` は毎回別の Java 実行環境を作るため、出力の取得もその実行環境内で行います。補助処理は ECJ でコンパイルしたクラスの `main(String[] args)` を呼び出し、標準出力・標準エラーを `/files/` 内に記録して Output に表示します。コンパイルエラー、例外、`System.exit()` の終了コードも表示します。
