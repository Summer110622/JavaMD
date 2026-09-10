# JavaMD

Javaの基礎からCollection Framework、ラムダ式、Stream API、スレッド・並行処理までを、比較表とコード例で体系的に学べる日本語ドキュメントです。

## 特徴

- 基礎から実務基礎まで参照可能
- 固定サイドバー + 目次検索 + 読了進捗
- ライト / ダークテーマ
- コード例のコピーボタン
- モバイル対応
- 外部ライブラリ・ビルド不要

## 内容

### Java / Language

- Java / JVM / JDK / バイトコード / GC
- コンパイルと実行
- 変数、プリミティブ型、参照型、null、var、final、キャスト
- String / StringBuilder / Wrapper / equals
- 演算子、if、switch、for、while
- 配列、メソッド、overload、可変長引数
- class / constructor / static / final
- record / enum
- 継承 / abstract class / interface / polymorphism
- アクセス修飾子 / package / import
- checked / unchecked exception / try-with-resources
- Generics / wildcard / PECS

### Collection Framework

- Collection / Map の全体像と選び方
- ArrayList / LinkedList / Vector
- HashSet / LinkedHashSet / TreeSet / EnumSet
- HashMap / LinkedHashMap / TreeMap / EnumMap / ConcurrentHashMap
- Hashtable の位置づけ
- Queue / Deque / ArrayDeque / PriorityQueue
- Comparable / Comparator / sort
- equals / hashCode とHash系Collectionの関係
- NavigableSet / NavigableMap の範囲検索
- 主要実装の計算量比較

### Lambda / Functional / Stream

- ラムダ式の全構文
- ターゲット型とeffectively final
- メソッド参照 / constructor参照
- Predicate / Function / Consumer / Supplier
- UnaryOperator / BinaryOperator / BiFunction
- 関数合成
- プリミティブ特化型
- Streamの遅延評価
- filter / map / flatMap / distinct / sorted / limit / skip / peek
- forEach / count / min / max / find / match / reduce
- Collectors.groupingBy / partitioningBy / joining / toMap
- parallelStream の注意点
- Optional

### Threads / Concurrency

詳細版は `threads.html` に分離しています。

- Thread / Runnable / start / run / join
- Thread state / lifecycle
- race condition / atomicity / visibility
- synchronized / monitor lock
- volatile
- ReentrantLock / AtomicInteger / LongAdder
- wait / notify / notifyAll
- ExecutorService / thread pool
- Future / CompletableFuture
- ConcurrentHashMap / CopyOnWriteArrayList / BlockingQueue
- Virtual Threads (Java 21)
- interrupt / cooperative cancellation
- deadlock と回避策
- 用途別使い分け

### Practical

- java.time
- Files / NIO.2
- 頻出ミス集
- 用途別チートシート

## プレビュー

メインドキュメント:
https://htmlpreview.github.io/?https://github.com/Summer110622/JavaMD/blob/feature/java-basics-site/index.html

スレッド・並行処理:
https://htmlpreview.github.io/?https://github.com/Summer110622/JavaMD/blob/feature/java-basics-site/threads.html

HTMLファイルを直接ブラウザで開いても表示できます。
