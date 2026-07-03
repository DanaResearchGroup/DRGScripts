---
title: Remote Dev — Pattern
tags: [tools, remote-dev, ssh, tailscale]
---

# Remote Dev — Pattern (laptop → Linux host)

> Part of [[Tools Index]] · companion to [[Tmux Cheatsheet]].

The working model: **one real environment on your office Linux PC**; your Win/Mac
laptop is a thin client into it plus native Obsidian. The agent stack (Claude Code,
agent-skills, superpowers) lives only on the Linux host. Fill the `<placeholders>`
with your own values once your tailnet is up.

## Setup summary

- **Tailscale** joins all your machines to one private network. Install on the Linux
  host (`sudo tailscale up`) and on each laptop (GUI app). Each host gets a stable
  MagicDNS name (e.g. `<linux-host>`) — no public IP, no port-forwarding.
- **SSH alias** (laptop `~/.ssh/config`, and a Windows copy at
  `C:\Users\<you>\.ssh\config` if you use WSL / VS Code Remote):
  ```
  Host <linux-host>
      HostName <linux-host>          # the tailnet MagicDNS name
      User <your-user>
      Compression yes                # helps on slow/remote links
  ```
- **Cockpit on Windows:** the WSL Ubuntu tab in Windows Terminal. On macOS: the native
  terminal.

## Sit down & get working (30-second routine)

1. Open your terminal (WSL Ubuntu tab on Windows; Terminal on macOS).
2. Confirm **Tailscale** shows *Connected* (tray/menubar icon).
3. Attach to where you left off:
   ```bash
   ssh <linux-host>          # then: tmux attach -t cc   (or: tmux new -s cc)
   ```
   Optional terminal profile that auto-lands in tmux:
   ```
   ssh -t <linux-host> "tmux attach -t cc || tmux new -s cc"
   ```

## The golden rule

**Always run Claude Code (and any long job) inside `tmux` on the remote.** A dropped
wifi / closed lid / network blip then never kills the agent — it keeps running on the
Linux host and you just re-attach.

- Detach (leave running): **`C-a` then `d`** (prefix remapped from `C-b` — see [[Tmux Cheatsheet]])
- Re-attach: `tmux attach -t cc`
- List sessions: `tmux ls`

## Flaky networks — use mosh

On hotel/cell wifi, prefer **mosh** to the host — it rides out IP changes and lag:
```bash
mosh <your-user>@<linux-host>     # then tmux attach -t cc
```

## Editing files on the host from the laptop

- **VS Code Remote-SSH** (`<linux-host>`) for a full editor + integrated terminal.
- Or a mounted drive over SSHFS — browse/quick-edit only; run builds/agents in tmux
  **on the host**, not over the mount.

---

> Cluster/compute access (PBS, exit nodes, institution VPNs) is **out of scope** for the
> first-pass setup. Add a section here for your own cluster once you have access.
