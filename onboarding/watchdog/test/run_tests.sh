#!/usr/bin/env bash
# Hermetic unit tests for cc-watchdog. No real tmux/Slack needed (PATH shims).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PASS=0; FAIL=0

t() { # t <name> <fn>
  local out
  if out=$("$2" 2>&1); then echo "PASS $1"; PASS=$((PASS + 1))
  else echo "FAIL $1"; echo "$out" | sed 's/^/    /'; FAIL=$((FAIL + 1)); fi
}

setup() {
  TMP=$(mktemp -d)
  export CC_WATCHDOG_HOME="$TMP/wd"
  export TMUX_SHIM_DIR="$TMP/tmux"
  export SHIM_LOG_DIR="$TMP/shimlog"
  mkdir -p "$TMUX_SHIM_DIR" "$SHIM_LOG_DIR"
  export PATH="$HERE/shims:$PATH"
  export SLACK_WEBHOOK_URL="http://example.invalid/hook"
  unset WATCHDOG_DRY TMUX_PANE
}

# --- tests appended by later tasks above this line ---

echo "---"
echo "$PASS passed, $FAIL failed"
(( FAIL == 0 ))
