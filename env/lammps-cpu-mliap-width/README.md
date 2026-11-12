# env/lammps-cpu-mliap-width — trial of "plan B" for lammps/lammps PR #5301 (2026-11-12)

S. Plimpton's review (2026-11-11): the buffer overrun is not a CommBrick/CommTiled problem; pair mliap (or its model) should
provide the comm size at init.  This build tests that route on the unpatched release.

* Source: `env/lammps-gpu/worktree-mliap-width` (branch `mliap-declare-comm-width`, from `stable_30Sep2026`, **without** the
  CommBrick/CommTiled patch).  One commit (beefce3aa4), 6 files, patch copy `env/patches/lammps-30Sep2026-mliap-declared-comm-width.patch`.
  - `MLIAPUnified.__init__(..., comm_width=None)`; `MLIAPDummyModel::comm_width` (0 = not declared); both Cython couplings read
    it with `getattr(unified, 'comm_width', None)` so models pickled earlier still load.
  - `PairMLIAPKokkos::settings()`: right after `build_unified()`, `comm_forward = comm_reverse =` declared width, or the default
    256 for undeclared models.  It has to be `settings()`, not `init_style()`: `PairHybrid::flags()` collects the sub-styles'
    comm sizes when the hybrid style is set up (the first version set it in `init_style()` and segfaulted under hybrid/scaled).
  - `forward_comm()` / `reverse_comm()` no longer overwrite `comm_forward`; a width above the maximum is an error naming
    `comm_width`; the call passes the actual width as `isize` (`comm->forward_comm(this, vl)`).
* Build: `build.sh` (copy of env/lammps-cpu-mliap/build.sh without the patch step) -> `bin/lmp_cpumliapw` (Kokkos Serial).
* Tests: `test/run_tests.sh` -> `test/run_tests.out` (`-k on t 1 -sf kk`, 108-atom Al-Li cell).

| test | result |
|---|---|
| exchange-only model (`test/exch_model.py`), widths 4 / 128 / 256, brick and tiled, 1 and 4 ranks | all 12 pass (ghost rows filled; reverse sums exact on 1 rank) |
| width 300 undeclared; width 64 declared 32 | clean error "exchange width N exceeds the maximum M set at init: declare comm_width" (8 of 8) |
| width 300 declared 512 | pass (4 of 4) |
| MatterSim-5M, undeclared (default 256 suffices), 1 / 4 ranks, plain and hybrid/scaled with ufm, tiled | energies = the patched-Comm build (-403.17566 / -403.1757 eV; hybrid -281.68908 / -281.6891) |
| NequIP-OAM-L, undeclared | error: its exchange width is **704** > 256 |
| NequIP-OAM-L with `comm_width = 704` written into the pickle (`test/nequip_declared704.pt`, not committed) | energies = the patched-Comm build (-404.08091 / -404.08096 eV; hybrid -282.32276 / -282.32279; tiled -404.08096) |

Findings: the route works without touching Comm, including hybrid/scaled and tiled.  A default alone cannot cover existing
models (NequIP-OAM-L needs 704), so either the default is raised (e.g. 1024) or the exporters must declare the width.
Not tested here: the GPU device path (it grows its own buffers per call and never overflowed), MACE on the CPU, the develop branch.

## Second step (2026-11-12 afternoon): warning, check against Comm's sizes, develop port

