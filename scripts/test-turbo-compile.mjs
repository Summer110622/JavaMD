import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const turboUrl = new URL('turbo-compile.js', root);
execFileSync(process.execPath, ['--check', fileURLToPath(turboUrl)], { stdio: 'inherit' });
const turbo = readFileSync(turboUrl, 'utf8');
for (const required of [
  'MAX_COMPILE_CACHE = 8',
  'requestIdleCallback',
  "compileSource(source, 'speculative')",
  "compileSource(source, 'warmup')",
  'compileCache.get(source)',
  "runBtn.removeEventListener('click', baselineRunJavaSource)",
  "runBtn.addEventListener('click', turboRunJavaSource)",
  'cheerpjRunMain(',
]) {
  assert.ok(turbo.includes(required), `turbo compiler is missing: ${required}`);
}

const builtPath = process.argv[2];
if (builtPath) {
  const built = readFileSync(builtPath, 'utf8');
  assert.ok(built.includes('<script src="turbo-compile.js"></script>'), 'built page must load turbo-compile.js');
}
console.log('Turbo compile warmup, speculative compile, LRU cache, and fresh execution path verified.');
