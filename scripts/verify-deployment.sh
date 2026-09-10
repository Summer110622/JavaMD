#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PAGES_URL="${1:?Usage: bash scripts/verify-deployment.sh https://owner.github.io/repository/}"
PAGES_URL="${PAGES_URL%/}/"
EXPECTED_MANIFEST="${2:-$REPO_DIR/_site/vendor/checksums.sha256}"
test -s "$EXPECTED_MANIFEST"
CACHE_KEY="$(git -C "$REPO_DIR" rev-parse HEAD)"
CHECK_DIR="$(mktemp -d)"
trap 'rm -rf -- "$CHECK_DIR"' EXIT
mkdir -p "$CHECK_DIR/vendor"

# Use deploy-pages' complete project URL, including /JavaMD/, and retry CDN propagation.
for asset in index.html threads.html vendor/ecj-3.44.0.jar vendor/playground-runner.jar vendor/checksums.sha256 favicon.svg favicon.ico; do
  curl --fail --location --retry 5 --retry-all-errors \
    --connect-timeout 15 --max-time 120 \
    "${PAGES_URL}${asset}?revision=${CACHE_KEY}" --output "$CHECK_DIR/$asset"
  test -s "$CHECK_DIR/$asset"
done
(cd "$CHECK_DIR" && sha256sum --check "$REPO_DIR/scripts/ecj.sha256")
(cd "$CHECK_DIR" && sha256sum vendor/ecj-3.44.0.jar vendor/playground-runner.jar > expected-checksums.sha256)
cmp "$CHECK_DIR/expected-checksums.sha256" "$CHECK_DIR/vendor/checksums.sha256"
cmp "$EXPECTED_MANIFEST" "$CHECK_DIR/vendor/checksums.sha256"

# CheerpJ reads JAR byte ranges, so HTTP 200 alone is not sufficient.
for asset in vendor/ecj-3.44.0.jar vendor/playground-runner.jar; do
  RANGE_STATUS="$(curl --fail --silent --show-error --location \
    --retry 3 --retry-all-errors --connect-timeout 15 --max-time 120 \
    --range 0-7 --write-out '%{http_code}' \
    "${PAGES_URL}${asset}?revision=${CACHE_KEY}" --output "$CHECK_DIR/range.bin")"
  test "$RANGE_STATUS" = 206
  test "$(wc -c < "$CHECK_DIR/range.bin")" -eq 8
  cmp -n 8 "$CHECK_DIR/$asset" "$CHECK_DIR/range.bin"
done
for asset in index.html threads.html favicon.svg favicon.ico; do
  cmp "$REPO_DIR/$asset" "$CHECK_DIR/$asset"
done
printf 'Verified deployed HTML: %sindex.html and %sthreads.html\n' "$PAGES_URL" "$PAGES_URL"
printf 'Verified deployed ECJ: %svendor/ecj-3.44.0.jar\n' "$PAGES_URL"
printf 'Verified deployed runner against built manifest: %svendor/playground-runner.jar\n' "$PAGES_URL"
printf 'Verified HTTP 206 byte-range access for both JARs.\n'
printf 'Verified deployed favicons: %sfavicon.svg and %sfavicon.ico\n' "$PAGES_URL" "$PAGES_URL"
