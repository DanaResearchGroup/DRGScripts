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
  export HERDR_SHIM_DIR="$TMP/herdr"
  mkdir -p "$TMUX_SHIM_DIR" "$SHIM_LOG_DIR" "$HERDR_SHIM_DIR"
  export PATH="$HERE/shims:$PATH"
  export SLACK_WEBHOOK_URL="http://example.invalid/hook"
  export CC_WATCHDOG_AGENTS_STATE="$TMP/agents"
  unset WATCHDOG_DRY TMUX_PANE HERDR_ENV HERDR_PANE_ID
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

mk_deadline() { # <pane> <deadline-offset-s> <set-offset-s> <reason> — echoes file path
  local now f
  now=$(date +%s)
  f="$CC_WATCHDOG_HOME/state/$1.deadline"
  mkdir -p "$CC_WATCHDOG_HOME/state"
  {
    echo "pane=$1"
    echo "set=$(( now + $3 ))"
    echo "deadline=$(( now + $2 ))"
    echo "reason=$4"
    echo "transcript=$TMP/transcript.jsonl"
  } > "$f"
  echo "$f"
}

live_busy_pane() { # <pane>
  echo "$1 100" > "$TMUX_SHIM_DIR/panes"
  printf 'working... esc to interrupt\n' > "$TMUX_SHIM_DIR/content-$1"
}

test_wd_not_due_is_noop() {
  setup; src_watchdog; live_busy_pane %1
  local f; f=$(mk_deadline %1 600 -60 "later")
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  [[ -f "$f" ]] && ! grep -q '^notified=' "$f"
}

test_wd_tier1_notifies_once() {
  setup; src_watchdog; live_busy_pane %1
  local f; f=$(mk_deadline %1 -120 -1800 "suite")
  process_deadline "$f"
  grep -q 'deadline MISSED' "$SHIM_LOG_DIR/curl.log" || { echo "no tier1"; return 1; }
  process_deadline "$f"
  (( $(grep -c 'deadline MISSED' "$SHIM_LOG_DIR/curl.log") == 1 )) \
    || { echo "notified twice"; return 1; }
}

test_wd_tier2_injects_after_grace() {
  setup; src_watchdog; live_busy_pane %1
  local f; f=$(mk_deadline %1 $(( -GRACE_MIN * 60 - 60 )) -7200 "suite")
  set_field "$f" notified "$(( $(date +%s) - GRACE_MIN * 60 ))"
  process_deadline "$f"
  grep -q 'Escape' "$TMUX_SHIM_DIR/send-keys.log" || { echo "no Escape"; return 1; }
  grep -q 'Dead-man deadline expired' "$TMUX_SHIM_DIR/send-keys.log" \
    || { echo "no recovery prompt"; return 1; }
  grep -q '^recovered=' "$f" || { echo "no recovered stamp"; return 1; }
  [[ -f "$CC_WATCHDOG_HOME/state/pane-%1.last-recovery" ]] || { echo "no last-recovery"; return 1; }
}

test_wd_backoff_after_recent_recovery() {
  setup; src_watchdog; live_busy_pane %1
  date +%s > "$CC_WATCHDOG_HOME/state/pane-%1.last-recovery"
  local f; f=$(mk_deadline %1 $(( -GRACE_MIN * 60 - 60 )) -7200 "again")
  set_field "$f" notified "$(( $(date +%s) - GRACE_MIN * 60 ))"
  process_deadline "$f"
  [[ ! -f "$TMUX_SHIM_DIR/send-keys.log" ]] || { echo "injected during backoff"; return 1; }
  grep -q 'notify-only backoff' "$SHIM_LOG_DIR/curl.log" || { echo "no backoff notice"; return 1; }
  set_field "$f" recovered "$(( $(date +%s) - GRACE_MIN * 60 - 60 ))"
  process_deadline "$f" || { echo "process_deadline failed on 2nd pass"; return 1; }
  ! grep -q 'RECOVERY FAILED' "$SHIM_LOG_DIR/curl.log" || { echo "false RECOVERY FAILED in backoff mode"; return 1; }
}