* Commit 2 on both branches: an undeclared model prints one warning on rank 0 when it is loaded ("does not declare comm_width:
  using 256 ... will become mandatory"), and `forward_comm()`/`reverse_comm()` compare the width with
  `MIN(comm_forward, comm->get_maxforward())` (resp. reverse), i.e. with what `Comm::init()` really allocated for.
  `maxforward`/`maxreverse` are protected in `Comm`, so `comm.h` gained two read-only accessors (4 lines; no change to the comm
  loops or allocation).  Dropping this strengthening restores "Comm untouched".
* develop port: `env/lammps-gpu/worktree-mliap-width-develop`, branch `mliap-declare-comm-width-develop` (from upstream develop
  7dbed49448, the base of PR #5301); the release commit cherry-picked without conflicts.  Patch `env/patches/lammps-develop-mliap-declared-comm-width.patch`.
  Build `env/lammps-cpu-mliap-width-develop/` (`lmp_cpumliapwd`).
* `test/run_tests.sh` on both CPU builds after commit 2 (`run_tests.out` in each folder): identical outcome to the table above -
  16 exchange cases pass, 8 stop with the width error, MatterSim-5M and NequIP-OAM-L (declared 704) reproduce the reference
  energies on 1 / 4 ranks, plain, hybrid/scaled and tiled; undeclared NequIP-OAM-L stops with "width 704 exceeds the maximum 256".
* GPU device path: `env/lammps-gpu-mliap-width/` (`lmp_gpumliapw`, same source as the release CPU build), comparison job
  `test/gpu_width.sbatch` against the production `lmp_gpumliap` on mygarden6 (Slurm 31685).

## GPU device path (Slurm 31685 on mygarden6, `env/lammps-gpu-mliap-width/test/gpu_width.31685.out`)

`lmp_gpumliapw` (declared-width build) against the production `lmp_gpumliap` (patched Comm), in.kk v0 (plain) / v3 (0.7 model + 0.3 ufm, hybrid/scaled/kk), 108 atoms:

| model | production | declared-width build |
|---|---|---|
| MatterSim-5M (undeclared) | -403.17578 / -281.68916 | -403.17578 / -281.68916 (warning) |
| MACE-MPA-0 cueq (undeclared) | -403.92018 / -282.21024 | error: width **512** > 256 |
| SevenNet-0 OEQ (undeclared) | -401.71027 / -280.6633 | error: width **480** > 256 |
| NequIP-OAM-L OEQ (undeclared) | -404.08095 / -282.32278 | error: width **704** > 256 |
| NequIP-OAM-L OEQ, comm_width = 704 | -404.08096 / -282.32278 | -404.08095 / -282.32279 |

A default of 256 covers only MatterSim among the four models; the default would have to be >= 704.

## Largest exchange width per model (Slurm 31686, `env/lammps-gpu-mliap-width/test/gpu_declared.sbatch` / `.31686.out`)

Declare 1, run, raise the declaration to the width named in the error, repeat until the run passes (the error names the first
exchange that exceeds the limit, not the maximum): MatterSim-5M 256; SevenNet-0 OEQ 128 then 480; MACE-MPA-0 cueq 512;
NequIP-OAM-L OEQ 704.  With the final declaration all four give the production energies, plain and hybrid/scaled/kk
(-403.17578 / -281.68916; -401.71027 / -280.6633; -403.92017 / -282.21024; -404.08095 / -282.32278).

## Width vs model size and export variant (Slurm 31687, `test/gpu_sizes.sbatch` / `gpu_sizes.31687.out`, 1.5 h)

Largest exchange width: NequIP-OAM S / M / L = 320 / 480 / 704 (L plain export also 704); MatterSim 1M / 5M = 128 / 256;
MACE-MPA-0 medium e3nn-f32 and cuEquivariance exports both 512.  Every model reproduces the production energies once the
width is declared.  The width follows the model architecture: it changes with the model size inside a package, not with the
export variant.  (MACE small/large and SevenNet-MF-ompa have no ML-IAP export here and were not measured.)

## Regression, AddressSanitizer and commit 3 (2026-11-12 night)

* Commit 3 on both branches: `comm_width = 0` is a valid declaration ("no exchange"; undeclared is -1 internally) and the bundled
  `python/lammps/mliap/mliap_unified_lj.py` sets it, so models without exchange get no warning.  Branches now 3 commits, 8 files.
* Regression on the develop build (`env/lammps-cpu-mliap-width-develop/regress/`): `examples/melt` brick and tiled, 1 / 4 ranks,
  plain and Kokkos = reference log to all digits; `examples/mliap/in.mliap.unified.lj.Ar` 1 / 4 ranks, plain and Kokkos = reference
  log, no warning (run with `PYTHONPATH=<worktree>/python` so the embedded Python sees the updated LJ model);
  `make check-whitespace|check-permissions|check-homepage|check-errordocs` exit 0 (run with env/ftphase's python on PATH: needs yaml).
  `test/run_tests.sh` unchanged outcome (16 pass, 8 stop, MatterSim / NequIP energies).
* AddressSanitizer (`env/lammps-cpu-mliap-asan-b/` = plan B on stable_30Sep2026, `env/lammps-cpu-mliap-asan-stable/` = unmodified
  stable_30Sep2026 from `env/lammps-gpu/worktree-stable-asan`; `-fsanitize=address`, RelWithDebInfo; driver and output
  `env/lammps-cpu-mliap-asan-b/test/asan_tests.{sh,out}`): exchange-only model, widths 4 / 32 / 128 / 256, 300 declared 512,
  704 declared 704, brick and tiled, 1 and 4 ranks.  Plan B: 24 of 24 clean.  Unmodified: 18 of 24 heap-buffer-overflow in
  `PairMLIAPKokkos` (all widths >= 128, and width 32 with tiled); width 4 and width 32 with brick fit by chance.
  Pitfall: an ASan binary dies with SIGILL in OpenMPI's memory patcher (`mca_base_patcher_patch_apply_binary` -> libasan
  `mprotect`); run with `OMPI_MCA_memory=^patcher`.  In a script, call `env/ftphase/bin/mpirun` explicitly (plain `mpirun`
  resolved to Intel MPI and rejected `-x`).
