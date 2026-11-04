# Reply to the review comment on lammps/lammps#5301 (tiled communication) -- paste as a PR comment

Thanks, you are right: with `comm_style tiled` the same ML-IAP exchange overruns the tiled buffers. I reproduced it with the
`MLIAPUnified` exchange test on a 108-atom cell (`-k on t 1 -sf kk`, `comm_style tiled`): width 4 runs, width 256 segfaults on 1 and
4 MPI ranks with only the CommBrick change in place.

Pushed a second commit that adds the equivalent checks to `CommTiled::forward_comm(Pair *)` and `reverse_comm(Pair *)`
(which `CommTiledKokkos` also uses as its host fallback). They reuse the bounds `borders()` already keeps, once per call with the
actual width: forward comm grows `buf_send` to `nsize*smaxone` (one packed message) and `buf_recv` to `nsize*rmaxall` (all
messages of a swap at the `forward_recv_offset` positions); reverse comm grows them to `nsize*rmaxone` and `nsize*smaxall`.
This is the same pairing `borders()` uses with `maxforward`/`maxreverse`, so the `sendself` message (which also goes through
`buf_send`) is covered.

Verified with the same test on the patched build: `comm_style tiled`, widths 4 and 256, 1 and 4 ranks run and return the expected
ghost/reverse sums; a MatterSim ML-IAP model under `comm_style tiled` gives the same energy as with `comm_style brick`
(-403.17566 eV on 1 rank, -403.1757 eV on 4 ranks). `examples/melt` runs unchanged with brick and tiled (4 ranks) on the develop build;
`make check-whitespace` passes.
