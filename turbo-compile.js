(() => {
  'use strict';

  const MAX_COMPILE_CACHE = 8;
  const SPECULATIVE_DELAY_MS = 550;
  const compileCache = new Map();
  let apiPromise = null;
  let compileTail = Promise.resolve();
  let speculativeTimer = 0;
  let monacoHooked = false;
  let warmupStarted = false;
  let turboCounter = 0;

  const baselineRunJavaSource = runJavaSource;
  runBtn.removeEventListener('click', baselineRunJavaSource);

  async function getCompilerApi() {
    if (!apiPromise) {
      apiPromise = (async () => {
        const lib = await initPlayground();
        const [Files, Paths, Runner] = await Promise.all([
          lib.java.nio.file.Files,
          lib.java.nio.file.Paths,
          lib.javamd.PlaygroundRunner,
        ]);
        const readText = async path => String(await Files.readString(await Paths.get(path, [])));
        return { Runner, readText };
      })();
    }
    return apiPromise;
  }

  function touchEntry(source, entry) {
    compileCache.delete(source);
    compileCache.set(source, entry);
  }

  function trimCompileCache(keepSource) {
    while (compileCache.size > MAX_COMPILE_CACHE) {
      let removed = false;
      for (const [source, entry] of compileCache) {
        if (source !== keepSource && entry.state === 'done') {
          compileCache.delete(source);
          removed = true;
          break;
        }
      }
      if (!removed) break;
    }
  }

  function cachedCompilation(source) {
    const entry = compileCache.get(source);
    if (!entry) return null;
    touchEntry(source, entry);
    if (entry.state === 'done') {
      return Promise.resolve({ ...entry.result, cacheHit: true, joinedPending: false });
    }
    return entry.promise.then(result => ({ ...result, cacheHit: false, joinedPending: true }));
  }

  function compileSource(source, origin = 'run') {
    const cached = cachedCompilation(source);
    if (cached) return cached;

    const promise = compileTail.then(async () => {
      const { Runner, readText } = await getCompilerApi();
      const compileId = `${Date.now()}-${++turboCounter}`;
      const sourcePath = '/str/Main.java';
      const outDir = `/files/javamd-compile-${compileId}`;
      const compileLog = `${outDir}/compiler.txt`;
      cheerpOSAddStringFile(sourcePath, new TextEncoder().encode(source));
      const started = performance.now();
      const compiled = await Runner.compile(sourcePath, outDir, compileLog);
      let diagnostics = '';
      try {
        diagnostics = await readText(compileLog);
      } catch (_) {
        // Runner always creates this file; keep diagnostics optional if a VM error prevents it.
      }
      return {
        source,
        outDir,
        diagnostics,
        ok: Boolean(compiled),
        compileMs: performance.now() - started,
        origin,
        cacheHit: false,
        joinedPending: false,
      };
    });

    compileTail = promise.then(() => undefined, () => undefined);
    const pending = { state: 'pending', promise, origin };
    compileCache.set(source, pending);
    promise.then(result => {
      if (compileCache.get(source) !== pending) return;
      const done = { state: 'done', result };
      touchEntry(source, done);
      trimCompileCache(source);
    }, () => {
      if (compileCache.get(source) === pending) compileCache.delete(source);
    });
    return promise;
  }

  function scheduleSpeculativeCompile(delay = SPECULATIVE_DELAY_MS) {
    clearTimeout(speculativeTimer);
    if (mobileRunQuery.matches || runInProgress) return;
    speculativeTimer = setTimeout(() => {
      const source = editorValue();
      if (!source.trim() || compileCache.has(source) || runInProgress) return;
      compileSource(source, 'speculative').catch(() => {});
    }, delay);
  }

  async function warmupTurboCompiler() {
    if (warmupStarted || mobileRunQuery.matches) return;
    warmupStarted = true;
    const source = editorValue();
    try {
      await compileSource(source, 'warmup');
      if (!runInProgress && editorValue() === source) {
        statusText('Turbo compiler ready · current source precompiled', 'ready');
      } else {
        scheduleSpeculativeCompile(120);
      }
    } catch (_) {
      // A normal Run will surface initialization errors with the existing error UI.
    }
  }

  async function turboRunJavaSource() {
    if (mobileRunQuery.matches) {
      output.textContent = 'スマホではJavaコードの実行を利用できません。PCから開いて実行してください。';
      return;
    }
    if (runInProgress) return;

    const source = editorValue();
    const totalStarted = performance.now();
    runInProgress = true;
    runBtn.disabled = true;
    output.textContent = 'Turbo compiling Main.java…';

    try {
      statusText('Turbo compile…');
      const waitStarted = performance.now();
      const compilation = await compileSource(source, 'run');
      const compileWaitMs = performance.now() - waitStarted;
      if (!compilation.ok) {
        output.textContent = (compilation.diagnostics || 'コンパイルに失敗しました。') + beginnerHints(source);
        statusText(`Compile error · ${compileWaitMs.toFixed(0)} ms`, 'error');
        return;
      }

      lastCompilation = {
        source,
        outDir: compilation.outDir,
        diagnostics: compilation.diagnostics,
      };

      const pkg = source.match(/^\s*package\s+([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*;/m);
      const mainClass = (pkg ? `${pkg[1]}.` : '') + 'Main';
      const runId = `${Date.now()}-${++turboCounter}`;
      const logPath = `/files/javamd-run-${runId}/output.txt`;
      const { readText } = await getCompilerApi();
      const runStarted = performance.now();
      statusText(compilation.cacheHit ? 'Compile cache hit · Running Main.main()…' : 'Compiled · Running Main.main()…');
      const exitCode = await cheerpjRunMain(
        'javamd.PlaygroundRunner', RUNNER_PATH,
        '--run', compilation.outDir, logPath, mainClass,
      );
      const runMs = performance.now() - runStarted;
      const text = await readText(logPath);
      output.textContent = (compilation.diagnostics ? `${compilation.diagnostics}\n` : '')
        + (text || '(出力なし)')
        + `\n\nProcess finished with exit code ${exitCode}`;

      const totalMs = performance.now() - totalStarted;
      let compileLabel;
      if (compilation.cacheHit) {
        compileLabel = `compile cache ${compileWaitMs.toFixed(0)} ms`;
      } else if (compilation.joinedPending) {
        compileLabel = `compile joined ${compileWaitMs.toFixed(0)} ms`;
      } else {
        compileLabel = `compile ${compilation.compileMs.toFixed(0)} ms`;
      }
      statusText(`Done · ${compileLabel} · run ${runMs.toFixed(0)} ms · total ${totalMs.toFixed(0)} ms`, exitCode === 0 ? 'ready' : 'error');
    } catch (err) {
      let message = String(err?.message || err);
      try {
        if (err?.getMessage) message = String(await err.getMessage());
      } catch (_) {}
      output.textContent = `Error:\n${message}${beginnerHints(source)}`;
      statusText('Compile / Run failed', 'error');
    } finally {
      runInProgress = false;
      runBtn.disabled = mobileRunQuery.matches;
    }
  }

  runJavaSource = turboRunJavaSource;
  runBtn.addEventListener('click', turboRunJavaSource);
  fallback.addEventListener('input', () => scheduleSpeculativeCompile());

  function hookMonaco() {
    if (monacoHooked || !monacoEditor) return false;
    monacoEditor.onDidChangeModelContent(() => scheduleSpeculativeCompile());
    monacoHooked = true;
    return true;
  }

  if (!hookMonaco()) {
    const hookTimer = setInterval(() => {
      if (hookMonaco()) clearInterval(hookTimer);
    }, 200);
    setTimeout(() => clearInterval(hookTimer), 30000);
  }

  const startWarmup = () => warmupTurboCompiler();
  if ('requestIdleCallback' in window) {
    requestIdleCallback(startWarmup, { timeout: 350 });
  } else {
    setTimeout(startWarmup, 120);
  }
})();
