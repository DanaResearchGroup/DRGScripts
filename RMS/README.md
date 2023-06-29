# RMS — reactor simulation, ROP & flux diagrams

[`Constant T P ideal gas reactor.ipynb`](Constant%20T%20P%20ideal%20gas%20reactor.ipynb)
simulates a homogeneous, isothermal, isobaric (constant *T*, *P*) ideal-gas batch
reactor with [ReactionMechanismSimulator.jl](https://github.com/ReactionMechanismSimulator/ReactionMechanismSimulator.jl)
(RMS) and produces a **rate-of-production (ROP)** plot and a **reaction-flux diagram**.

RMS is a **Julia** package, so this is a Julia notebook — it does *not* run in the
Cantera/Python environment used by the rest of this repo (e.g. `Cantera/ROP`). The two
are complementary: reach for RMS when you want its native `getfluxdiagram` /
`plotrops` and its tight coupling to RMG mechanisms.

## Environment (one-time setup)

RMS installation details drift between releases; the
[RMS README](https://github.com/ReactionMechanismSimulator/ReactionMechanismSimulator.jl#installation)
is the authoritative source. The setup below is the common path.

1. **Install Julia** (1.9+ recommended) — e.g. via [`juliaup`](https://github.com/JuliaLang/juliaup).
   Download the installer, review it, then run it (rather than piping straight into a shell):
   ```bash
   curl -fsSL https://install.julialang.org -o install-julia.sh
   sh install-julia.sh
   ```
   See the [juliaup README](https://github.com/JuliaLang/juliaup#installation) for Windows
   and other install options.

2. **Install RMS and the packages this notebook uses** from a Julia REPL:
   ```julia
   using Pkg
   Pkg.add(["ReactionMechanismSimulator", "DifferentialEquations", "Sundials", "PyPlot"])
   ```

3. **Enable Chemkin input (optional).** To read RMG `chem_annotated.inp` +
   `species_dictionary.txt`, RMS calls RMG-Py through `PyCall`, so point PyCall at a
   Python that has `rmgpy` installed (e.g. this repo's `rmg_env` conda env):
   ```julia
   ENV["PYTHON"] = "/home/<you>/anaconda3/envs/rmg_env/bin/python"
   using Pkg; Pkg.build("PyCall")
   ```
   You can skip this if you only ever read native `.rms` files.

4. **Register the Jupyter Julia kernel** so this notebook opens with a Julia kernel:
   ```julia
   using Pkg; Pkg.add("IJulia")
   using IJulia; installkernel("Julia")
   ```

5. **Install Graphviz** (`dot`) — RMS renders the flux diagram with it:
   ```bash
   conda install -c conda-forge graphviz   # or: sudo apt install graphviz
   ```

## Getting a mechanism

Set `mech` in the notebook to a mechanism file (the default is a `path/to/mechanism.rms`
placeholder). RMS reads either:

- **A native RMS file** (`.rms` / `.yml`) — no Python needed. Set `mech` to it and leave
  `spc_dict = nothing`.
- **An RMG Chemkin pair** — `chem_annotated.inp` + `species_dictionary.txt` from any RMG
  job. Set `mech` to the `.inp` and `spc_dict` to the dictionary. On first read RMS caches
  a `<name>.rms` next to the `.inp`, which loads faster afterwards.

Species names in `initial_mole_fractions` and `rop_species` must match the labels used in
your mechanism (RMG-style, e.g. `NH3`, `O2`, `Ar`, `NO`).

Keep mechanism files outside the repo (or add them to `.gitignore`) — they are large,
run-specific inputs and should not be committed.

## Running

1. Open the notebook with a **Julia kernel** (JupyterLab/Notebook, or VS Code with the
   Julia extension).
2. Edit the **User inputs** cell — mechanism path, `T`, `P`, `max_time`, initial mole
   fractions, `rop_species`, and the flux-diagram time/tolerances.
3. Run all cells top to bottom.

Expected output: cell 6 shows the ROP plot for `rop_species`; cell 7 renders the flux
diagram at `flux_time`. The first run in a fresh Julia session is slow — RMS and its ODE
dependencies precompile.

## Notes

- First-call latency ("time to first plot") is a Julia trait, not an error — subsequent
  runs in the same session are fast.
- The stiff solver (`CVODE_BDF` from Sundials) with tight tolerances suits combustion
  kinetics; loosen `abstol`/`reltol` if a run is slow and you don't need that precision.
- Flux-diagram output empty or too dense? Adjust `flux_conc_tol` / `flux_rate_tol`.
