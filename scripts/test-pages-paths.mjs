import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';

const root = new URL('../', import.meta.url);
const html = readFileSync(new URL('_site/index.html', root), 'utf8');
// Exercise the deployed loader's actual declarations with different document URLs.
const declarations = ['ECJ_URL', 'ECJ_PATH', 'RUNNER_URL', 'RUNNER_PATH', 'RUNTIME_PATH'].map(name => {
  const declaration = html.match(new RegExp(`\\bconst\\s+${name}\\s*=\\s*[^;]+;`))?.[0];
  assert.ok(declaration, `${name} declaration must be in source HTML`);
  return declaration;
}).join('\n');

const cases = [
  ['https://example.com/', '/vendor/ecj-3.44.0.jar'],
  ['https://example.com/index.html', '/vendor/ecj-3.44.0.jar'],
  ['https://summer110622.github.io/JavaMD/', '/JavaMD/vendor/ecj-3.44.0.jar'],
  ['https://summer110622.github.io/JavaMD/index.html?test=1#playground', '/JavaMD/vendor/ecj-3.44.0.jar'],
  ['http://localhost:8000/JavaMD/', '/JavaMD/vendor/ecj-3.44.0.jar'],
];
for (const [baseURI, expectedPath] of cases) {
  const actual = runInNewContext(
    `${declarations}\n({url: ECJ_URL.href, path: ECJ_PATH, runnerUrl: RUNNER_URL.href, runnerPath: RUNNER_PATH, runtimePath: RUNTIME_PATH})`,
    { URL, document: { baseURI } },
    { timeout: 1000 },
  );
  assert.equal(actual.url, new URL(expectedPath, baseURI).href);
  assert.equal(actual.path, `/app${expectedPath}`);
  const expectedRunnerPath = expectedPath.replace('ecj-3.44.0.jar', 'playground-runner.jar');
  assert.equal(actual.runnerUrl, new URL(expectedRunnerPath, baseURI).href);
  assert.equal(actual.runnerPath, `/app${expectedRunnerPath}`);
  assert.equal(actual.runtimePath, `${actual.path}:${actual.runnerPath}`);
  // CheerpJ /app maps to the origin root, retaining the project-site prefix.
  assert.equal(new URL(actual.path.slice('/app'.length), baseURI).href, actual.url);
  console.log(`${baseURI} → ${actual.path}`);
}

for (const page of ['index.html', 'threads.html']) {
  const source = readFileSync(new URL(`_site/${page}`, root), 'utf8');
  const iconTags = [...source.matchAll(/<link\b[^>]*\brel=["'][^"']*\bicon\b[^"']*["'][^>]*>/gi)];
  assert.ok(iconTags.length, `${page} must declare a favicon`);
  for (const [tag] of iconTags) {
    const href = tag.match(/\bhref=["']([^"']+)["']/i)?.[1];
    assert.ok(href, `${page} icon must have an href`);
    for (const prefix of ['/', '/JavaMD/']) {
      const iconUrl = new URL(href, `https://example.com${prefix}${page}`);
      assert.equal(iconUrl.origin, 'https://example.com');
      assert.ok(iconUrl.pathname.startsWith(prefix), `favicon must retain ${prefix}`);
      const artifactPath = new URL(`_site/${iconUrl.pathname.slice(prefix.length)}`, root);
      assert.ok(readFileSync(fileURLToPath(artifactPath)).length, `missing icon: ${artifactPath}`);
    }
  }
}
console.log('Root and /JavaMD/ compiler, runner, and favicon paths verified.');
