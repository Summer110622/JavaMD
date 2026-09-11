(() => {
  'use strict';

  // Stability-first accelerator: warm only the Java/ECJ runtime.
  // User source is compiled exclusively by the existing explicit Run path.
  let warmupPromise = null;
  let warmupScheduled = false;

  async function warmCompilerRuntime() {
    if (mobileRunQuery.matches) return;
    if (warmupPromise) return warmupPromise;

    warmupPromise = (async () => {
      await initPlayground();
      if (!runInProgress) {
        statusText('Java 17 + ECJ ready · compile on Run', 'ready');
      }
    })().catch(() => {
      // Do not surface background warmup failures as user-facing errors.
      // The normal Run path will retry initialization and report real failures.
      warmupPromise = null;
      if (!runInProgress) updateMobileRunState();
    });

    return warmupPromise;
  }

  function scheduleWarmup() {
    if (warmupScheduled || mobileRunQuery.matches || document.visibilityState === 'hidden') return;
    warmupScheduled = true;
    const start = () => {
      warmupScheduled = false;
      void warmCompilerRuntime();
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(start, { timeout: 1200 });
    } else {
      setTimeout(start, 250);
    }
  }

  if (document.readyState === 'complete') {
    scheduleWarmup();
  } else {
    window.addEventListener('load', scheduleWarmup, { once: true });
  }

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && !warmupPromise) scheduleWarmup();
  });
})();
