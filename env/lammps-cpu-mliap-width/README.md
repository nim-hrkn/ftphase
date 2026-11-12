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
