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

test_deadman_set_writes_fields() {
  setup; cd "$TMP"
  TMUX_PANE=%7 "$HERE/../cc-deadman" set 30 "suite run" >/dev/null || return 1
  local f="$CC_WATCHDOG_HOME/state/%7.deadline"
  [[ -f "$f" ]] || { echo "no deadline file"; return 1; }
  grep -qx 'pane=%7' "$f" || { echo "bad pane"; return 1; }
  grep -qx 'reason=suite run' "$f" || { echo "bad reason"; return 1; }
  local s d
  s=$(sed -n 's/^set=//p' "$f"); d=$(sed -n 's/^deadline=//p' "$f")
  (( d - s == 1800 )) || { echo "bad delta: $((d - s))"; return 1; }
}

test_deadman_clear_removes() {
  setup; cd "$TMP"
  TMUX_PANE=%7 "$HERE/../cc-deadman" set 30 "x" >/dev/null || return 1
  TMUX_PANE=%7 "$HERE/../cc-deadman" clear >/dev/null || return 1
  [[ ! -f "$CC_WATCHDOG_HOME/state/%7.deadline" ]]
}

test_deadman_extend_pushes_and_resets_tiers() {
  setup; cd "$TMP"
  TMUX_PANE=%7 "$HERE/../cc-deadman" set 30 "x" >/dev/null
  local f="$CC_WATCHDOG_HOME/state/%7.deadline"
  echo "notified=123" >> "$f"
  local before after
  before=$(sed -n 's/^deadline=//p' "$f")
  TMUX_PANE=%7 "$HERE/../cc-deadman" extend 10 >/dev/null
  after=$(sed -n 's/^deadline=//p' "$f")
  (( after - before == 600 )) || { echo "bad extend"; return 1; }
  ! grep -q '^notified=' "$f" || { echo "notified not reset"; return 1; }
}

test_deadman_pane_from_process_tree() {
  setup; cd "$TMP"
  echo "%9 $$" > "$TMUX_SHIM_DIR/panes"   # this test shell is cc-deadman's ancestor
  "$HERE/../cc-deadman" set 5 "tree" >/dev/null || return 1
  [[ -f "$CC_WATCHDOG_HOME/state/%9.deadline" ]]
}

t deadman_set_writes_fields test_deadman_set_writes_fields
t deadman_clear_removes test_deadman_clear_removes
t deadman_extend_pushes_and_resets_tiers test_deadman_extend_pushes_and_resets_tiers
t deadman_pane_from_process_tree test_deadman_pane_from_process_tree

src_watchdog() { . "$HERE/../cc-stall-watchdog.sh"; }

test_wd_notify_posts_to_slack() {
  setup; src_watchdog
  notify "hello world"
  grep -q "hello world" "$SHIM_LOG_DIR/curl.log" || { echo "no slack post"; return 1; }
}

test_wd_notify_dry_is_log_only() {
  setup; export WATCHDOG_DRY=1; src_watchdog
  notify "quiet"
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "curl called in dry mode"; return 1; }
  grep -q "NOTIFY: quiet" "$CC_WATCHDOG_HOME/log" || { echo "not logged"; return 1; }
}

test_wd_notify_falls_back_without_webhook() {
  setup; unset SLACK_WEBHOOK_URL; src_watchdog
  notify "fallback"
  grep -q "fallback" "$SHIM_LOG_DIR/notify-send.log" || { echo "no notify-send"; return 1; }
}

test_wd_pane_busy_matches_footer() {
  setup; src_watchdog
  echo "%1 100" > "$TMUX_SHIM_DIR/panes"
  printf 'stuff\n... esc to interrupt\n' > "$TMUX_SHIM_DIR/content-%1"
  pane_busy %1 || { echo "should be busy"; return 1; }
  printf '> \n' > "$TMUX_SHIM_DIR/content-%1"
  pane_idle %1 || { echo "should be idle"; return 1; }
}

test_wd_config_overrides_defaults() {
  setup
  mkdir -p "$CC_WATCHDOG_HOME"
  echo "GRACE_MIN=7" > "$CC_WATCHDOG_HOME/config"
  src_watchdog
  (( GRACE_MIN == 7 )) || { echo "GRACE_MIN=$GRACE_MIN"; return 1; }
}

t wd_notify_posts_to_slack test_wd_notify_posts_to_slack
t wd_notify_dry_is_log_only test_wd_notify_dry_is_log_only
t wd_notify_falls_back_without_webhook test_wd_notify_falls_back_without_webhook
t wd_pane_busy_matches_footer test_wd_pane_busy_matches_footer
t wd_config_overrides_defaults test_wd_config_overrides_defaults

# --- tests appended by later tasks above this line ---

echo "---"
echo "$PASS passed, $FAIL failed"
(( FAIL == 0 ))
