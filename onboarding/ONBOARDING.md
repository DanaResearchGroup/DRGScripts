# Onboarding — mirror the group's coding-agent setup

> **How to use this file:** open Antigravity (`agy`), Codex (`codex`), or OpenCode
> (`opencode`) on your **office Linux PC** and say *"read onboarding/ONBOARDING.md and walk
> me through it, one step at a time."* The agent will run the commands with you and stop for
> account logins, API keys, and other input only you can provide.
> Maintainers: see [MAINTAINING.md](./MAINTAINING.md).
>
> Written by Alon Grinberg Dana ([@alongd](https://github.com/alongd)).

## What you're building

- **One real environment, on your office Linux PC** — the agent clients, shared skills,
  instructions, Headroom proxies, and Herdr live here and only here.
- **Your laptop (Win/Mac) is a thin client + Obsidian** — you SSH/mosh into the Linux PC
  and attach your Herdr session (or tmux), and you run Obsidian locally on the Dropbox-synced vault.
- This is **your own independent setup**: your own Tailscale tailnet, your own Obsidian
  vault, and your own model-provider accounts. Nothing here grants access to anyone else's
  machines or credentials.

Install any combination of **Antigravity, Codex, and OpenCode**. The group configuration is
shared where the clients support common standards (`AGENTS.md` and `~/.agents/skills`) and
kept client-specific where their formats differ.

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

### 3. Coding-agent clients

Install at least one client. Installing all three is useful for cross-checking difficult work;
each client uses your own account or provider credentials.

**Antigravity:** install the `agy` CLI and authenticate with your account. Confirm it starts
with `agy`.

**Codex:** install the official CLI, start it, and sign in with your ChatGPT account:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
```

**OpenCode:** install the official CLI, start it, and run `/connect` to choose a provider and
enter that provider's API key:

```bash
curl -fsSL https://opencode.ai/install | bash
opencode
```

OpenCode stores provider credentials in `~/.local/share/opencode/auth.json`. Keep that file
local and out of Git. In each project, `/init` can create or improve a project `AGENTS.md`;
review it and commit it with the project. See OpenCode's official
[configuration](https://opencode.ai/docs/config/), [rules](https://opencode.ai/docs/rules/),
and [skills](https://opencode.ai/docs/skills/) references when its format changes.

### 4. Client configuration locations

| Client | Global instructions | Global config | Project instructions |
|---|---|---|---|
| Antigravity | `~/.gemini/config/GEMINI.md` | `~/.gemini/config/` | `.agents/rules/` |
| Codex | `~/.codex/AGENTS.md` | `~/.codex/config.toml` | `AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` | `~/.config/opencode/opencode.json` | `AGENTS.md` |

Codex can fall back to existing `CLAUDE.md` and `GEMINI.md` files when configured to do so.
OpenCode uses `CLAUDE.md` only when no `AGENTS.md` exists. Prefer adding `AGENTS.md` to each
project over maintaining three copies of the same project rules.

### 5. agent-skills
The group's skills live in one repo — [`DanaResearchGroup/agent-skills`](https://github.com/DanaResearchGroup/agent-skills).
Clone it once and expose the same checkout through the shared agent-standard path and the
Claude-compatible path. Codex and OpenCode discover `~/.agents/skills` directly; the second
link preserves Claude Code and older skill assumptions:
```bash
git clone https://github.com/DanaResearchGroup/agent-skills.git ~/Code/agent-skills
mkdir -p ~/.agents ~/.claude
for path in ~/.agents/skills ~/.claude/skills; do
  [ -e "$path" ] && [ ! -L "$path" ] \
    && mv "$path" "$path.bak.$(date +%Y%m%d%H%M%S)"
done
ln -sfn ~/Code/agent-skills ~/.agents/skills
ln -sfn ~/Code/agent-skills ~/.claude/skills
ls -ld ~/.agents/skills ~/.claude/skills
```
That symlink is the whole install. Skills are self-describing — each carries its own
description, so the agent finds the right one without a list to maintain. Read
`agent-skills/README.md` for what's in there; `git -C ~/Code/agent-skills pull` updates
everything at once.

Discovery does not guarantee client compatibility. A skill that names Claude-only tools,
`~/.claude` hooks, or Claude hook response JSON may remain Claude-specific even though Codex or
OpenCode can see it. Treat the skill's `compatibility` field and its own setup section as
authoritative. Maintainers should port the workflow or mark the limitation rather than relying
on path aliases to hide it.

We **do not use gstack.** It was a third-party suite we ran for a while and removed in
August 2026: most of its skills went unused, and the ones we wanted couldn't be fixed
durably because the repo was upstream-owned. `/review` was rewritten as ours inside
`agent-skills`; the rest were dropped. If you see `gstack` in an older doc or in your own
setup, see *Already installed gstack?* below.

Status displays differ by client. Claude Code users can install the script under
[`statusline/`](./statusline/). Codex users should configure the native status line and can
optionally build the group's dual-budget enhancement under
[`statusline/codex/`](./statusline/codex/). OpenCode reports session usage through its TUI and
`opencode stats`; it does not currently expose a Codex-style configurable footer.

#### Already installed gstack? (migrating an existing setup)

Skip this if you're setting up fresh. If you followed an earlier version of this runbook you
have a `~/.claude/skills/gstack` clone (~1.6 GB) and a `~/.gstack` state directory. Removing
them is safe, but **do the state copy first** — `~/.gstack/projects/` holds accumulated
per-project learnings that the skills still read, just from a new path:

```bash
# 1. Keep the learnings. ~/.skills is where the current skills read this state from.
mkdir -p ~/.skills
cp -rn ~/.gstack/* ~/.skills/ 2>/dev/null || true
diff -r ~/.gstack/projects ~/.skills/projects && echo "state copied intact"
```

Only once that `diff` prints `state copied intact`:

```bash
# 2. Drop the suite and the old state directory.
rm -rf ~/.claude/skills/gstack ~/.gstack

# 3. Point the skills directory at the group repo (step 5 above). If ~/.claude/skills is a
#    real directory rather than a symlink, move your own skills into the clone first.
ls -ld ~/.claude/skills
```

Finally, remove the `# gstack` section from your `~/.claude/CLAUDE.md` (or `GEMINI.md`) if you
copied an older `CLAUDE.global.md` — it lists ~35 skills that no longer exist, and an agent
reading it will keep trying to invoke them. `/browse` in particular is gone; use the agent's
own web tools.

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
herdr integration install codex
herdr integration install opencode
mkdir -p ~/.config/herdr                          # ensure the config dir exists before copying
cp <path-to-this-DRGScripts-clone>/onboarding/dotfiles/herdr-config.toml ~/.config/herdr/config.toml
```
If a client is not installed, skip its integration command. Herdr does not currently publish an
`agy` integration target; AGY still runs normally inside a Herdr pane. Confirm the installed
hooks with `herdr integration status`. The `/herdr` control skill lets supported agents drive
panes and tabs. Launch with `herdr`, start your chosen agent inside a pane, detach with `prefix+q`
(prefix is `ctrl+b`), and use `prefix+?` to list all bindings.

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

### 7. Global instructions and subagents

Copy the client-neutral group instructions, then edit the **Obsidian Vault path** to match
your Dropbox layout:

```bash
mkdir -p ~/.codex ~/.config/opencode ~/.gemini/config
cp <path-to-this-DRGScripts-clone>/onboarding/AGENTS.global.md ~/.codex/AGENTS.md
cp <path-to-this-DRGScripts-clone>/onboarding/AGENTS.global.md ~/.config/opencode/AGENTS.md
cp <path-to-this-DRGScripts-clone>/onboarding/CLAUDE.global.md ~/.gemini/config/GEMINI.md
```

For Codex, merge the following into `~/.codex/config.toml` so repositories that have not
migrated yet still load their existing guides. Keep `project_doc_fallback_filenames` at the TOML
top level, before any `[section]` header:

```toml
project_doc_fallback_filenames = ["CLAUDE.md", "GEMINI.md"]

[tui]
status_line = ["model-with-reasoning", "current-dir", "git-branch", "context-used"]
```

The native `context-used` item prints a percentage. To reproduce the PI's exact dual-budget
footer — for example `Context 188.3k/1050k 17.9% (188.3k/258.4k 72.9%)` — follow
[`statusline/codex/README.md`](./statusline/codex/README.md). The first denominator is the
model's published maximum; the parenthesized denominator is Codex's effective runtime budget.
That enhanced text requires the documented source patch because stock Codex does not expose a
custom status-line command.

In Antigravity, **Subagents** are spawned dynamically via the `define_subagent` and `invoke_subagent` tools.
Our four group roles live in [`onboarding/agents/`](./agents/) as one Markdown file each —
`snippet-classifier.md`, `code-implementer.md`, `architecture-reviewer.md`,
`project-executor.md`. Each carries the role's name, description, pinned model, and effort in
its front-matter, plus the system prompt in its body. Point Antigravity at them and ask it to
register each as a subagent:

> "Read `<path-to-this-DRGScripts-clone>/onboarding/agents/*.md` and register each as a
> subagent with `define_subagent`, using the front-matter for name, description, and model."

AGY has no persistent subagent registry yet, so this is a per-session step until it does.

Install equivalent native definitions from the same canonical role files:

```bash
python3 <path-to-this-DRGScripts-clone>/onboarding/agents/install.py codex
python3 <path-to-this-DRGScripts-clone>/onboarding/agents/install.py opencode
```

The installer maps the four cost tiers to current Codex models. OpenCode provider model IDs vary,
so its generated roles inherit the active model; add a valid `provider/model` field later if you
want a provider-specific pin. The installer refuses to overwrite an existing role. Verify with
Codex's `/agent` picker and `opencode agent list`; invoke an OpenCode subagent with `@name`.

### 8. ARC project guide
When you set up an ARC working copy, copy this repo's rules into the standard project guide.
Antigravity also gets its native rule copy:
```bash
cp <path-to-this-DRGScripts-clone>/ARC/CLAUDE.md <arc-path>/AGENTS.md
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

### 11. Headroom token compression (AGY + Codex + OpenCode)

[Headroom](https://github.com/headroomlabs-ai/headroom) compresses selected context before it
reaches the model. Savings depend on the workload, so treat `headroom perf` as the evidence for
your setup rather than assuming a fixed percentage.

**a. Install** — the `headroom` CLI ships via pip; `pipx` keeps it isolated and on `PATH`:
```bash
sudo apt install -y pipx            # older Ubuntu: sudo apt install -y python3-pip && python3 -m pip install --user pipx
pipx install "headroom-ai[all]"     # [all] bundles the ML compressor — large download
pipx ensurepath                     # puts ~/.local/bin on PATH for future shells
export PATH="$HOME/.local/bin:$PATH" && headroom --version   # this shell
```

**b. Set up one proxy per client.** Separate ports and profiles make each integration easy to
inspect, restart, or remove. Headroom has native Codex and OpenCode targets. Antigravity still
uses a provider-only service plus `GEMINI_BASE_URL`. Run only the command blocks for clients you
are onboarding.
```bash
# AGY service: no direct client mutation; the shell variable below performs the routing.
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --backend google --port 8787 --profile agy

# Codex and OpenCode: Headroom writes reversible, client-native provider configuration.
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --target codex  --backend openai    --port 8788 --profile codex
headroom install apply --preset persistent-service --runtime python --scope provider \
  --providers manual --target opencode --backend openai --port 8789 --profile opencode
```
If OpenCode uses an Anthropic provider, set its Headroom backend to `anthropic` instead. The
installer preserves unrelated OpenCode settings and records a backup for removal.

If you installed the AGY profile, inject its base URL into your shell profile. The guard keeps a
re-run from appending a second copy:
```bash
grep -qxF 'export GEMINI_BASE_URL="http://127.0.0.1:8787"' ~/.bashrc \
  || echo 'export GEMINI_BASE_URL="http://127.0.0.1:8787"' >> ~/.bashrc
```

**c. Apply the group's "Balanced" tuning** — compress tool/user context, keep the last 2 turns
verbatim, strict accuracy guard. Do **not** set `HEADROOM_SAVINGS_PROFILE`: its only valid
values re-impose the conservative defaults.
```bash
# Keep only the profiles you installed in step b, for example: services=(codex opencode)
services=(agy codex opencode)
for svc in "${services[@]}"; do
  dropin_dir="$HOME/.config/systemd/user/headroom-$svc.service.d"; mkdir -p "$dropin_dir"
  cat > "$dropin_dir/tuning.conf" <<'EOF'
[Service]
Environment=HEADROOM_COMPRESS_USER_MESSAGES=1
Environment=HEADROOM_PROTECT_RECENT=2
Environment=HEADROOM_MIN_TOKENS=250
Environment=HEADROOM_ACCURACY_GUARD=strict
EOF
done
systemctl --user daemon-reload
for svc in "${services[@]}"; do
  systemctl --user restart "headroom-$svc"
done
sudo loginctl enable-linger "$USER"   # keep proxies up across logout/reboot
```

**d. Verify** the same profiles selected in `services`:
```bash
for profile in "${services[@]}"; do
  headroom install status --profile "$profile"   # Status: running · Healthy: yes
done
headroom perf                                    # savings, once traffic has flowed
```

> **Restart to take effect.** Open agent sessions retain their old provider settings. Start fresh
> sessions for the clients whose profiles you installed.

> **To reverse it entirely:** run `headroom install remove --profile <name>` and remove
> `tuning.conf` for each profile in `services`, then run `systemctl --user daemon-reload`. If AGY
> was selected, also remove `GEMINI_BASE_URL` from `~/.bashrc`.

### 12. Silent-stall guard for long agent sessions

Long autonomous sessions can die out silently when waiting on background work (e.g. test suites) whose owner died.
**With Antigravity, we no longer need the bash-based `cc-watchdog`.**
AGY natively supports background tasks and a `/schedule` slash command. 

Before a session goes quiet while waiting on something, the agent must simply set an
early-termination timer. There are two forms of this, and they are not interchangeable.

**What you type**, in an AGY session:
```text
/schedule 2400 Check on the command status. If it stalled, ping Slack.
```

**What the agent emits internally** — shown so you recognise it in a transcript. Do not paste
this anywhere; it is not a shell command and not a slash command:
```text
call:default_api:schedule{"DurationSeconds":"2400", "Prompt":"Check on the command status. If it stalled, ping Slack.", "TimerCondition":"any"}
```
The agent's rules (`GEMINI.md`) instruct it to always set a `TimerCondition: any` timer before long waits. If the background tasks finish early, the timer is aborted. If the deadline passes, the timer fires a high-priority message directly into the agent's context, and the agent uses the `slack-notify` skill to ping you. 

*You do not need to install `watchdog/install.sh` anymore.*

The Slack ping is **optional** — Slack is deferred in this first pass (section D). If you do want
it, the `slack-notify` skill authenticates with a bot token, not a webhook: follow the Slack row
in [MAINTAINING.md](./MAINTAINING.md) to create the token and write it to
`~/.claude/.slack-bot-token`. That path is the skill's own default and is **not** a typo for a
`~/.gemini/` one — the skill predates AGY and reads it regardless of which agent invokes it; set
`CC_SLACK_TOKEN_FILE` if you want it elsewhere. Without a token the timer still fires into the
agent's context; you just don't get the push notification.

### 13. Contract gate — define the work before editing (Claude Code only)

> **Not yet ported to Antigravity.** The gate is a Claude Code `PreToolUse` hook wired into
> `~/.claude/settings.json`; AGY manages hooks under `~/.gemini/config/`. On a first-pass AGY
> setup this step installs nothing — skip it, and see the port row in
> [MAINTAINING.md](./MAINTAINING.md).

The `contract` skill (in `agent-skills`) exists to catch **correct code, wrong thing**: a clean
implementation of a misread request, discovered only after the tokens are spent. It denies the
first `Edit`/`Write`/`NotebookEdit` in an opted-in repo until a durable note records Intent,
Verifier, Non-goals and Gates. `Read`, `Grep` and `Bash` are never gated, so exploration is
untouched.

**a. Wire the two hooks** — type `/hooks` in Claude Code and add both. They fail open: with no
repo enabled they exit 0 and change nothing, so wiring them is safe before any repo opts in.

- **`PreToolUse`** — matcher `Edit|Write|NotebookEdit`, command
  `~/.claude/skills/contract/hooks/contract-gate.sh`
- **`SessionStart`** — no matcher, command
  `~/.claude/skills/contract/hooks/contract-inject.sh`

Copy the matcher exactly as written: three tool names separated by plain `|`, no backslashes.

**b. Ask which repos to gate — never assume a list.**

> **Agent running this onboarding, on Claude Code: stop here and ask.** Use `AskUserQuestion`,
> multi-select, offering the repos the member has actually cloned as options. Enabling a repo
> changes how every future session behaves in it, so the list is the member's call, not yours —
> and a list you guessed is one they will disable in a week. Recommend starting with two or
> three where a misread request costs the most to unwind.
>
> **On Antigravity, do not stop and do not ask** — this whole step is unported (see the banner
> above). Skip straight to section B.

Then, for each repo they chose:
```bash
cd <repo> && ~/.claude/skills/contract/bin/contract enable
```
Enabling is keyed on the shared git dir, so one call covers every worktree of that repo.

**c. Put the CLI on your PATH** — optional, for typing `contract new <slug>` by hand. The hooks
call it by absolute path, so nothing breaks without this. Safe to re-run:
```bash
mkdir -p ~/.local/bin
ln -sfn ~/.claude/skills/contract/bin/contract ~/.local/bin/contract
```
(`~/.local/bin` is already on `PATH` if you ran `pipx ensurepath` in step 11.)

**d. Expand on evidence, not enthusiasm.** The skip log is the instrument:
```bash
cat "$(git rev-parse --git-common-dir)/contract-skips.log"
```
A repo where skips dominate is a repo where the gate is noise — run `contract disable` there.
Add repos only where the log shows it catching real definition gaps.

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
- [ ] Each installed client sees the shared skills: ask it to list `review`, `handoff`, and
      `obsidian-vault`, and confirm `ls -ld ~/.agents/skills` points at the group clone.
- [ ] Codex: `/statusline` includes `context-used`. With the optional group build, it renders
      both budgets in the form `Context used/model % (used/effective %)`. OpenCode:
      `opencode stats` returns session/token statistics.
- [ ] `herdr integration status` reports current Codex and OpenCode integrations for the
      clients you installed.
- [ ] Obsidian opens the synced vault on the Linux PC **and** on the laptop; the scaffolded
      tree (`Code/`, `knowledge/`, `tools/`, …) is present with the seed notes.
- [ ] `headroom install status --profile agy`, `--profile codex`, and `--profile opencode`
      show *running / healthy* for the clients you installed. In the shell you'll launch AGY
      from, `echo $GEMINI_BASE_URL` prints
      `http://127.0.0.1:8787` — open a **new** shell first, since step 11 only appended it to
      `~/.bashrc`.
- [ ] Launch `agy` and test the native schedule tool: `/schedule 300 Check if tests finished`. Ensure the scheduled task runs in the background.
- [ ] *(Claude Code only, step 13)* In a repo you enabled, `contract status` prints
      `enabled=yes`, and asking Claude Code to edit a file there is denied with instructions
      naming `contract new` and `contract skip`. In a repo you did **not** enable, editing is
      unaffected.

---

## D. Later (deferred)

Slack notifications, MCP connectors, gbrain, and cluster/PBS compute remain outside the first
pass. When you're ready, [MAINTAINING.md](./MAINTAINING.md) lists each and how to add it.
