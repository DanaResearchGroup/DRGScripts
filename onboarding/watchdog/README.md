# cc-watchdog — dead-man's switch for Claude Code sessions

Long autonomous Claude Code sessions can die out silently: the session waits on
background work (a test suite, a build) whose owner died, and nothing ever wakes
it — it looks exactly like "done, waiting for you". cc-watchdog catches this.

## How it works

1. Before a session goes quiet while waiting on something, it (or you) declares
   a deadline: `cc-deadman set 40 "full test suite, ~25 min"` (expected duration
   + 50% margin).
2. A systemd user timer runs `cc-stall-watchdog.sh` every 5 minutes:
   - Session progressed and is idle again → deadline self-clears.
   - Deadline missed → **Slack ping** (tier 1).
   - Still nothing an hour later (`GRACE_MIN=60`) → the watchdog **nudges the
     session itself** (tier 2): Escape if busy, then a recovery prompt asking it
     to check honest status and continue. Repeat stalls within 24 h back off to
     notify-only — no injection loops.
   - Sessions that never declared: if a pane is mid-turn busy for over
     `BACKSTOP_HOURS=6` h with an equally stale transcript, you get a
     notify-only ping (max once per 12 h). Legitimate long quiet runs (a 2.75 h
     suite) can never trip this.

The watchdog is deliberately timer-driven, not Claude-Code-hook-driven: hook
watchers only wake when a turn ends, which is exactly the blind spot that
produces multi-hour stalls.

## tmux and Herdr

Sessions under **tmux** and under **Herdr** are both supported. Inside a Herdr
pane, `cc-deadman` keys the deadline to `$HERDR_PANE_ID` automatically; the
watchdog then reads Herdr's native `agent_status` (busy = `working`; `blocked`
counts as NOT idle, so a blocked agent still triggers your tier-1 ping) and
injects recovery via `herdr pane run`. If `herdr` refuses commands from the
timer's context, the watchdog degrades gracefully: the pane is assumed alive,
injection is skipped (logged), and the Slack alert still fires. Run the smoke
test below once from inside a Herdr pane to confirm external control works on
your setup. Limitation: the no-declaration backstop scans tmux panes only —
Herdr sessions are covered by declared deadlines.

## Install

    ./install.sh

Then set your Slack incoming webhook in `~/.cc-watchdog/config`:

    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

Optional overrides in the same file: `GRACE_MIN`, `BACKSTOP_HOURS`,
`BACKSTOP_RENOTIFY_HOURS`, `RECOVERY_BACKOFF_HOURS`, `WATCHDOG_DRY=1` (log-only).

## Session-side commands

    cc-deadman set <minutes> "<reason>"   # declare before a long wait
    cc-deadman extend <minutes>           # work is legitimately taking longer
    cc-deadman clear                      # first action after resuming
    cc-deadman list                       # what's armed right now

## Smoke test

1. In a tmux Claude Code session: `cc-deadman set 1 "smoke test"`.
2. Within ~6 min: Slack ping (tier 1).
3. To see tier 2 quickly: `echo GRACE_MIN=2 >> ~/.cc-watchdog/config`, wait
   ~3 more min, watch the recovery prompt land in the pane. Revert the config
   line and `cc-deadman clear` afterwards.

Recommended first deployment: `WATCHDOG_DRY=1` in the config for 2–3 days;
watch `~/.cc-watchdog/log` for what it *would* have done, then remove the flag.

## Unit tests

    test/run_tests.sh   # hermetic; fakes tmux/curl/pstree via PATH shims
