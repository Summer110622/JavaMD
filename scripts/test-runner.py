#!/usr/bin/env python3
"""Exercise the built bridge in real Java processes, including captured failures."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile


site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
classpath = os.pathsep.join(str(site / "vendor" / name) for name in (
    "playground-runner.jar", "ecj-3.44.0.jar"))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


with tempfile.TemporaryDirectory(prefix="javamd-runner-") as temporary:
    workspace = Path(temporary)
    sequence = 0

    def run(source, expected_exit, expected_phase, expected_text,
            main_class="Main", launcher="javamd.PlaygroundRunner", extra_classpath=None):
        global sequence
        sequence += 1
        source_file = workspace / "Main.java"
        source_file.write_text(source, encoding="utf-8")
        output_directory = workspace / f"classes-{sequence}"
        log = output_directory / "output.log"
        phase = output_directory / "phase.txt"
        cp = classpath if extra_classpath is None else str(extra_classpath) + os.pathsep + classpath
        result = subprocess.run([
            "java", "-cp", cp, launcher, str(source_file), str(output_directory),
            str(log), str(phase), main_class,
        ], capture_output=True, text=True, timeout=30)
        text = log.read_text(encoding="utf-8") if log.exists() else ""
        require(result.returncode == expected_exit,
                f"Case {sequence}: exit {result.returncode}, expected {expected_exit}: "
                f"{text}\n{result.stderr}")
        require(phase.read_text() == expected_phase,
                f"Case {sequence}: wrong phase: {phase.read_text()}")
        require(expected_text in text,
                f"Case {sequence}: missing {expected_text!r} in {text!r}")
        require(not result.stdout and not result.stderr,
                f"Case {sequence}: output escaped capture: {result.stdout}{result.stderr}")
        print(f"PASS case {sequence}: exit {expected_exit}, phase {expected_phase}")
        return text

    run('''public class Main {
        public static void main(String[] args) {
            System.out.println("Hello, Java!");
            System.out.println("合格！");
            for (int i = 1; i <= 3; i++) System.out.println("count: " + i);
        }
    }''', 0, "run", "Hello, Java!\n合格！\ncount: 1\ncount: 2\ncount: 3\n")

    run('''public class Main {
        public static void main(String[] args) { System.out.println("broken") }
    }''', 1, "compile", "Syntax error")

    run('''public class Main {
        public static void main(String[] args) { throw new IllegalStateException("runtime failure"); }
    }''', 1, "run", "java.lang.IllegalStateException: runtime failure")

    for value in ("first submission", "changed submission"):
        run('public class Main { public static void main(String[] args) { '
            f'System.out.println("{value}");' + ' } }', 0, "run", value)

    run('''public class Main {
        public static void main(String[] args) {
            System.out.print("before exit"); System.err.print(" and stderr"); System.exit(7);
        }
    }''', 7, "run", "before exit and stderr")

    run('''package example;
    public class Main {
        public static void main(String[] args) {
            System.out.println(java.util.List.of("a", "b").stream().toList());
        }
    }''', 0, "run", "[a, b]", main_class="example.Main")

    run('''public class Main {
        public static void main(String[] args) {
            new Thread(() -> {
                try { Thread.sleep(50); } catch (InterruptedException e) { throw new RuntimeException(e); }
                System.out.println("worker completed");
            }).start();
        }
    }''', 0, "run", "worker completed")

    # Reproduce CheerpJ's missing desktop JDK metadata without altering the JAR.
    probe = workspace / "RuntimeProbe.java"
    probe.write_text('''import java.net.URI;
    import java.nio.file.*;
    public class RuntimeProbe {
        public static void main(String[] args) throws Exception {
            FileSystems.getFileSystem(URI.create("jrt:/"));
            Path emptyHome = Files.createTempDirectory(Path.of(args[0]).getParent(), "empty-jre-");
            System.setProperty("java.home", emptyHome.toString());
            javamd.PlaygroundRunner.main(args);
        }
    }''', encoding="utf-8")
    subprocess.run(["javac", "--release", "17", "-cp", classpath, "-d", str(workspace), str(probe)],
                   check=True, capture_output=True, text=True, timeout=30)
    run('''public class Main {
        public static void main(String[] args) {
            System.out.println(java.util.List.of("runtime classes available").get(0));
        }
    }''', 0, "run", "runtime classes available", launcher="RuntimeProbe", extra_classpath=workspace)

    # Match the browser's two-process flow: a persistent compiler followed by
    # repeated fresh runs with no ECJ on the execution classpath.
    split_probe = workspace / "CompileProbe.java"
    split_probe.write_text("""import java.nio.file.*;
    public class CompileProbe {
        public static void main(String[] args) throws Exception {
            var originalOut = System.out;
            var originalErr = System.err;
            for (int i = 0; i < 3; i++) {
                String source = i == 1 ? "invalid java" :
                    "public class Main { static int count; public static void main(String[] args) { " +
                    "System.out.println(++count); } }";
                Files.writeString(Path.of(args[0]), source);
                boolean ok = javamd.PlaygroundRunner.compile(args[0], args[1], args[2]);
                if (ok != (i != 1)) throw new AssertionError("compile/error/recovery failed");
                if (System.out != originalOut || System.err != originalErr)
                    throw new AssertionError("compiler redirected shared output");
            }
        }
    }""", encoding="utf-8")
    subprocess.run(["javac", "--release", "17", "-cp", classpath, "-d", str(workspace), str(split_probe)],
                   check=True, capture_output=True, text=True, timeout=30)
    split_dir = workspace / "split-classes"
    subprocess.run(["java", "-cp", str(workspace) + os.pathsep + classpath, "CompileProbe",
                    str(workspace / "Main.java"), str(split_dir), str(split_dir / "compiler.log")],
                   check=True, capture_output=True, text=True, timeout=30)
    for iteration in range(2):
        log = workspace / f"split-run-{iteration}.log"
        result = subprocess.run(["java", "-cp", str(site / "vendor/playground-runner.jar"),
                                 "javamd.PlaygroundRunner", "--run", str(split_dir), str(log), "Main"],
                                check=True, capture_output=True, text=True, timeout=30)
        require(log.read_text() == "1\n", "cached class leaked static state or failed to run again")
        require(not result.stdout and not result.stderr, "fresh run output escaped capture")
    print("PASS persistent compiler: success/error/recovery, fresh cached-class runs without ECJ")

print("All Java playground bridge checks passed.")
