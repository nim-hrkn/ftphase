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

Still open: multi-rank (`forward_exchange`) is untested; cuEquivariance is not installed; the WorkChain still uses `pair_style mace`.