test_wd_self_clear_on_progress_and_idle() {
  setup; src_watchdog
  echo "%1 100" > "$TMUX_SHIM_DIR/panes"
  printf '> \n' > "$TMUX_SHIM_DIR/content-%1"   # idle
  local f; f=$(mk_deadline %1 -120 -1800 "done actually")
  touch "$TMP/transcript.jsonl"                  # mtime now > set time
  process_deadline "$f"
  [[ ! -f "$f" ]] || { echo "not cleared"; return 1; }
  [[ -f "$CC_WATCHDOG_HOME/state/archive/%1.deadline" ]] || { echo "not archived"; return 1; }
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "notified on self-clear"; return 1; }
}

test_wd_vanished_pane_notifies_and_archives() {
  setup; src_watchdog
  : > "$TMUX_SHIM_DIR/panes"                     # no panes at all
  local f; f=$(mk_deadline %1 -120 -1800 "gone")
  process_deadline "$f"
  grep -q 'VANISHED' "$SHIM_LOG_DIR/curl.log" || { echo "no vanish notice"; return 1; }
  [[ ! -f "$f" ]] || { echo "not archived"; return 1; }
}

test_wd_phoenix_defers() {
  setup; src_watchdog; live_busy_pane %1
  export CC_WATCHDOG_AGENTS_STATE="$TMP/agents"
  mkdir -p "$TMP/agents"
  touch "$TMP/agents/abc.limit-wait"
  echo "%1" > "$TMP/agents/abc.tmux-pane"
  src_watchdog                                   # re-source to pick up override
  local f; f=$(mk_deadline %1 -120 -1800 "limit")
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "notified despite Phoenix"; return 1; }
  [[ -f "$f" ]] || { echo "file touched"; return 1; }
  grep -q 'DEFER: Phoenix owns' "$CC_WATCHDOG_HOME/log" || { echo "no DEFER log"; return 1; }
}

t wd_not_due_is_noop test_wd_not_due_is_noop
t wd_tier1_notifies_once test_wd_tier1_notifies_once
t wd_tier2_injects_after_grace test_wd_tier2_injects_after_grace
t wd_backoff_after_recent_recovery test_wd_backoff_after_recent_recovery
t wd_self_clear_on_progress_and_idle test_wd_self_clear_on_progress_and_idle
t wd_vanished_pane_notifies_and_archives test_wd_vanished_pane_notifies_and_archives
t wd_phoenix_defers test_wd_phoenix_defers

test_deadman_herdr_pane_key() {
  setup; cd "$TMP"
  HERDR_ENV=1 HERDR_PANE_ID=w1:p3 "$HERE/../cc-deadman" set 30 "melt sim" >/dev/null || return 1
  local f="$CC_WATCHDOG_HOME/state/herdr:w1:p3.deadline"
  [[ -f "$f" ]] || { echo "no herdr deadline file"; return 1; }
  grep -qx 'pane=herdr:w1:p3' "$f" || { echo "bad pane key"; return 1; }
}

test_wd_herdr_vanished_detected() {
  setup; src_watchdog
  herdr_pane w9:p9 idle   # herdr reachable, but lists a DIFFERENT pane
  local f; f=$(mk_deadline herdr:w1:p3 -120 -1800 "gone")
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  grep -q 'VANISHED' "$SHIM_LOG_DIR/curl.log" || { echo "no vanish notice"; return 1; }
  [[ ! -f "$f" ]] || { echo "not archived"; return 1; }
}

herdr_pane() { # <id> <agent_status> — register a live herdr pane in the shim
  printf '{"panes": [{"pane_id": "%s"}]}\n' "$1" > "$HERDR_SHIM_DIR/panes.json"
  printf '{"pane_id": "%s", "agent_status": "%s"}\n' "$1" "$2" > "$HERDR_SHIM_DIR/status-$1.json"
}

test_wd_herdr_status_mapping() {
  setup; src_watchdog
  herdr_pane w1:p3 working
  pane_busy herdr:w1:p3 || { echo "working should be busy"; return 1; }
  ! pane_idle herdr:w1:p3 || { echo "working must not be idle"; return 1; }
  herdr_pane w1:p3 blocked
  ! pane_busy herdr:w1:p3 || { echo "blocked is not busy"; return 1; }
  ! pane_idle herdr:w1:p3 || { echo "blocked must NOT be idle (no self-clear)"; return 1; }
  herdr_pane w1:p3 idle
  pane_idle herdr:w1:p3 || { echo "idle should be idle"; return 1; }
}

