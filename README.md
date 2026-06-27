# DRGScripts

[![CI](https://github.com/DanaResearchGroup/DRGScripts/actions/workflows/ci.yml/badge.svg)](https://github.com/DanaResearchGroup/DRGScripts/actions/workflows/ci.yml)
[![secret scan](https://img.shields.io/badge/secret%20scan-gitleaks-success)](https://github.com/DanaResearchGroup/DRGScripts/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Shared utility scripts and notebooks for the **Dana Research Group** — tooling around
[RMG-Py](https://github.com/ReactionMechanismGenerator/RMG-Py),
[ARC](https://github.com/ReactionMechanismGenerator/ARC),
[T3](https://github.com/ReactionMechanismGenerator/T3),
[Arkane](https://reactionmechanismgenerator.github.io/RMG-Py/users/arkane/index.html),
and [Cantera](https://cantera.org/) for building chemical kinetic models and analyzing them.

Most scripts assume you already have RMG-Py / ARC / T3 installed and on your `PYTHONPATH`
(see [bashrc/](bashrc/.bashrc) for the typical environment aliases).

## What's in here

| Path | What it does |
|------|--------------|
| [`ARC/`](ARC/) | Notebooks that generate ARC input files — from a SMILES list, from a Chemkin model (GAV species), or from an Arkane/Explorer input. Includes [`ARC/CLAUDE.md`](ARC/CLAUDE.md), a guide for using Claude Code inside the ARC repo. |
| [`Kinetics_lib/`](Kinetics_lib/) | `K_extract.py` — build a non-pressure-dependent RMG kinetic library from literature rate data in CSV. |
| [`Pdep/`](Pdep/) | `K_Pdep_extract.py` — build a pressure-dependent (`PDepArrhenius`) RMG kinetic library from CSV. |
| [`Cantera/ROP/`](Cantera/ROP/) | `ROP.ipynb` — rate-of-production analysis on a Cantera mechanism. |
| [`FluxDiagrams/JSR/`](FluxDiagrams/JSR/) | Generate annotated reaction-flux diagrams (with molecule images) for a JSR simulation. |
| [`kinetics/`](kinetics/) | Notebooks comparing reactions against RMG-database estimates via ARC's functions. |
| [`Servers/`](Servers/) | Per-server (Atlas / Azure / Zeus) ARC & T3 `settings.py`, `submit.py`, and submit-script templates. **Placeholders only** — copy into `~/.arc` / `~/.t3` and fill in your own values. |
| [`bashrc/`](bashrc/.bashrc) | Example `.bashrc` aliases for the RMG / ARC / T3 workflow. |
| [`data/`](data/) | Shared reference data used by some of the notebooks. |

## Usage notes

- **Kinetic library extraction** (`Kinetics_lib/`, `Pdep/`): drop your `smiles*.csv` and
  `kinetics*.csv` inputs into the script's `files/` folder, edit the library metadata at the
  bottom of the script, then run `python K_extract.py` / `python K_Pdep_extract.py`. The
  output `reactions.py` is a ready-to-use RMG kinetics library.
- **Notebooks**: open with Jupyter from the notebook's own directory; paths are relative to
  it. Edit the clearly-marked input paths/placeholders at the top of each notebook.
- **Server configs** (`Servers/`): never edit the repo copies with real values. Copy the
  relevant `settings.py` / `submit.py` into your home `~/.arc` (or `~/.t3`) and fill in your
  username, server address, and key path there.

## Contributing

- Branch off `main` and open a pull request; don't push directly to `main`.
- **CI runs on every PR** (see badges above):
  - a **Python lint**: `python -m compileall` byte-compiles all scripts, then
    [ruff](https://github.com/astral-sh/ruff) fails only on genuine errors (syntax
    errors, undefined names) — style is intentionally not enforced;
  - a **[gitleaks](https://github.com/gitleaks/gitleaks) secret scan**.
- **Never commit real secrets.** Server settings here are placeholders; keep real
  credentials in your local `~/.arc` / `~/.t3`.
- **Clear notebook outputs before committing** to avoid leaking local paths/usernames and
  bloating the repo:
  ```bash
  jupyter nbconvert --clear-output --inplace path/to/notebook.ipynb
  ```

## License

[MIT](LICENSE) © DanaResearchGroup
