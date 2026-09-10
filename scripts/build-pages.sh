#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SITE_DIR="$REPO_DIR/_site"
ECJ_JAR=ecj-3.44.0.jar
CLASSES_DIR="$(mktemp -d)"
trap 'rm -rf -- "$CLASSES_DIR"' EXIT

# The source HTML is the deployed HTML; no deployment-only loader rewriting.
rm -rf -- "$SITE_DIR"
mkdir -p "$SITE_DIR/vendor"
for asset in index.html threads.html README.md LICENSE favicon.svg favicon.ico; do
  cp "$REPO_DIR/$asset" "$SITE_DIR/$asset"
done

curl --fail --location --retry 3 --retry-all-errors \
  --connect-timeout 15 --max-time 120 \
  "https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.44.0/$ECJ_JAR" \
  --output "$SITE_DIR/vendor/$ECJ_JAR"

# Check the downloaded dependency before passing it to the Java compiler.
(cd "$SITE_DIR" && sha256sum --check "$REPO_DIR/scripts/ecj.sha256")
javac --release 17 -cp "$SITE_DIR/vendor/$ECJ_JAR" \
  -d "$CLASSES_DIR" "$REPO_DIR/src/javamd/PlaygroundRunner.java"
# No generated manifest or changing timestamps: identical class files produce the same JAR.
jar --create --file "$SITE_DIR/vendor/playground-runner.jar" \
  --no-manifest --date=2024-01-01T00:00:00Z -C "$CLASSES_DIR" .
(cd "$SITE_DIR" && sha256sum "vendor/$ECJ_JAR" vendor/playground-runner.jar > vendor/checksums.sha256)

python3 "$REPO_DIR/scripts/verify-pages.py" "$SITE_DIR"
