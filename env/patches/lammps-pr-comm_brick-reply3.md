<!-- Draft reply to sjplimp's comment of 2026-11-11 on lammps/lammps PR #5301.  Written 2026-11-12 (third revision, with the GPU and develop results).
     User's decisions: ask for the current PR as an interim fix (admittedly awkward); show plan B at the same time; state the NequIP 704 fact;
     transition period with a warning for models that do not declare the width.
     Numbers: env/lammps-cpu-mliap-width/README.md, env/lammps-cpu-mliap-width*/test/run_tests.out, env/lammps-gpu-mliap-width/test/gpu_width.31685.out.
     Before posting: push the branch mliap-declare-comm-width-develop to the fork (not pushed yet). -->

Thanks, I agree with the diagnosis: the comm size should come from pair mliap (ultimately from the model), not from extra logic in
CommBrick/CommTiled. I implemented that route to see what it takes, and I would like to propose getting there in steps.

**What I tried (the model declares its width).** Branch `mliap-declare-comm-width-develop` on my fork (3 commits on top of the
base of this PR, 8 files; the same change on `stable_30Sep2026` for testing):

- `MLIAPUnified.__init__()` gets an optional `comm_width`; `MLIAPDummyModel` carries it (0 = not declared); both Cython couplings
  read it with `getattr`, so models pickled before the change still load.
- `PairMLIAPKokkos::settings()` sets `comm_forward = comm_reverse =` the declared width right after the unified model is built,
  or a default (256, the value you suggested) with a one-time warning when the model declares nothing. It has to be
  `settings()`, not `init_style()`: `PairHybrid::flags()` collects the sub-styles' comm sizes when the hybrid style is created,
  and with `init_style()` a `hybrid/scaled` run still overflowed.
- `forward_comm()`/`reverse_comm()` no longer overwrite `comm_forward`; a larger width stops with an error that names
  `comm_width`, and the actual width is passed as `isize`. The check is made against what `Comm::init()` allocated for; for that
  I added two read-only accessors (`get_maxforward()`, `get_maxreverse()`) to `comm.h`, since the members are protected. The comm
  loops and the allocation are untouched, and the accessors can go if you prefer the check against `comm_forward` only.

Without this PR's CommBrick/CommTiled changes this works on the host path (Kokkos Serial, `-k on t 1 -sf kk`, 1 and 4 MPI
ranks, brick and tiled, develop and `stable_30Sep2026`): an exchange-only test model passes for widths 4/128/256, 300 passes when
the model declares 512, and an undeclared 300 or a declared-32-used-64 stops with the error instead of a segfault. On the GPU
device path the energies are identical to the current build. `comm_width = 0` is a valid declaration for models that never
exchange (the bundled `MLIAPUnifiedLJ` now sets it, so `examples/mliap/in.mliap.unified.lj.Ar` runs without the warning and
reproduces its reference log, plain and with Kokkos, 1 and 4 ranks). `examples/melt` (brick and tiled) reproduces its reference
log; `make check-whitespace`, `check-permissions`, `check-homepage` and `check-errordocs` pass.

I also ran the exchange-only model under AddressSanitizer (widths 4/32/128/256, 300 declared 512, 704 declared 704; brick and
tiled; 1 and 4 ranks): with the `comm_width` branch all 24 runs are clean; with the unmodified `stable_30Sep2026` 18 of the 24
report a heap-buffer-overflow in `PairMLIAPKokkos` (everything from width 128 up, and width 32 with `comm_style tiled`), while
width 4 and width 32 with brick happen to fit.

**The problem with a default.** The width is the length of the per-atom node features exchanged in a message-passing layer,
so it follows from the architecture of the model (number of channels, maximum angular momentum), not from the package. I
measured the largest width of each unified model I have by declaring a width and raising it to the value named in the error
until the run passed (GPU, 108-atom cell; with the final declaration every model reproduces the energies of a build that has
this PR, plain and under `hybrid/scaled` with `ufm`):

| package | model | largest exchange width | undeclared, default 256 |
|---|---|---|---|
| MatterSim | v1-1M | 128 | runs (warning) |
| MatterSim | v1-5M | 256 | runs (warning), exactly at the limit |
| NequIP | OAM-S | 320 | stops with the width error |
| NequIP | OAM-M | 480 | stops |
| NequIP | OAM-L (OpenEquivariance and plain export) | **704** | stops |
| SevenNet | 7net-0 (OpenEquivariance export) | 480 (128 in an earlier layer) | stops |
| MACE | MPA-0 medium (e3nn and cuEquivariance export) | 512 | stops |

The width changes with the size of the model inside one package (NequIP 320/480/704, MatterSim 128/256) and between layers of
one model (SevenNet-0 128 and 480); it did not change with the export variant of the same model. With a default of 256, six
of these eight exports stop until their exporter declares the width, and a default that fits today's model of a package gives
no guarantee for the next one. The exporters live in the MLIP packages (mace, nequip, sevenn, mattersim), not in LAMMPS, and
every existing `.pt` file would have to be re-exported. Any default is a guess about models LAMMPS cannot see: too small and
existing models stop working, large enough for all of them and every run pays for buffers sized for the worst case.

**Proposal.**

1. For the November release, take this PR as an interim fix. I know it is awkward — it puts a size check in a place that is
   designed not to need one — but it is the only variant that makes every existing unified model run on the host path without
   touching the MLIP packages. At present the host path of `pair mliap/kk` corrupts the heap for any width above what
   `Comm::init()` happened to allocate, and a run does not always crash (see the AddressSanitizer runs above).
2. Introduce `comm_width` in the `MLIAPUnified` interface as above, as the documented way for a model to state its width.
   A model that does not declare it keeps working, but pair mliap prints a warning once when the model is loaded, saying that
   the declaration will become mandatory, so that users and the MLIP package maintainers have a transition period. Exporters
   should assign `self.comm_width = ...` rather than pass it to `super().__init__()`, so that the same exporter also works with
   an older `lammps` Python package. I can open the corresponding issues/PRs for the exporters.
3. After that period, make the declaration mandatory (the warning becomes an error) and remove the growth checks of this PR
   again. I can prepare that PR as well.

If you would rather not carry the interim checks at all, I can replace this PR with the `comm_width` branch right away; in that
case the default would have to be at least 704 (I would suggest 1024) for the models above to keep working until their
exporters are updated, and I would appreciate your view on which default is acceptable.
