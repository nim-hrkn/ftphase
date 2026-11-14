<!-- Draft reply 4 to sjplimp's comment of 2026-11-13 15:39 UTC on lammps/lammps PR #5301
     (https://github.com/lammps/lammps/pull/5301#issuecomment-6857669959). Short acknowledgement before the
     implementation. Not posted by Claude; the user posts it. Text to post starts below this comment. -->

Thanks, that works for me, and it is cleaner than what I proposed: the other pair styles keep the unchanged
`forward_comm()`/`reverse_comm()`.

I will update this PR accordingly:

- restore `forward_comm(Pair *)` and `reverse_comm(Pair *)` in CommBrick/CommTiled to what is in develop;
- add `forward_comm_dynamic(Pair *, int)` and `reverse_comm_dynamic(Pair *, int)` (declared in `Comm`, implemented in
  CommBrick and CommTiled) that take the width of the call and grow the buffers when needed;
- make `pair mliap/kk` the only caller.

I will rerun the tests from my previous comment (exchange widths up to 704, brick and tiled, 1 and 4 ranks, AddressSanitizer,
the MLIP models, `examples/melt`) and push in the next few days. If you prefer other names or signatures for the two methods,
please tell me.

For step (2) I will take up `comm_width` with the MLIP package maintainers and come back with a separate PR.
