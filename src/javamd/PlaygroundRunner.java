package javamd;

import java.io.FileOutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.net.URI;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

/** Compiles and runs one editor submission inside a fresh CheerpJ process. */
public final class PlaygroundRunner {
    private static boolean runtimeConfigured;

    private PlaygroundRunner() {}

    /** Runs in the persistent library JVM, so ECJ's JRT index survives edits. */
    public static synchronized boolean compile(String sourcePath, String outputPath, String logPath)
            throws Exception {
        Path outputDirectory = Path.of(outputPath);
        Files.createDirectories(outputDirectory);
        try (PrintWriter diagnostics = new PrintWriter(
                new FileOutputStream(logPath), true, StandardCharsets.UTF_8)) {
            try {
                // Reflection into ECJ's JRT caches is only needed once per persistent
                // library JVM. Keeping it off the hot path makes speculative/repeated
                // compiles cheaper while preserving the existing Java 17 setup.
                if (!runtimeConfigured) {
                    configureCurrentRuntime();
                    runtimeConfigured = true;
                }
                return org.eclipse.jdt.internal.compiler.batch.Main.compile(
                    new String[] {
                        "-17", "-proc:none", "-encoding", "UTF-8",
                        "-d", outputDirectory.toString(), sourcePath
                    }, diagnostics, diagnostics, null);
            } catch (Throwable failure) {
                failure.printStackTrace(diagnostics);
                return false;
            }
        }
    }

    public static void main(String[] args) throws Exception {
        // Browser compilation happens in library mode. Only user code enters
        // this fresh process, preserving static state, threads and System.exit.
        if (args.length == 4 && args[0].equals("--run")) {
            execute(Path.of(args[1]), args[2], args[3]);
            return;
        }
        if (args.length != 5) {
            throw new IllegalArgumentException(
                "Expected --run, outputDirectory, logPath, mainClass; or sourcePath, "
                + "outputDirectory, logPath, phasePath, mainClass");
        }

        // Keep the standalone compile-and-run entry point for CLI regression checks.
        Path outputDirectory = Path.of(args[1]);
        Files.createDirectories(outputDirectory);
        Path phasePath = Path.of(args[3]);
        Files.writeString(phasePath, "compile", StandardCharsets.UTF_8);
        if (!compile(args[0], args[1], args[2])) {
            System.exit(1);
            return;
        }
        Files.writeString(phasePath, "run", StandardCharsets.UTF_8);
        execute(outputDirectory, args[2], args[4]);
    }

    private static void execute(Path outputDirectory, String logPath, String mainClassName)
            throws Exception {
        Files.createDirectories(Path.of(logPath).toAbsolutePath().getParent());
        PrintStream capture = new PrintStream(
            new FileOutputStream(logPath, true), true, StandardCharsets.UTF_8);
        System.setOut(capture);
        System.setErr(capture);
        try {
            URLClassLoader application = new URLClassLoader(
                new URL[] { outputDirectory.toUri().toURL() },
                PlaygroundRunner.class.getClassLoader());
            Thread.currentThread().setContextClassLoader(application);
            Class<?> mainClass = application.loadClass(mainClassName);
            mainClass.getMethod("main", String[].class).invoke(null, (Object) new String[0]);
            // Return naturally so non-daemon threads can finish and keep printing.
            capture.flush();
        } catch (Throwable failure) {
            while (failure instanceof InvocationTargetException && failure.getCause() != null) {
                failure = failure.getCause();
            }
            failure.printStackTrace(capture);
            capture.flush();
            System.exit(1);
        }
    }

    private static void configureCurrentRuntime() throws Exception {
        Path javaHome = Path.of(System.getProperty("java.home")).toAbsolutePath().normalize();
        if (Files.exists(javaHome.resolve("release"))) {
            return;
        }

        // CheerpJ 4.3 has a working jrt:/ filesystem but omits the desktop JDK's
        // release and lib/jrt-fs.jar files. ECJ 3.44.0 normally reads those files
        // to open another JRT filesystem. Seed its caches with the running JVM
        // instead, preserving Java 17's real standard classes and module data.
        // These private fields are specific to the checksum-pinned ECJ version;
        // upgrading ECJ requires rerunning the browser compilation checks.
        seedCache("org.eclipse.jdt.internal.compiler.util.Jdk", "pathToRelease",
            javaHome, System.getProperty("java.version"));
        seedCache("org.eclipse.jdt.internal.compiler.util.JRTUtil", "JRT_FILE_SYSTEMS",
            javaHome, FileSystems.getFileSystem(URI.create("jrt:/")));
    }

    @SuppressWarnings("unchecked")
    private static void seedCache(String className, String fieldName, Path key, Object value)
            throws ReflectiveOperationException {
        Field field = Class.forName(className).getDeclaredField(fieldName);
        field.setAccessible(true);
        Map<Path, Object> cache = (Map<Path, Object>) field.get(null);
        cache.put(key, value);
    }
}
