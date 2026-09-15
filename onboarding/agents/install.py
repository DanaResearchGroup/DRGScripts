#!/usr/bin/env python3
"""Install the canonical group roles in Codex or OpenCode's native format."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections.abc import Callable


Renderer = Callable[[dict[str, str], str], str]


CODEX_MODELS = {
    "haiku": "gpt-5.6-luna",
    "sonnet": "gpt-5.6-terra",
    "opus": "gpt-6-astra",
    "fable": "gpt-5.6-sol",
}


def parse_role(path: pathlib.Path) -> tuple[dict[str, str], str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing frontmatter delimiter") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path}: invalid frontmatter line: {line}")
        metadata[key.strip()] = value.strip()
    for key in ("name", "description", "model", "effort"):
        if not metadata.get(key):
            raise ValueError(f"{path}: missing {key!r} frontmatter")
    return metadata, "\n".join(lines[end + 1 :]).strip() + "\n"


def render_codex(metadata: dict[str, str], body: str) -> str:
    model = CODEX_MODELS.get(metadata["model"])
    if model is None:
        raise ValueError(f"no Codex mapping for model alias {metadata['model']!r}")
    values = {
        "name": metadata["name"],
        "description": metadata["description"],
        "model": model,
        "model_reasoning_effort": metadata["effort"],
        "developer_instructions": body,
    }
    return "".join(f"{key} = {json.dumps(value)}\n" for key, value in values.items())


def render_opencode(metadata: dict[str, str], body: str) -> str:
    # Provider model IDs differ, so inherit the active OpenCode model by default.
    return (
        "---\n"
        f"description: {json.dumps(metadata['description'])}\n"
        "mode: subagent\n"
        "---\n\n"
        f"{body}"
    )


def client_configuration(client: str) -> tuple[pathlib.Path, Renderer, str]:
    if client == "codex":
        return pathlib.Path.home() / ".codex" / "agents", render_codex, ".toml"
    if client == "opencode":
        return pathlib.Path.home() / ".config" / "opencode" / "agents", render_opencode, ".md"
    raise ValueError(f"unsupported client {client!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client", choices=("codex", "opencode"))
    parser.add_argument("--output", type=pathlib.Path, help="override the native agent directory")
    args = parser.parse_args()

    source_dir = pathlib.Path(__file__).resolve().parent
    default_destination, renderer, suffix = client_configuration(args.client)
    destination = (args.output or default_destination).expanduser()
    destination.mkdir(parents=True, exist_ok=True)

    rendered = []
    for source in sorted(source_dir.glob("*.md")):
        metadata, body = parse_role(source)
        target = destination / f"{metadata['name']}{suffix}"
        rendered.append((target, renderer(metadata, body)))

    for target, _ in rendered:
        if target.exists():
            print(f"error: refusing to overwrite {target}", file=sys.stderr)
            return 1

    for target, content in rendered:
        target.write_text(content, encoding="utf-8")
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
