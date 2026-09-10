# JavaMD

Javaの基礎からCollection Framework、ラムダ式、Stream API、スレッド・並行処理までを、比較表とコード例で体系的に学べる日本語ドキュメントです。

## 特徴

- 基礎から実務基礎まで参照可能
- 固定サイドバー + 目次検索
- ライト / ダークテーマ
- コード例のコピーボタン
- 右側に初心者向けJava実験場
- モバイル対応

## Java実験場

メインドキュメントの右側に、簡単なJavaコードをその場で試せる実験場を用意しています。

- Powered by CheerpJ 4.3
- 初回実行時にブラウザ内Javaランタイムを遅延ロード
- BeanShell 2.1.1をCheerpJ JVM上で実行して初心者向けJavaスニペットを評価
- `System.out.println`、変数、演算、if / for などの簡単なコード向け
- 実行結果を右側のOutputへ表示
- 実行 / リセット
- `Ctrl + Enter` / `Cmd + Enter` で実行
- 狭い画面ではドキュメント本文の下へ移動

完全なJava IDEや複数ファイルプロジェクト用のコンパイラではなく、学習用の簡易スニペット実行環境です。CheerpJランタイムとBeanShell JARは実行時に外部配信元から読み込みます。

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

メインドキュメント + Java実験場:
https://htmlpreview.github.io/?https://github.com/Summer110622/JavaMD/blob/feature/java-basics-site/index.html

スレッド・並行処理:
https://htmlpreview.github.io/?https://github.com/Summer110622/JavaMD/blob/feature/java-basics-site/threads.html

CheerpJ実験場は `http://` または `https://` で配信されたページ上で利用してください。
