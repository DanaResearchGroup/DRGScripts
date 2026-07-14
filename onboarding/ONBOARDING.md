# Onboarding — mirror the group's Claude-Code setup

> **How to use this file:** open Claude Code on your **office Linux PC** and say
> *"read onboarding/ONBOARDING.md and walk me through it, one step at a time."* Claude Code
> will run the commands with you and stop for anything that needs your input (logins, tokens).
> Maintainers: see [MAINTAINING.md](./MAINTAINING.md).
>
> Written by Alon Grinberg Dana ([@alongd](https://github.com/alongd)).

## What you're building

- **One real environment, on your office Linux PC** — the agent stack (Claude Code,
  agent-skills, superpowers, Herdr) lives here and only here.
- **Your laptop (Win/Mac) is a thin client + Obsidian** — you SSH/mosh into the Linux PC
  and attach your Herdr session (or tmux), and you run Obsidian locally on the Dropbox-synced vault.
- This is **your own independent setup**: your own Tailscale tailnet, your own Obsidian
  vault, your own Claude account. Nothing here grants access to anyone else's machines.

First pass is **Claude Code only**, plus the **Headroom** token-compression layer (step 12),
which also pre-wires the Codex proxy. Codex CLI itself, Slack, MCP connectors, and cluster
compute are deferred — see [MAINTAINING.md](./MAINTAINING.md) for how to add them later.

---

## A. Office Linux PC (the real environment)

### 1. Base packages
```bash
sudo apt update && sudo apt install -y git tmux curl jq mosh build-essential
```
(Adapt for your distro's package manager if not Debian/Ubuntu.)

### 2. Tailscale (your own tailnet)
Install per <https://tailscale.com/download>, then:
```bash
sudo tailscale up
```
Log in with your account, give this host a clear name (e.g. `office-pc`). This joins
**your own** tailnet — it's how your laptop will reach this machine later.

### 3. Claude Code
Install Claude Code and log in with **your own** account. Confirm it runs: `claude`.

### 4. superpowers
Install the official superpowers plugin in Claude Code (its skills back this runbook).

### 5. agent-skills
Follow the **"New member — Claude Code only"** path in
<https://github.com/DanaResearchGroup/agent-skills/blob/main/SETUP.md>:
```bash
git clone https://github.com/DanaResearchGroup/agent-skills ~/Code/agent-skills
ln -s ~/Code/agent-skills ~/.claude/skills
chmod +x ~/Code/agent-skills/bin/cc-statusline.sh
```
Then wire the status line in `~/.claude/settings.json`:
```json
"statusLine": { "type": "command", "command": "/home/<you>/Code/agent-skills/bin/cc-statusline.sh" }
```
Updates later: tell Claude Code *"update my agent-skills"* (see
[UPDATING.md](https://github.com/DanaResearchGroup/agent-skills/blob/main/UPDATING.md)).

### 6. gstack skills
[gstack](https://github.com/garrytan/gstack) is a **separate** suite of ~23 Claude-Code skills
(`/review`, `/qa`, `/ship`, `/browse`, `/design-review`, …) that the global CLAUDE.md (step 8)
and the smoke test below both expect. It is *not* part of the agent-skills clone from step 5 —
it's a different repo that installs **into** that clone, so you have to add it explicitly here.
Easiest path — paste this to a Claude Code session and let it run:

> Install gstack: run `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`.

`./setup` builds gstack's headless browser and registers the skills; it needs **`bun`**
(install from <https://bun.sh>) — if `bun` is missing the script stops and prints the exact
install command, so run that first and re-run `./setup`. Because `~/.claude/skills` *is* your
agent-skills repo, gstack lands in `agent-skills/gstack/` and its skills sync into top-level
folders there; those are **git-ignored** — don't commit them. Update gstack later with
`/gstack-upgrade`. The `gstack` section in your `~/.claude/CLAUDE.md` (the skill list and the
"use `/browse` for all web browsing" rule) comes from the CLAUDE.global.md merge in step 8, so
you don't add it by hand here.

### 7. Terminal multiplexer — Herdr (tmux also supported)
A multiplexer keeps your panes (and long agent sessions) alive across
disconnects, and is what the cc-watchdog guard (step 13) drives.
**Use [Herdr](https://herdr.dev)** — it's the group's recommended default because
it's agent-aware (shows each agent's live state in a sidebar) and the cc-watchdog
guard and the PI's watchers gate on that state natively. tmux is also fully
supported if you deliberately prefer a keyboard-first, ubiquitous multiplexer.

**Herdr** (recommended):
```bash
curl -fsSL https://herdr.dev/install.sh | sh     # installs the `herdr` binary
herdr integration install claude                 # wires the agent-state hook into ~/.claude/settings.json
mkdir -p ~/.config/herdr                          # ensure the config dir exists before copying
cp <path-to-this-DRGScripts-clone>/onboarding/dotfiles/herdr-config.toml ~/.config/herdr/config.toml
```
The `/herdr` control skill ships in the agent-skills clone from step 5, so
Claude Code can drive panes/tabs directly. Launch with `herdr`, then start
`claude` inside a pane; detach with `prefix+q` (prefix is `ctrl+b`), `prefix+?`
lists all bindings.

**tmux** (alternative — if you deliberately prefer it):
```bash
cp <path-to-this-DRGScripts-clone>/onboarding/dotfiles/tmux.conf ~/.tmux.conf
```
Prefix is `C-a`. (Optional persistence plugins need `tpm` — see the comments in the file.)

The cc-watchdog stall-guard (step 13) works under both Herdr and tmux. (The PI's optional
auto-handoff / Phoenix watchers — deferred for members, see MAINTAINING — are
likewise multiplexer-aware if you enable them later.)

Optional remote-attach aliases (add to `~/.bashrc`), to connect and attach on a
workstation named `ol`:
```bash
alias olh='herdr --remote ol'                       # Herdr (needs herdr installed on ol)
alias olt='ssh -t ol "tmux attach || tmux new"'   # tmux
```

### 8. Global CLAUDE.md
Merge [CLAUDE.global.md](./CLAUDE.global.md) into your `~/.claude/CLAUDE.md` (have Claude
Code merge it, preserving any lines you've already added). Fix the **Obsidian Vault path**
to match your Dropbox layout (step 10).

### 9. ARC project guide
When you set up an ARC working copy, copy this repo's [ARC/CLAUDE.md](../ARC/CLAUDE.md)
into it so Claude Code has the ARC conventions in context.

### 10. Dropbox + Obsidian
Install the **Dropbox desktop client** (it syncs your vault at the filesystem level — no
remotely-save plugin). Install **Obsidian**. Decide your vault path, e.g.
`$HOME/Dropbox/Vault`.

### 11. Scaffold the vault
Follow [vault-structure.md](./vault-structure.md): create the folder tree and copy the
seed files (operating manual, wiki index, tools cheatsheets) into place. Then open the
folder in Obsidian ("Open folder as vault").

### 12. Headroom token compression (Claude Code + Codex)
[Headroom](https://github.com/headroomlabs-ai/headroom) compresses what your agent *reads*
(tool outputs, logs, files, history) before it reaches the model — typically **12–90% fewer
tokens, same answers**, and reversible (the model can pull originals back on demand). It runs
as two local proxies (one per provider) that your agents route through. Your data stays on
this PC.

**a. Install** — the `headroom` CLI ships via pip; `pipx` keeps it isolated and on `PATH`:
```bash
sudo apt install -y pipx            # older Ubuntu: sudo apt install -y python3-pip && python3 -m pip install --user pipx
pipx install "headroom-ai[all]"     # [all] bundles the ML compressor — large download
pipx ensurepath                     # puts ~/.local/bin on PATH for future shells
export PATH="$HOME/.local/bin:$PATH" && headroom --version   # this shell
```

**b. Set up both proxies** — one per backend (a single proxy can't serve Anthropic *and*
OpenAI). `--scope provider` writes each redirect into that tool's own config, **not** your
shell profiles:
```bash
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --target claude --backend anthropic --port 8787 --profile claude
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --target codex  --backend openai    --port 8788 --profile codex
```
This points Claude Code (`~/.claude/settings.json`) at `127.0.0.1:8787` and Codex
(`~/.codex/config.toml`) at `127.0.0.1:8788`, each as a systemd **user** service. The Codex
proxy is wired now even though Codex CLI is deferred — it's harmless until you install Codex,
then it just works.

**c. Apply the group's "Balanced" tuning** — compress tool/user context, keep the last 2 turns
verbatim, strict accuracy guard. Do **not** set `HEADROOM_SAVINGS_PROFILE`: its only valid
values re-impose the conservative defaults.
```bash
for svc in claude codex; do
  d="$HOME/.config/systemd/user/headroom-$svc.service.d"; mkdir -p "$d"
  cat > "$d/tuning.conf" <<'EOF'
[Service]
Environment=HEADROOM_COMPRESS_USER_MESSAGES=1
Environment=HEADROOM_PROTECT_RECENT=2
Environment=HEADROOM_MIN_TOKENS=250
Environment=HEADROOM_ACCURACY_GUARD=strict
EOF
done
systemctl --user daemon-reload
systemctl --user restart headroom-claude headroom-codex
sudo loginctl enable-linger "$USER"   # keep proxies up across logout/reboot
```

**d. Verify:**
```bash
headroom install status --profile claude   # Status: running · Healthy: yes
headroom install status --profile codex
headroom perf                              # savings, once traffic has flowed
```

> **Restart to take effect.** A running `claude`/`codex` reads its base URL at launch, so any
> already-open session keeps going direct until restarted. Start a fresh session (or
> `claude --continue` to keep your history) and it routes through the proxy. Subscription
> login and claude.ai connectors are unaffected.

> **To reverse it entirely:** `headroom install remove --profile claude && headroom install
> remove --profile codex`, then `rm -f ~/.config/systemd/user/headroom-{claude,codex}.service.d/tuning.conf
> && systemctl --user daemon-reload`. Optionally `sudo loginctl disable-linger "$USER"` to undo the
> linger from step **c** — but only if no *other* systemd user service relies on it (linger keeps
> all your user services alive across logout, not just Headroom's).

### 13. cc-watchdog — silent-stall guard for long agent sessions

Long autonomous Claude Code runs can die out silently: the session waits on
background work (a test suite, a build) whose owner died, and nothing ever
wakes it — it looks exactly like "done, waiting for you". cc-watchdog is a
dead-man's switch that catches this.

Before a session goes quiet while waiting on something, it declares a deadline
(`cc-deadman set 40 "full test suite, ~25 min"`). A systemd user timer checks
every 5 minutes; if the deadline passes you get a Slack ping, and if nothing
recovers within an hour the watchdog nudges the session itself ("your awaited
work likely died — check honest status and continue").

Install:
```bash
cd ~/Code/DRGScripts/onboarding/watchdog
./install.sh
```
Then put your Slack incoming-webhook URL in `~/.cc-watchdog/config`:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```
(Create one: api.slack.com/apps → your app → Incoming Webhooks → add to your
own DM or a private channel.)

Works for agent sessions under tmux and under Herdr alike (inside a Herdr pane
the deadline keys itself to the Herdr pane id and recovery uses `herdr pane
run`; see the README's "tmux and Herdr" section and run its smoke test once
from inside Herdr).

The session-side habit lives in the global CLAUDE.md you merged in step 8
(silent-stall prevention rules): agents declare deadlines before long waits and
run final gates in the mother session. The watchdog is the enforcement; the
rules are the prevention. Details: `onboarding/watchdog/README.md`.

---

## B. Laptop (Windows / macOS) — thin client + Obsidian

1. **Windows only: WSL with Ubuntu** — your terminal cockpit is a WSL Ubuntu tab in
   Windows Terminal (that's where `ssh`/`mosh` run). In an **administrator** PowerShell:
   ```powershell
   wsl --install -d Ubuntu
   ```
   Reboot when prompted, create your Ubuntu user, then inside Ubuntu:
   ```bash
   sudo apt update && sudo apt install -y mosh
   ```
   (macOS: skip — use the native Terminal; `brew install mosh` if you want mosh.)
2. **Tailscale** — install the GUI app, sign in to the same tailnet, confirm *Connected*.
3. **Terminal into the Linux PC** (run agents on the remote, never the laptop). With Herdr
   (recommended) one command attaches your remote session — start `claude` inside a pane:
   ```bash
   herdr --remote <office-pc>      # your user + tailnet host name; needs herdr on both ends
   ```
   Prefer tmux? Attach the classic way instead:
   ```bash
   ssh <you>@<office-pc>      # your user + tailnet host name
   tmux attach -t cc || tmux new -s cc
   claude
   ```
   Add the SSH alias from the seeded `tools/Remote Dev — Pattern` note to `~/.ssh/config`
   (sets `User` and `Compression yes`) so plain `ssh <office-pc>` works too.
   On flaky wifi use `mosh <you>@<office-pc>` instead of `ssh`. See the seeded
   `tools/Remote Dev — Pattern` and `tools/Tmux Cheatsheet` notes.
4. **Obsidian** — install the Dropbox client + Obsidian on the laptop and open the **same**
   synced vault folder. No agent stack on the laptop.

---

## C. Verification smoke test

- [ ] `tailscale status` shows your tailnet and this host.
- [ ] From the laptop: `ssh`/`mosh` into the Linux PC and attach your session
      (`herdr --remote`, or `tmux attach`) works.
- [ ] A Claude Code session lists the gstack skills from step 6 (type `/` and look for
      `/browse`, `/review`, `/ship`, …); superpowers loads.
- [ ] The status line shows the model name + context-window %.
- [ ] Obsidian opens the synced vault on the Linux PC **and** on the laptop; the scaffolded
      tree (`Code/`, `knowledge/`, `tools/`, …) is present with the seed notes.
- [ ] `headroom install status --profile claude` and `--profile codex` both show *running /
      healthy*; in a **freshly started** Claude Code session, typing `!env | grep ANTHROPIC_BASE_URL`
      at the Claude Code prompt (the leading `!` tells Claude Code to run the rest as a shell
      command) prints `http://127.0.0.1:8787`.
- [ ] `systemctl --user status cc-stall-watchdog.timer` shows *active (waiting)*.
- [ ] In a tmux Claude Code session: `cc-deadman set 1 "smoke test"` → Slack ping within
      ~6 min (then `cc-deadman clear`).

---

## D. Later (deferred)

Codex CLI (its Headroom proxy is already set up in step 12 — just install Codex and it routes),
Slack notifications, MCP connectors, gbrain, and cluster/PBS compute are intentionally out of
this first pass. When you're ready, [MAINTAINING.md](./MAINTAINING.md) lists each and
how to un-defer it.