test_wd_herdr_tier2_uses_pane_run() {
  setup; src_watchdog
  herdr_pane w1:p3 working
  local f; f=$(mk_deadline herdr:w1:p3 $(( -GRACE_MIN * 60 - 60 )) -7200 "herdr suite")
  set_field "$f" notified "$(( $(date +%s) - GRACE_MIN * 60 ))"
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  grep -q 'Dead-man deadline expired' "$HERDR_SHIM_DIR/pane-run.log" || { echo "no pane run"; return 1; }
  [[ ! -f "$TMUX_SHIM_DIR/send-keys.log" ]] || { echo "tmux injection used for herdr pane"; return 1; }
  grep -qx 'recovery_kind=inject' "$f" || { echo "no inject stamp"; return 1; }
}

test_wd_herdr_unreachable_degrades_to_notify() {
  setup; src_watchdog
  # no panes.json / status files: every herdr call fails (external control unavailable)
  local f; f=$(mk_deadline herdr:w1:p3 -120 -1800 "unreachable")
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  ! grep -q 'VANISHED' "$SHIM_LOG_DIR/curl.log" || { echo "false VANISH"; return 1; }
  grep -q 'deadline MISSED' "$SHIM_LOG_DIR/curl.log" || { echo "tier1 did not fire"; return 1; }
  [[ -f "$f" ]] || { echo "deadline archived while unreachable"; return 1; }
}

test_wd_herdr_self_clear_on_idle() {
  setup; src_watchdog
  herdr_pane w1:p3 idle
  local f; f=$(mk_deadline herdr:w1:p3 -120 -1800 "finished")
  touch "$TMP/transcript.jsonl"
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  [[ ! -f "$f" ]] || { echo "not self-cleared"; return 1; }
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "notified on self-clear"; return 1; }
}

test_wd_herdr_phoenix_defers() {
  setup; src_watchdog
  herdr_pane w1:p3 working
  mkdir -p "$CC_WATCHDOG_AGENTS_STATE"
  touch "$CC_WATCHDOG_AGENTS_STATE/abc.limit-wait"
  echo "w1:p3" > "$CC_WATCHDOG_AGENTS_STATE/abc.herdr-pane"
  src_watchdog   # re-source after the state dir exists
  local f; f=$(mk_deadline herdr:w1:p3 -120 -1800 "limit")
  process_deadline "$f" || { echo "process_deadline failed"; return 1; }
  grep -q 'DEFER: Phoenix owns' "$CC_WATCHDOG_HOME/log" || { echo "no DEFER log"; return 1; }
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "notified despite Phoenix"; return 1; }
}

t deadman_herdr_pane_key test_deadman_herdr_pane_key
t wd_herdr_vanished_detected test_wd_herdr_vanished_detected
t wd_herdr_phoenix_defers test_wd_herdr_phoenix_defers
t wd_herdr_status_mapping test_wd_herdr_status_mapping
t wd_herdr_tier2_uses_pane_run test_wd_herdr_tier2_uses_pane_run
t wd_herdr_unreachable_degrades_to_notify test_wd_herdr_unreachable_degrades_to_notify
t wd_herdr_self_clear_on_idle test_wd_herdr_self_clear_on_idle

mk_cc_pane() { # <pane> <fake-claude-pid> — busy CC pane whose transcript lives under fake $HOME
  echo "$1 100" > "$TMUX_SHIM_DIR/panes"
  printf 'working... esc to interrupt\n' > "$TMUX_SHIM_DIR/content-$1"
  echo "shell(100)---claude($2)" > "$TMUX_SHIM_DIR/pstree-100"
}

