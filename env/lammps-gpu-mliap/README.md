# env/lammps-gpu-mliap — LAMMPS 30Sep2026 + KOKKOS/CUDA + ML-IAP(Python) for libtorch MLIPs in calphy (2026-10-30)

`bin/lmp_gpumliap` = the `env/lammps-gpu` build (stable_30Sep2026, KOKKOS/CUDA sm_86, ML-PACE, ML-SNAP,
`hybrid/scaled/kk`, `ufm`) plus `ML-IAP` with `MLIAP_ENABLE_PYTHON` and `PYTHON`, built as a shared library
(`lib/liblammps_gpumliap.so`, rpath `$ORIGIN/../lib`). Source tree: `../lammps-gpu/src` (shared). `build.sh` has the flags.

Why: `pair_style mliap unified <model.pt> 0` runs a Python ML model *inside* LAMMPS. With `-k on g 1 -sf kk` the Kokkos
coupling (`mliap_unified_couple_kokkos`) hands the neighbour data to the model as cupy/torch GPU arrays and offers
`forward_exchange` for message-passing layers (multi-rank ghosts), so MACE, SevenNet, MatterSim, NequIP, MatGL can run on
the GPU **without a model-specific LAMMPS fork**, and `hybrid/scaled/kk` (calphy's reversible scaling, UFM switching) works.

## Verified (Slurm 22988, GPU held exclusively, RTX 3060; `test/bench.sbatch`, `test/bench.22988.out`)

Correctness (108-atom Al-Li cell `test/conf.data`, `run 0`): plain / `hybrid/scaled/kk v_lam mliap` λ=1 / λ=1.222 / 0.7 model + 0.3 ufm

| model | plain pe (eV), press (bar) | λ=1 | λ=1.222 | reference pair style |
|---|---|---|---|---|
| MACE-MPA-0 fp64 (`potentials/mace/macempa0mediummodel.model-mliap_lammps.pt`) | −403.92008, 607.25954 | identical | ×1.222 exactly | `pair_style mace`: −403.92008, 607.2595 |
| MACE-MPA-0 fp32 (`...-mliap_lammps-f32.pt`) | −403.92018, 607.457 | identical | ×1.222 | `pair_style mace` fp32: −403.92018 |
| SevenNet-0 OEQ (`potentials/sevenn/7net-0_mliap_oeq.pt`) | −401.71027, 65.576 | identical | ×1.222 | `e3gnn` (oeq): −401.71027, 65.562 |
| SevenNet-0 without OEQ (`7net-0_mliap.pt`) | **crash** (`free(): corrupted unsorted chunks` in torch autograd backward, inside the embedded interpreter) | | | works when env/torch's python drives the conda liblammps |

The ufm mix gives pe = 0.7·E_model + 0.53 eV (UFM repulsion) and a non-zero pressure, i.e. the virial is passed through
`hybrid/scaled/kk` (unlike SevenNet's `e3gnn`, which returns zero pressure under `hybrid/scaled`, see `docs/mlip.html` §5).

Speed (s/step, 100 NVE steps, 1 MPI rank, 4 CPUs, exclusive GPU):

| | 108 atoms | 256 atoms |
|---|---|---|
| MACE-MPA-0 fp64 — ML-IAP / `pair_style mace` | 0.391 / 0.467 | 0.944 / 1.036 |
| MACE-MPA-0 fp32 — ML-IAP / `pair_style mace` | **0.037** / 0.098 | **0.090** / 0.177 |
| SevenNet-0 OEQ — ML-IAP / `e3gnn` | 0.0111 / **0.0076** | 0.0132 / **0.0095** |
| SevenNet-0 no OEQ — `e3gnn` | 0.0368 | — |

MACE fp32 is 2-2.6× faster through ML-IAP than through the ACEsuit `pair_style mace`; SevenNet is 1.4× slower than its own
`e3gnn` + OEQ. (Numbers measured earlier outside Slurm while an AiiDA calphy job held the GPU are not comparable.)

## How to run

```
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1            # the models are pickled Python objects
PYTHONHOME=<project>/env/mace  bin/lmp_gpumliap -k on g 1 -sf kk -pk kokkos newton on neigh half -in in.lmp   # MACE
PYTHONHOME=<project>/env/torch bin/lmp_gpumliap -k on g 1 -sf kk -pk kokkos newton on neigh half -in in.lmp   # SevenNet
# in.lmp:  atom_modify map yes / newton on / pair_style mliap unified /abs/path/model.pt 0 / pair_coeff * * Al Li
```

`bin/lmp_mliap_mace.sh` and `bin/lmp_mliap_sevenn.sh` set these variables (use them as calphy's `lammps_executable`).
The embedded interpreter is libpython 3.12.15 (resolved from env/ftphase at run time, linked against env/torch; same
version); `PYTHONHOME` selects which env's packages it sees. Both env/mace and env/torch therefore need: `cupy-cuda12x`
(14.2.0, installed), the pure-Python `lammps` package (`pip install ../lammps-gpu/src/python`, for the base class
`lammps.mliap.mliap_unified_abc.MLIAPUnified` of the pickled wrappers; installed), and the model's own package.

Model export:
- MACE: `mace_create_lammps_model --format mliap` (mace-torch 0.3.16) forces an e3nn→cuEquivariance conversion that fails
  without cuequivariance ("Unexpected key(s) ... symmetric_contractions.weight"); `test/mace_to_mliap.py <model> [float32]`
  does the same export without it.
- SevenNet: `PYTHONPATH=<a lammps python package> sevenn get_model 7net-0 -mliap -oeq -o 7net-0_mliap_oeq` (needs a visible
  GPU for the OEQ check). Always use the `-oeq` export here (the plain one crashes, see above).

## Build pitfalls (three attempts)
1. `set -u` before `conda activate` kills the script (the cuda-nvcc activate hook reads unset variables).
2. With `BUILD_SHARED_LIBS=on` CMake links through a response file `@objects1.rsp`, which Kokkos' `nvcc_wrapper` cannot
   expand ("cannot specify '-o' with '-c' ... with multiple files") → `CMAKE_CXX_USE_RESPONSE_FILE_FOR_{OBJECTS,LIBRARIES}=OFF`.
3. With env/ftphase activated FindPython picked ftphase's libpython → explicit `Python_ROOT_DIR/Python_LIBRARY/Python_INCLUDE_DIR`;
   and the installed binary needs `CMAKE_INSTALL_RPATH='$ORIGIN/../lib'` (no patchelf here).

## calphy run (Slurm 22990, 2026-10-30, `ftphase/examples/calphy_mliap_mace/`)

`calculation_block(gpu=True, lammps_executable=bin/lmp_mliap_mace.sh, pair_style="mliap unified <f32 model> 0", pair_coeff="* * Al Li")`,
mode ts, 256 Al atoms 1100 -> 700 K, same settings as the example-8 job pk 4356 (`pair_style mace` fp32): G(1100 K) −4.187613 vs
−4.187605 eV/atom, 700-1000 K within +0.10..+0.15 meV/atom (independent seeds; liquid run-to-run spread is 0.1-0.5 meV/atom);
0.085 s/step vs 0.157, calphy wall 5.14 h vs 9.57 h. No `atom_modify map yes` needed. Details in that folder's README.

The WorkChain (`run_aiida.py --mlip mace-mpa-0`) uses this route since 2026-10-30 (`calphy_gpu: True`; old route `--mlip mace-mpa-0-pairstyle`;
smoke pk 6160). Deploying to another calphy host means copying `bin/` + `lib/` and adding cupy-cuda12x + the lammps python package to its env/mace.

## MatterSim (Slurm 22999, 2026-10-30, `test/bench_mattersim.sbatch`, `test/bench_mattersim.22999.out`)

mattersim 1.2.5 (pip, in env/torch; its PyPI torchvision 0.26.0 breaks torch 2.11.0 with "operator torchvision::nms does not exist",
reinstall torchvision/torchaudio from the cu128 index) ships the official ML-IAP wrapper `mattersim.lammps.mliap_wrapper.MatterSimMLIAP`
(M3GNet, fp32, forward/reverse exchange, `torch.compile` on the GPU by default). Export: `test/mattersim_to_mliap.py` ->
`potentials/mattersim/mattersim-v1.0.0-{5M,1M}_mliap{,_nocompile}.pt`; wrapper `bin/lmp_mliap_mattersim.sh` (PYTHONHOME env/torch).
Correctness (108-atom `test/conf.data`, `run 0`): 5M pe −403.17578 eV vs ASE calculator −403.17511 (6 µeV/atom), press −3403.39 vs −3403.49 bar;
1M −401.87122 vs −401.87140; `hybrid/scaled/kk` λ=1 identical, λ=1.222 exact, 0.7 model + 0.3 ufm sane. No `atom_modify` needed.

| s/step | 108 atoms | 256 atoms |
|---|---|---|
| MatterSim-v1 5M (compiled; first launch +20 s compile) | 0.018 | 0.040 |
| MatterSim-v1 5M (nocompile) | 0.024 | — |
| MatterSim-v1 1M (compiled) | 0.012 | 0.015 |
| MACE-MPA-0 fp32 ML-IAP / SevenNet-0 OEQ ML-IAP (for reference) | 0.037 / 0.011 | 0.090 / 0.013 |

WorkChain: `run_aiida.py --mlip mattersim-5m|mattersim-1m` (`qha_calculator: mattersim` -> `MatterSimCalculator(load_path=<.pth>)` in
`ftphase/src/ftphase/aiida/runners.py`; the runner now casts energies to float because MatterSim returns numpy float32, which json cannot
serialise: smoke pk 6231 failed on that, pk 6244 resubmitted). The wrapper sets `TORCHINDUCTOR_FX_GRAPH_CACHE/AUTOGRAD_CACHE=1` and
`TORCHINDUCTOR_CACHE_DIR=~/.cache/torchinductor_mattersim` so calphy's ~20 LAMMPS launches per job share the compile cache.

## NequIP-OAM-L 0.1 (Slurm 23000, 2026-10-30, `test/bench_nequip.sbatch`, `test/bench_nequip.23000.out`)

nequip 0.19.1 + nequip-allegro 0.8.3 (pip, env/torch; adds lightning, torch/e3nn/sevenn/mattersim unchanged). Model choice and sources:
`ftphase/examples/mlip_bench/nequip_allegro_survey.md` (MIR group package files, CC-BY-4.0, Zenodo 18775904; copy in
`potentials/nequip/NequIP-OAM-L-0.1.nequip.zip`, cache `~/.nequip/model_cache/`). Export (CPU, ~1 min each):
`nequip-prepare-lmp-mliap nequip.net:mir-group/NequIP-OAM-L:0.1 X.nequip.lmp.pt [--modifiers enable_OpenEquivariance] [--no-compile]`
-> `potentials/nequip/NequIP-OAM-L-0.1{,-nocompile,-plain}.nequip.lmp.pt` (117 MB each: the package is embedded). Wrapper `bin/lmp_mliap_nequip.sh`
(PYTHONHOME env/torch, inductor cache dir `~/.cache/torchinductor_nequip`). Model: r_c 6 Å, 6 layers, float32, ZBL on.

Correctness (108-atom `test/conf.data`, `run 0`): ML-IAP pe −404.08095 eV, press 2017.74 bar; the package model evaluated eagerly in Python
(`test/nequip_ref_eager.py`, nequip data pipeline, CPU) gives −404.08091 eV, 2017.68 bar (0.4 µeV/atom). All three exports agree to 5e-5 eV;
`hybrid/scaled/kk` λ=1 identical, λ=1.222 exact, 0.7 model + 0.3 ufm sane. `atom_modify map yes` is in `in.kk` (nequip docs use it).

| s/step | 108 atoms | 256 atoms |
|---|---|---|
| OpenEquivariance, compiled (first launch ~60 s, warm ~40 s per LAMMPS start) | 0.0125 | 0.029 |
| OpenEquivariance, eager | 0.016 | — |
| plain e3nn | 0.077 | 0.198 |
| MatterSim 5M / MACE-MPA-0 fp32 / SevenNet-0 OEQ (ML-IAP, reference) | 0.018 / 0.037 / 0.011 | 0.040 / 0.090 / 0.013 |

ASE calculator: nequip >= 0.7 only loads AOTInductor-compiled models (`nequip-compile --mode aotinductor --target ase`). The GPU compile
needs `cuda.h` on `CPATH` (`env/torch/include`; the sbatch sets it now, the first run failed without it); the CPU compile fails with an inductor
codegen error under g++ 13 ("'decltype' evaluates to 'float'", torch 2.11), so the CPU reference uses the eager path above. The WorkChain
runner (`qha_calculator: nequip`) compiles the package for the job's device at start (~2 min) unless it is given a `.nequip.pt2`;
`run_aiida.py --mlip nequip-oam-l` (dry run OK, not yet run).

## cuEquivariance for MACE (Slurm 23174, 2026-11-03, `test/bench_cueq.sbatch`, `test/bench_cueq.23174.out`)

`cuequivariance` / `cuequivariance-torch` / `cuequivariance-ops-torch-cu12` 0.13.0 in env/mace (no dependency conflicts). With them the
official exporter works: `mace_create_lammps_model <copy of the .model> --format mliap --dtype float32` ->
`potentials/mace/macempa0mediummodel-cueq.model-mliap_lammps.pt` (the tensor products become `cuequivariance_torch` modules; the file is
named after the input model, so export from a copy to keep the e3nn files). GPU held exclusively, 108-atom cell `run 0`: pe −403.92018 eV,
press 607.453 bar = the e3nn export (−403.92018, 607.451); `hybrid/scaled/kk` λ=1 and the ufm mix identical to the e3nn run.

| s/step | 108 atoms | 256 atoms |
|---|---|---|
| MACE-MPA-0 fp32, cuEquivariance ML-IAP | 0.0173 | 0.0198 |
| MACE-MPA-0 fp32, e3nn ML-IAP | 0.0371 | 0.0900 |
| MACE-MPA-0 fp32, `pair_style mace` (lmp_mace) | 0.098 | 0.177 |

4.5x faster than the e3nn ML-IAP export at 256 atoms (9x the original pair style); the WorkChain's `mace-mpa-0` entry uses the cueq file
since 2026-11-03. cueq kernels are CUDA-only: for the CPU use `-mliap_lammps-f32-cpu.pt`.

Multi-rank `forward_exchange`: verified on the CPU build with 4 and 12 ranks (env/lammps-cpu-mliap); multi-GPU untested (one GPU per host).
