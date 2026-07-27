# Onboarding — mirror the group's Antigravity (AGY) setup

> **How to use this file:** open the Antigravity CLI (`agy`) on your **office Linux PC** and say
> *"read onboarding/ONBOARDING.md and walk me through it, one step at a time."* Antigravity
> will run the commands with you and stop for anything that needs your input (logins, tokens).
> Maintainers: see [MAINTAINING.md](./MAINTAINING.md).
>
> Written by Alon Grinberg Dana ([@alongd](https://github.com/alongd)).

## What you're building

- **One real environment, on your office Linux PC** — the agent stack (Antigravity CLI,
  skills, plugins, Herdr) lives here and only here.
- **Your laptop (Win/Mac) is a thin client + Obsidian** — you SSH/mosh into the Linux PC
  and attach your Herdr session (or tmux), and you run Obsidian locally on the Dropbox-synced vault.
- This is **your own independent setup**: your own Tailscale tailnet, your own Obsidian
  vault, your own Antigravity account. Nothing here grants access to anyone else's machines.

First pass is **Antigravity only**, plus the **Headroom** token-compression layer (step 11),
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

### 3. Antigravity CLI
Install the Antigravity CLI (`agy`) and authenticate with your account. Confirm it runs: `agy`.

### 4. Customizations & Plugins
Antigravity natively supports many advanced functionalities without third-party plugins. Custom rules, hooks, plugins, and MCP servers are managed via `~/.gemini/config/` (global) or `.agents/` (per-project).

### 5. agent-skills & gstack skills
The `agent-skills` and `gstack` suites (e.g. `/review`, `/ship`, `/qa`, `/browse`) have been **natively ported to Antigravity**. 
You do **not** need to `git clone` them manually. They are automatically available in `~/.gemini/antigravity-cli/skills/`.
AGY uses progressive disclosure to only inject skill descriptions into context until they are needed, keeping your sessions lightweight.
You can update your global skills later by asking Antigravity to *"upgrade gstack skills"*.

**Status line — not yet ported.** The installer in this repo
(`onboarding/statusline/install.sh`) patches Claude Code's `settings.json` and does **not**
apply to Antigravity. Skip it and use AGY's built-in CLI telemetry for now; porting it to an
AGY hook is tracked in [MAINTAINING.md](./MAINTAINING.md).

### 6. Terminal multiplexer — Herdr (tmux also supported)
A multiplexer keeps your panes (and long agent sessions) alive across
disconnects.
**Use [Herdr](https://herdr.dev)** — it's the group's recommended default because
it's agent-aware (shows each agent's live state in a sidebar), which is what the
PI's watchers gate on natively. tmux is also fully
supported if you deliberately prefer a keyboard-first, ubiquitous multiplexer.

**Herdr** (recommended):
```bash
curl -fsSL https://herdr.dev/install.sh | sh     # installs the `herdr` binary
herdr integration install agy                    # wires the agent-state hook into AGY (if supported, otherwise hooks.json)
mkdir -p ~/.config/herdr                          # ensure the config dir exists before copying
cp <path-to-this-DRGScripts-clone>/onboarding/dotfiles/herdr-config.toml ~/.config/herdr/config.toml
```
The `/herdr` control skill is ported to AGY, so
Antigravity can drive panes/tabs directly. Launch with `herdr`, then start
`agy` inside a pane; detach with `prefix+q` (prefix is `ctrl+b`), `prefix+?`
lists all bindings.

**tmux** (alternative — if you deliberately prefer it):
```bash
cp <path-to-this-DRGScripts-clone>/onboarding/dotfiles/tmux.conf ~/.tmux.conf
```
Prefix is `C-a`. (Optional persistence plugins need `tpm` — see the comments in the file.)

The stall guard (step 12) is AGY-native and needs no multiplexer support of its own. (The PI's
optional auto-handoff / Phoenix watchers — deferred for members, see MAINTAINING — are
multiplexer-aware if you enable them later.)

Optional remote-attach aliases (add to `~/.bashrc`), to connect and attach on a
workstation named `ol`:
```bash
alias olh='herdr --remote ol'                       # Herdr (needs herdr installed on ol)
alias olt='ssh -t ol "tmux attach || tmux new"'   # tmux
```

### 7. Global Rules and Subagents (GEMINI.md)
Migrate [CLAUDE.global.md](./CLAUDE.global.md) rules into your global Antigravity config (`~/.gemini/config/GEMINI.md`). Fix the **Obsidian Vault path** to match your Dropbox layout.

In Antigravity, **Subagents** are spawned dynamically via the `define_subagent` and `invoke_subagent` tools.
Our four group roles live in [`onboarding/agents/`](./agents/) as one Markdown file each —
`snippet-classifier.md`, `code-implementer.md`, `architecture-reviewer.md`,
`project-executor.md`. Each carries the role's name, description, pinned model, and effort in
its front-matter, plus the system prompt in its body. Point Antigravity at them and ask it to
register each as a subagent:

> "Read `<path-to-this-DRGScripts-clone>/onboarding/agents/*.md` and register each as a
> subagent with `define_subagent`, using the front-matter for name, description, and model."

AGY has no persistent subagent registry yet, so this is a per-session step until it does.

### 8. ARC project guide
When you set up an ARC working copy, copy this repo's rules to it so Antigravity has the ARC conventions in context:
```bash
mkdir -p <arc-path>/.agents/rules
cp <path-to-this-DRGScripts-clone>/ARC/CLAUDE.md <arc-path>/.agents/rules/arc-rules.md
```

### 9. Dropbox + Obsidian
Install the **Dropbox desktop client** (it syncs your vault at the filesystem level — no
remotely-save plugin). Install **Obsidian**. Decide your vault path, e.g.
`$HOME/Dropbox/Vault`.

### 10. Scaffold the vault
Follow [vault-structure.md](./vault-structure.md): create the folder tree and copy the
seed files (operating manual, wiki index, tools cheatsheets) into place. Then open the
folder in Obsidian ("Open folder as vault").

### 11. Headroom token compression (AGY + Codex)
[Headroom](https://github.com/headroomlabs-ai/headroom) compresses what your agent *reads* before it reaches the model — typically **12–90% fewer tokens, same answers**.

**a. Install** — the `headroom` CLI ships via pip; `pipx` keeps it isolated and on `PATH`:
```bash
sudo apt install -y pipx            # older Ubuntu: sudo apt install -y python3-pip && python3 -m pip install --user pipx
pipx install "headroom-ai[all]"     # [all] bundles the ML compressor — large download
pipx ensurepath                     # puts ~/.local/bin on PATH for future shells
export PATH="$HOME/.local/bin:$PATH" && headroom --version   # this shell
```

**b. Set up both proxies** — For Antigravity (`agy`), we manually route its traffic through Headroom using environment variables until it receives official installer support.
```bash
# Start a systemd service for AGY proxy (using generic or Google backend depending on Headroom support)
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --target generic --backend google --port 8787 --profile agy
  
# Setup Codex CLI proxy
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --target codex  --backend openai    --port 8788 --profile codex
```
Then, inject the Base URL into your bash profile for Antigravity. The guard keeps a re-run from
appending a second copy:
```bash
grep -qxF 'export GEMINI_BASE_URL="http://127.0.0.1:8787"' ~/.bashrc \
  || echo 'export GEMINI_BASE_URL="http://127.0.0.1:8787"' >> ~/.bashrc
```

**c. Apply the group's "Balanced" tuning** — compress tool/user context, keep the last 2 turns
verbatim, strict accuracy guard. Do **not** set `HEADROOM_SAVINGS_PROFILE`: its only valid
values re-impose the conservative defaults.
```bash
for svc in agy codex; do
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
systemctl --user restart headroom-agy headroom-codex
sudo loginctl enable-linger "$USER"   # keep proxies up across logout/reboot
```

**d. Verify:**
```bash
headroom install status --profile agy   # Status: running · Healthy: yes
headroom install status --profile codex
headroom perf                              # savings, once traffic has flowed
```

> **Restart to take effect.** Any open `agy` session keeps going direct until restarted. Start a fresh session and it routes through the proxy.

> **To reverse it entirely:** `headroom install remove --profile agy && headroom install
> remove --profile codex`, then `rm -f ~/.config/systemd/user/headroom-{agy,codex}.service.d/tuning.conf
> && systemctl --user daemon-reload`. Don't forget to remove `GEMINI_BASE_URL` from your `~/.bashrc`.

### 12. Silent-stall guard for long agent sessions

Long autonomous sessions can die out silently when waiting on background work (e.g. test suites) whose owner died.
**With Antigravity, we no longer need the bash-based `cc-watchdog`.**
AGY natively supports background tasks and a `/schedule` slash command. 

Before a session goes quiet while waiting on something, the agent must simply set an early-termination timer:
```bash
# Agent sets a timer to check back if stalled (natively handled within AGY):
call:default_api:schedule{"DurationSeconds":"2400", "Prompt":"Check on the command status. If it stalled, ping Slack.", "TimerCondition":"any"}
```
The agent's rules (`GEMINI.md`) instruct it to always set a `TimerCondition: any` timer before long waits. If the background tasks finish early, the timer is aborted. If the deadline passes, the timer fires a high-priority message directly into the agent's context, and the agent uses the `slack-notify` skill to ping you. 

*You do not need to install `watchdog/install.sh` anymore.*

The Slack ping is **optional** — Slack is deferred in this first pass (section D). If you do want
it, the `slack-notify` skill authenticates with a bot token, not a webhook: follow the Slack row
in [MAINTAINING.md](./MAINTAINING.md) to create the token and write it to
`~/.claude/.slack-bot-token`. Without it the timer still fires into the agent's context; you just
don't get the push notification.

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
   (recommended) one command attaches your remote session — start `agy` inside a pane:
   ```bash
   herdr --remote <office-pc>      # your user + tailnet host name; needs herdr on both ends
   ```
   Prefer tmux? Attach the classic way instead:
   ```bash
   ssh <you>@<office-pc>      # your user + tailnet host name
   tmux attach -t cc || tmux new -s cc
   agy
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
- [ ] An Antigravity session lists the group skills (type `/` and look for
      `/browse`, `/review`, `/ship`, …).
- [ ] The status line (if installed) shows the model name, context-window %, and
      your git location.
- [ ] Obsidian opens the synced vault on the Linux PC **and** on the laptop; the scaffolded
      tree (`Code/`, `knowledge/`, `tools/`, …) is present with the seed notes.
- [ ] `headroom install status --profile agy` and `--profile codex` both show *running /
      healthy*. In a **freshly started** Antigravity session, running `!echo $GEMINI_BASE_URL`
      prints `http://127.0.0.1:8787`.
- [ ] Launch `agy` and test the native schedule tool: `/schedule 300 Check if tests finished`. Ensure the scheduled task runs in the background.

---

## D. Later (deferred)

Codex CLI (its Headroom proxy is already set up in step 11 — just install Codex and it routes),
Slack notifications, MCP connectors, gbrain, and cluster/PBS compute are intentionally out of
this first pass. When you're ready, [MAINTAINING.md](./MAINTAINING.md) lists each and
how to un-defer it.