test_wd_backstop_trips_on_stale_busy_undeclared() {
  setup
  export HOME="$TMP/home"                        # fake HOME for transcript resolution
  src_watchdog
  mk_cc_pane %1 $$                               # real pid → /proc/$$/cwd works
  local munged proj
  munged=$(readlink "/proc/$$/cwd" | sed 's#[/.]#-#g')
  proj="$HOME/.claude/projects/$munged"
  mkdir -p "$proj"
  touch -d '7 hours ago' "$proj/session.jsonl"
  echo "$(( $(date +%s) - 7 * 3600 ))" > "$CC_WATCHDOG_HOME/state/pane-%1.busy-since"
  backstop_scan || { echo "backstop_scan failed"; return 1; }
  grep -q 'BACKSTOP' "$SHIM_LOG_DIR/curl.log" || { echo "no backstop notify"; return 1; }
  backstop_scan || { echo "backstop_scan failed on renotify pass"; return 1; }   # renotify suppression
  (( $(grep -c 'BACKSTOP' "$SHIM_LOG_DIR/curl.log") == 1 )) || { echo "renotified"; return 1; }
}

test_wd_backstop_skips_declared_and_fresh() {
  setup
  export HOME="$TMP/home"
  src_watchdog
  mk_cc_pane %1 $$
  # fresh pane: the scan must enumerate it (creating busy-since — the positive
  # control proving the scan actually ran) yet not trip
  backstop_scan || { echo "backstop_scan failed"; return 1; }
  [[ -f "$CC_WATCHDOG_HOME/state/pane-%1.busy-since" ]] || { echo "pane not enumerated"; return 1; }
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "tripped while fresh"; return 1; }
  # stale busy-since but declared deadline → A-layer owns it, no trip
  echo "$(( $(date +%s) - 7 * 3600 ))" > "$CC_WATCHDOG_HOME/state/pane-%1.busy-since"
  mk_deadline %1 600 -60 "declared" >/dev/null
  backstop_scan || { echo "backstop_scan failed on 2nd pass"; return 1; }
  [[ ! -f "$SHIM_LOG_DIR/curl.log" ]] || { echo "tripped despite declaration"; return 1; }
}

test_wd_backstop_clears_busy_since_on_idle() {
  setup; src_watchdog
  echo "%1 100" > "$TMUX_SHIM_DIR/panes"
  echo "shell(100)---claude(1)" > "$TMUX_SHIM_DIR/pstree-100"
  printf '> \n' > "$TMUX_SHIM_DIR/content-%1"    # idle
  echo "123" > "$CC_WATCHDOG_HOME/state/pane-%1.busy-since"
  backstop_scan || { echo "backstop_scan failed"; return 1; }
  [[ ! -f "$CC_WATCHDOG_HOME/state/pane-%1.busy-since" ]]
}

t wd_backstop_trips_on_stale_busy_undeclared test_wd_backstop_trips_on_stale_busy_undeclared
t wd_backstop_skips_declared_and_fresh test_wd_backstop_skips_declared_and_fresh
t wd_backstop_clears_busy_since_on_idle test_wd_backstop_clears_busy_since_on_idle

test_install_creates_links_and_units() {
  setup
  export HOME="$TMP/home"; mkdir -p "$HOME"
  CC_WATCHDOG_NO_SYSTEMD=1 "$HERE/../install.sh" >/dev/null || return 1
  [[ -L "$HOME/.local/bin/cc-deadman" ]] || { echo "no cc-deadman link"; return 1; }
  [[ -L "$HOME/.local/bin/cc-stall-watchdog.sh" ]] || { echo "no watchdog link"; return 1; }
  [[ -f "$HOME/.config/systemd/user/cc-stall-watchdog.timer" ]] || { echo "no timer unit"; return 1; }
  [[ -f "$HOME/.config/systemd/user/cc-stall-watchdog.service" ]] || { echo "no service unit"; return 1; }
  [[ -f "$HOME/.cc-watchdog/config" ]] || { echo "no config stub"; return 1; }
  # idempotent
  CC_WATCHDOG_NO_SYSTEMD=1 "$HERE/../install.sh" >/dev/null || { echo "second run failed"; return 1; }
}

t install_creates_links_and_units test_install_creates_links_and_units

# --- tests appended by later tasks above this line ---

echo "---"
echo "$PASS passed, $FAIL failed"
(( FAIL == 0 ))
