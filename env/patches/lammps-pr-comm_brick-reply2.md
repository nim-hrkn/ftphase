# Reply to sjplimp's question on lammps/lammps#5301 (why not set comm_forward to the max at init and pass isize) -- paste as a PR comment

Thanks for looking at it. You are right about the design: a style sets `comm_forward` to the largest width it will ever use and passes
a smaller `isize` per call. The problem is that `pair mliap/kk` cannot know that maximum at `init()`:

- With `pair_style mliap unified <model.pt>` the width is chosen by the user's Python model at run time. Each call to
  `forward_exchange(copy_from, copy_to, vec_len)` from Python (`src/KOKKOS/mliap_unified_couple_kokkos.pyx`) lands in
  `PairMLIAPKokkos::forward_comm()`, which does `comm_forward = vec_len = vl;` and then `comm->forward_comm(this)`
  (`src/KOKKOS/pair_mliap_kokkos.cpp`). The pair style never sets `comm_forward` in `init()`, so `Comm::init()` records 0 for it,
  and the first exchange with any width runs against buffers that were sized for other needs.
- A message-passing model may exchange several widths within one force call (node features of one layer, then another layer,
  then edge quantities in the reverse pass), and the widths depend on the model architecture: 64 to 256 doubles per atom in the
  models we ran (MatterSim, MACE-MPA-0, NequIP-OAM), and nothing in the `MLIAPUnified` interface tells the pair style the largest
  one in advance. A hard-coded value such as 256 would be an arbitrary bound: a model with wider features would overflow silently
  again, and every run would allocate 256 doubles per atom for the atom exchange even when the model needs 4.
- The Kokkos device path already handles this on demand: `CommKokkos::forward_comm_device(Pair*)` takes the maximum of
  `nsize*sendnum[iswap]` and `nsize*recvnum[iswap]` over the swaps on every call and calls `grow_buf_pair()` when it is larger
  than `max_buf_pair` (`src/KOKKOS/comm_kokkos.cpp`). That is why the GPU runs were correct. The host path in `CommBrick`/`CommTiled`
  (reached with a Kokkos Serial/OpenMP build, or with `comm host`) is the only place that still trusts the init-time value, so the
  PR makes the two paths consistent rather than introducing a new mechanism.

On the cost: in the current version the checks are two integer comparisons per call in `CommTiled` (against the bounds
`borders()` already keeps) and two per swap in `CommBrick`, i.e. at most ~12 comparisons per `forward_comm(Pair*)` call, next to
packing `nsize*sendnum` doubles per swap. The device path pays the same per-swap `MAX` loop today.

If you would rather keep the host path strictly init-sized, the alternative is an interface change in ML-IAP: have the unified
model declare its maximum exchange width when it is loaded (an attribute on the Python object that `PairMLIAPKokkos::init_style()`
copies into `comm_forward`/`comm_reverse`), and then pass `isize` per call. That changes the contract for every model exporter
(MACE, NequIP/Allegro, MatterSim, SevenNet), so I kept it out of this fix, but I can open it as a follow-up if you prefer that route.
