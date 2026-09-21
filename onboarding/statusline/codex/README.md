# Codex context status line

Stock Codex has a configurable native status line. Put this in `~/.codex/config.toml` or run
`/statusline` and select the same items:

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "git-branch", "context-used"]
```

The stock `context-used` item reports one percentage. The PI's build expands that item to show
the same token count against two limits:

```text
Context 188.3k/1050k 17.9% (188.3k/258.4k 72.9%)
        used / model maximum       used / effective Codex budget
```

The effective budget comes from the running Codex session. The model maximum is a small explicit
table in the patch; unknown models display `?` rather than borrowing the effective budget.

## Build the enhanced binary

This patch is pinned to upstream commit
[`fc269b66`](https://github.com/openai/codex/commit/fc269b66adc37f3c855df222ad80b02733355c46),
verified on 2026-09-15. The model-limit table follows OpenAI's
[model documentation](https://developers.openai.com/api/docs/models) as checked on that date.
Install the Rust toolchain named by `codex-rs/rust-toolchain.toml` plus the platform
build dependencies:

```bash
sudo apt update
sudo apt install -y build-essential pkg-config libssl-dev
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Then build a separate binary:

```bash
git clone https://github.com/openai/codex.git ~/Code/codex-context-status
cd ~/Code/codex-context-status
git checkout fc269b66adc37f3c855df222ad80b02733355c46
~/Code/DRGScripts/onboarding/statusline/codex/verify.sh "$PWD"

mkdir -p ~/.local/bin
install -m 0755 codex-rs/target/release/codex ~/.local/bin/codex-drg
~/.local/bin/codex-drg --version
```

Run `codex-drg` when you want the enhanced footer. Keeping it beside the official `codex` binary
makes rollback immediate and prevents an official update from silently overwriting the custom
build. The TOML status-line setting above is still required.

## Updating Codex

The verifier requires a clean checkout because it applies the patch in place. The TUI changes
often. When moving to a newer upstream release, create a fresh checkout, update the verifier's
expected commit, resolve any source changes deliberately, and run it again. Update the pinned
commit in this document only after those checks pass. Also review `model_maximum()` whenever the
group's model catalog changes.
