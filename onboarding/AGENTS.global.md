<!-- Generic global AGENTS.md for Codex and OpenCode. Adjust the vault path after copying. -->

# Response format

Write like a senior colleague reporting to another: plain, precise, and concise. Lead with the
answer or action. Add headings, lists, recaps, uncertainty, and implementation detail only when
they help the reader decide or verify something.

# Skills

Shared skills live in `~/.agents/skills`, a symlink to the group's `agent-skills` checkout. They
carry their own descriptions, so discover them from the filesystem instead of maintaining a list
here. Read a matching skill before starting work and follow its instructions.

# Obsidian vault

The Obsidian knowledge vault is at `$HOME/Dropbox/Vault` and is synced by Dropbox. Use the
`obsidian-vault` skill to search, create, and organize its notes. Change this path if your vault
lives elsewhere.

# Decisions

When a decision changes the work, use the client's structured question tool when one is available.
Give concrete options, recommend the option you would choose, and explain its practical cost.
Proceed with reasonable implementation details that do not need the user's judgment.

# Subagents

Use a specialized subagent when independent work or a focused review will save the main session's
context. The group roles are `snippet-classifier`, `code-implementer`, `architecture-reviewer`, and
`project-executor`; their source prompts live in the DRGScripts `onboarding/agents/` directory.
Route a known, well-scoped change to `code-implementer`; route a rough goal that needs planning and
sequencing to `project-executor`. Use `architecture-reviewer` for design judgment and
`snippet-classifier` for cheap classification. Do small tasks directly.

# Working files

Treat `docs/superpowers/` as local scratch. Keep it out of Git unless the repository explicitly
documents a different policy.

# Git

- Do feature work in a dedicated worktree. Shared primary checkouts may be used by other sessions.
- Push feature branches to the canonical DanaResearchGroup remote and open pull requests there.
- Keep one logical change per commit. Ask before rewriting published history or force-pushing.
- Before a rewrite, inspect worktrees and branches based on the affected commits so concurrent work
  is not orphaned.

# Context and handoffs

Read context usage from the client instead of guessing it. At a natural checkpoint around 35%
context use, save a durable handoff if substantial work remains. A stopped session with work in
flight must leave the next agent the objective, accepted decisions, completed work, verification,
and exact next step.

# Probe premises

Before a non-trivial plan or implementation rests on a load-bearing claim, test the cheapest fact
that could disprove it against the real code, data, or tool. If the premise cannot be checked,
surface it as a design risk. Do not change the implementation merely to evade a valid guard.

# Long-running work

Persist stdout and stderr for long scientific runs, for example:

```bash
<command> > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)
```

Keep final builds and test suites owned by the main session, bound commands that can hang with
`timeout`, and leave a timer or durable handoff before ending a turn with external work pending.
