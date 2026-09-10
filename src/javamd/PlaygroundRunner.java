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
    private PlaygroundRunner() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            throw new IllegalArgumentException(
                "Expected sourcePath, outputDirectory, logPath, phasePath, mainClass");
        }

        Path outputDirectory = Path.of(args[1]);
        Files.createDirectories(outputDirectory);

        // A library-mode System object belongs to a different CheerpJ process.
        // Capture here, where both compilation and the user's main actually run.
        PrintStream capture = new PrintStream(
            new FileOutputStream(args[2]), true, StandardCharsets.UTF_8);
        System.setOut(capture);
        System.setErr(capture);

        try {
            Path phasePath = Path.of(args[3]);
            Files.writeString(phasePath, "compile", StandardCharsets.UTF_8);
            configureCurrentRuntime();

            PrintWriter diagnostics = new PrintWriter(capture, true, StandardCharsets.UTF_8);
            boolean compiled = org.eclipse.jdt.internal.compiler.batch.Main.compile(
                new String[] {
                    "-17", "-proc:none", "-encoding", "UTF-8",
                    "-d", outputDirectory.toString(), args[0]
                }, diagnostics, diagnostics, null);
            diagnostics.flush();
            if (!compiled) {
                System.exit(1);
                return;
            }

            Files.writeString(phasePath, "run", StandardCharsets.UTF_8);
            URLClassLoader application = new URLClassLoader(
                new URL[] { outputDirectory.toUri().toURL() },
                PlaygroundRunner.class.getClassLoader());
            Thread.currentThread().setContextClassLoader(application);
            Class<?> mainClass = application.loadClass(args[4]);
            mainClass.getMethod("main", String[].class).invoke(null, (Object) new String[0]);

            // Return naturally: non-daemon threads may still need the classloader
            // and output stream. User System.exit(code) also keeps its exit code.
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
