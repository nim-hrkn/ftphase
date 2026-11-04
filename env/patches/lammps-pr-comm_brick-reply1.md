# Reply to the review comment on lammps/lammps#5301 (tiled communication) -- paste as a PR comment

Thanks, you are right: with `comm_style tiled` the same ML-IAP exchange overruns the tiled buffers. I reproduced it with the
`MLIAPUnified` exchange test on a 108-atom cell (`-k on t 1 -sf kk`, `comm_style tiled`): width 4 runs, width 256 segfaults on 1 and
4 MPI ranks with only the CommBrick change in place.

Pushed a second commit (ff223ea) that adds the equivalent checks to `CommTiled::forward_comm(Pair *)` and `reverse_comm(Pair *)`
(which `CommTiledKokkos` also uses as its host fallback). Per swap, before the receives are posted:

- `buf_send` must hold one packed message, so it is grown to `nsize * max(sendnum[iswap][i])` over the swap's send partners
  (forward) or `nsize * max(recvnum[iswap][i])` (reverse);
- `buf_recv` holds all messages of the swap at `forward_recv_offset` / `reverse_recv_offset`, so it is grown to
  `nsize * sum(recvnum[iswap][i])` over the `nrecv` remote partners (forward) or `nsize * sum(sendnum[iswap][i])` over the `nsend`
  remote partners (reverse).

The `sendself` message goes through `buf_send` as well and is covered by the max over all `nsendproc`/`nrecvproc` partners.

Verified with the same test on the patched build: `comm_style tiled`, widths 4 and 256, 1 and 4 ranks run and return the expected
ghost/reverse sums; a MatterSim ML-IAP model under `comm_style tiled` gives the same energy as with `comm_style brick`
(-403.17566 eV on 1 rank, -403.1757 eV on 4 ranks). `examples/melt` runs unchanged with brick and tiled (4 ranks) on the develop build;
`make check-whitespace` passes.
