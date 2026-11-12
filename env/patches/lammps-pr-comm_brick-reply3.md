<!-- Draft reply to sjplimp's comment of 2026-11-11 on lammps/lammps PR #5301.  Written 2026-11-12.
     User's decision: ask for the current PR as an interim fix (admittedly awkward), show plan B at the same time, state the NequIP 704 fact.
     Numbers: env/lammps-cpu-mliap-width/README.md (CPU, stable_30Sep2026).  GPU / develop results are added below when the runs finish. -->

Thanks, I agree with the diagnosis: the comm size should come from pair mliap (ultimately from the model), not from extra logic in
CommBrick/CommTiled. I tried that route to see what it takes, and I would like to propose doing it in two steps.

**What I tried (the "declare the width" route).** Branch `mliap-declare-comm-width` on my fork, one commit, 6 files, +42/−6,
CommBrick/CommTiled untouched:

- `MLIAPUnified.__init__()` gets an optional `comm_width`; `MLIAPDummyModel` carries it (0 = not declared); both Cython couplings
  read it with `getattr`, so models pickled before the change still load.
- `PairMLIAPKokkos::settings()` sets `comm_forward = comm_reverse =` the declared width right after the unified model is built,
  or a default (256, the value you suggested) when the model declares nothing. It has to be `settings()`, not `init_style()`:
  `PairHybrid::flags()` collects the sub-styles' comm sizes when the hybrid style is created, and with `init_style()` a
  `hybrid/scaled` run still overflowed.
- `forward_comm()`/`reverse_comm()` no longer overwrite `comm_forward`; a larger width stops with an error that names
  `comm_width`, and the actual width is passed as `isize`.

On the unpatched `stable_30Sep2026` (Kokkos Serial, `-k on t 1 -sf kk`, 1 and 4 MPI ranks, brick and tiled) this works: an
exchange-only test model passes for widths 4/128/256, 300 passes when the model declares 512, and an undeclared 300 gives the
error instead of a segfault. MatterSim (undeclared, fits in 256) gives the same energies as with this PR, alone and under
`hybrid/scaled` with `ufm`.

**The problem with a default.** The width is not small for every model: NequIP-OAM-L exchanges **704** values per atom, so with
a default of 256 it stops with the new error until its exporter declares the width (with `comm_width = 704` written into the
pickle it runs and reproduces the energies of this PR, plain, `hybrid/scaled` and tiled). The exporters live in the MLIP
packages (mace, nequip, sevenn, mattersim), not in LAMMPS, and every existing `.pt` file would have to be re-exported. Any
default is a guess about models LAMMPS cannot see: too small and existing models stop working, large enough for all of them
and every run pays for buffers sized for the worst case.

**Proposal.**

1. For the November release, take this PR as an interim fix. I know it is awkward — it puts a size check in a place that is
   designed not to need one — but it is the only variant that makes every existing unified model run on the host path without
   touching the MLIP packages, and it costs one integer comparison per pair comm call when the width does not grow. At present
   the host path of `pair mliap/kk` corrupts the heap for any width above what `Comm::init()` happened to allocate.
2. Introduce `comm_width` in the `MLIAPUnified` interface as above, as the documented way for a model to state its width, and
   ask the MLIP packages to set it in their exporters.
3. Once the exporters do, make the declaration mandatory and remove the growth checks of this PR again (a later release; I can
   prepare that PR and the notes for the package maintainers).

If you would rather not carry the interim checks at all, I can replace this PR with the `comm_width` branch right away; in that
case I would suggest a default of at least 1024 so that the NequIP models keep working until their exporter is updated, and I
would appreciate your view on which default is acceptable.
