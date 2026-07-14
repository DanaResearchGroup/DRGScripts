#!/usr/bin/env bash
# install.sh — install cc-watchdog: symlinks into ~/.local/bin + systemd user timer.
# Idempotent. CC_WATCHDOG_NO_SYSTEMD=1 skips systemctl (tests/CI).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
BIN="$HOME/.local/bin"
UNITS="$HOME/.config/systemd/user"
mkdir -p "$BIN" "$UNITS" "$HOME/.cc-watchdog/state"
ln -sf "$HERE/cc-deadman" "$BIN/cc-deadman"
ln -sf "$HERE/cc-stall-watchdog.sh" "$BIN/cc-stall-watchdog.sh"
cp "$HERE/cc-stall-watchdog.service" "$HERE/cc-stall-watchdog.timer" "$UNITS/"
touch "$HOME/.cc-watchdog/config"
if [[ -z "${CC_WATCHDOG_NO_SYSTEMD:-}" ]]; then
  systemctl --user daemon-reload
  systemctl --user enable --now cc-stall-watchdog.timer
fi
echo "cc-watchdog installed."
echo "Next: put SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... in ~/.cc-watchdog/config"
