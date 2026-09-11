import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const turboUrl = new URL('turbo-compile.js', root);
execFileSync(process.execPath, ['--check', fileURLToPath(turboUrl)], { stdio: 'inherit' });
const turbo = readFileSync(turboUrl, 'utf8');

for (const required of [
  'warmCompilerRuntime',
  'initPlayground()',
  'requestIdleCallback',
  "window.addEventListener('load', scheduleWarmup, { once: true })",
  "document.addEventListener('visibilitychange'",
  "Java 17 + ECJ ready · compile on Run",
]) {
  assert.ok(turbo.includes(required), `runtime warmup helper is missing: ${required}`);
}

for (const forbidden of [
  'SPECULATIVE_DELAY_MS',
  "compileSource(source, 'speculative')",
  "compileSource(source, 'warmup')",
  'onDidChangeModelContent',
  'compileCache',
  "runBtn.removeEventListener('click'",
  'runJavaSource =',
  'cheerpjRunMain(',
]) {
  assert.ok(!turbo.includes(forbidden), `stability-first warmup must not contain: ${forbidden}`);
}

const builtPath = process.argv[2];
if (builtPath) {
  const built = readFileSync(builtPath, 'utf8');
  assert.ok(built.includes('<script src="turbo-compile.js"></script>'), 'built page must load turbo-compile.js');
  assert.ok(
    built.includes('if(!lastCompilation||lastCompilation.source!==source)'),
    'Run path must compile only when the exact source differs from the last successful compile',
  );
  assert.ok(
    built.includes('lastCompilation={source,outDir,diagnostics}'),
    'Run path must cache only the exact successful source/output pair',
  );
  assert.ok(built.includes('cheerpjRunMain('), 'user execution must remain on the fresh JVM path');
}

console.log('Stable compiler warmup verified: no speculative user compile; exact-source cache and fresh execution preserved.');
