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

## プレビュー

Main.java実行 + 横幅リサイズ + 補完版:
https://htmlpreview.github.io/?https://raw.githubusercontent.com/Summer110622/JavaMD/feature/playground-resize-autocomplete/index.html

スレッド・並行処理:
https://htmlpreview.github.io/?https://github.com/Summer110622/JavaMD/blob/feature/java-basics-site/threads.html

CheerpJ実験場は `http://` または `https://` で配信されたページ上で利用してください。
