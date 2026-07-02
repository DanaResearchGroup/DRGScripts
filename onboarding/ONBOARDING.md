# Onboarding — mirror the group's Claude-Code setup

> **How to use this file:** open Claude Code on your **office Linux PC** and say
> *"read onboarding/ONBOARDING.md and walk me through it, one step at a time."* Claude Code
> will run the commands with you and stop for anything that needs your input (logins, tokens).
> Maintainers: see [MAINTAINING.md](./MAINTAINING.md).

## What you're building

- **One real environment, on your office Linux PC** — the agent stack (Claude Code,
  agent-skills, superpowers, tmux) lives here and only here.
- **Your laptop (Win/Mac) is a thin client + Obsidian** — you SSH/mosh into the Linux PC
  and `tmux attach`, and you run Obsidian locally on the Dropbox-synced vault.
- This is **your own independent setup**: your own Tailscale tailnet, your own Obsidian
  vault, your own Claude account. Nothing here grants access to anyone else's machines.

First pass is **Claude Code only**. Codex, Slack, MCP connectors, and cluster compute are
deferred — see [MAINTAINING.md](./MAINTAINING.md) for how to add them later.

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
<https://github.com/alongd/agent-skills/blob/main/SETUP.md>:
```bash
git clone https://github.com/alongd/agent-skills ~/Code/agent-skills
ln -s ~/Code/agent-skills ~/.claude/skills
chmod +x ~/Code/agent-skills/bin/cc-statusline.sh
```
Then wire the status line in `~/.claude/settings.json`:
```json
"statusLine": { "type": "command", "command": "/home/<you>/Code/agent-skills/bin/cc-statusline.sh" }
```
Updates later: tell Claude Code *"update my agent-skills"* (see
[UPDATING.md](https://github.com/alongd/agent-skills/blob/main/UPDATING.md)).

### 6. tmux config
```bash
cp <path-to-this-DRGScripts-clone>/onboarding/dotfiles/tmux.conf ~/.tmux.conf
```
Prefix is `C-a`. (Optional persistence plugins need `tpm` — see the comments in the file.)

### 7. Global CLAUDE.md
Merge [CLAUDE.global.md](./CLAUDE.global.md) into your `~/.claude/CLAUDE.md` (have Claude
Code merge it, preserving any lines you've already added). Fix the **Obsidian Vault path**
to match your Dropbox layout (step 9).

### 8. ARC project guide
When you set up an ARC working copy, copy this repo's [ARC/CLAUDE.md](../ARC/CLAUDE.md)
into it so Claude Code has the ARC conventions in context.

### 9. Dropbox + Obsidian
Install the **Dropbox desktop client** (it syncs your vault at the filesystem level — no
remotely-save plugin). Install **Obsidian**. Decide your vault path, e.g.
`$HOME/Dropbox/Vault`.

### 10. Scaffold the vault
Follow [vault-structure.md](./vault-structure.md): create the folder tree and copy the
seed files (operating manual, wiki index, tools cheatsheets) into place. Then open the
folder in Obsidian ("Open folder as vault").

---

## B. Laptop (Windows / macOS) — thin client + Obsidian

1. **Tailscale** — install the GUI app, sign in to the same tailnet, confirm *Connected*.
2. **Terminal into the Linux PC** (run agents on the remote, never the laptop):
   ```bash
   ssh <office-pc>            # your tailnet host name
   tmux attach -t cc || tmux new -s cc
   claude
   ```
   On flaky wifi use `mosh <you>@<office-pc>` instead of `ssh`. See the seeded
   `tools/Remote Dev — Pattern` and `tools/Tmux Cheatsheet` notes.
3. **Obsidian** — install the Dropbox client + Obsidian on the laptop and open the **same**
   synced vault folder. No agent stack on the laptop.

---

## C. Verification smoke test

- [ ] `tailscale status` shows your tailnet and this host.
- [ ] From the laptop: `ssh`/`mosh` into the Linux PC, `tmux attach` works.
- [ ] A Claude Code session lists the gstack skills (type `/`); superpowers loads.
- [ ] The status line shows the model name + context-window %.
- [ ] Obsidian opens the synced vault on the Linux PC **and** on the laptop; the scaffolded
      tree (`Code/`, `knowledge/`, `tools/`, …) is present with the seed notes.

---

## D. Later (deferred)

Codex, Slack notifications, MCP connectors, gbrain, and cluster/PBS compute are intentionally
out of this first pass. When you're ready, [MAINTAINING.md](./MAINTAINING.md) lists each and
how to un-defer it.
