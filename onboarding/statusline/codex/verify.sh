#!/usr/bin/env bash
set -euo pipefail

expected_commit=fc269b66adc37f3c855df222ad80b02733355c46
checkout=${1:-}
if [[ -z "$checkout" ]]; then
  printf 'usage: %s /path/to/clean/codex-checkout\n' "${0##*/}" >&2
  exit 2
fi

checkout=$(cd "$checkout" && pwd)
patch=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/context-model-and-effective.patch
actual_commit=$(git -C "$checkout" rev-parse HEAD)
if [[ "$actual_commit" != "$expected_commit" ]]; then
  printf 'expected Codex commit %s, found %s\n' "$expected_commit" "$actual_commit" >&2
  exit 1
fi
if ! git -C "$checkout" diff --quiet || ! git -C "$checkout" diff --cached --quiet; then
  printf 'Codex checkout must be clean: %s\n' "$checkout" >&2
  exit 1
fi

git -C "$checkout" apply --check "$patch"
git -C "$checkout" apply "$patch"

(
  cd "$checkout/codex-rs"
  cargo fmt -- --check
  cargo test -p codex-tui context_usage_display --lib
  cargo build -p codex-cli --bin codex --release
)

printf 'verified Codex context status patch at %s\n' "$expected_commit"
