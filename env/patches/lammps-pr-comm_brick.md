# Draft for the LAMMPS pull request (branch `fix-pair-comm-buffer-growth-develop` of github.com/nim-hrkn/lammps -> lammps/lammps `develop`)

Title:

    Grow CommBrick buffers in forward_comm/reverse_comm(Pair *) for communication sizes set at call time

Body (paste into the PR form; the template's fixed sections are kept, the AI section is edited as the template asks):

---

**Summary**

`CommBrick::forward_comm(Pair *)` and `CommBrick::reverse_comm(Pair *)` pack `nsize*sendnum` doubles into `buf_send` and receive
`nsize*recvnum` doubles into `buf_recv` without checking the buffer sizes. The buffers are sized in `borders()` from `maxforward`
and `maxreverse`, which `Comm::init()` reads from `pair->comm_forward` / `pair->comm_reverse` at init time. A pair style that only
knows its communication width when it communicates overflows the heap. `pair mliap/kk` is such a style: its `forward_exchange()` /
`reverse_exchange()` set `comm_forward` / `comm_reverse` to the feature width of the Python ML-IAP model (64-256 for current
message-passing models such as MACE, NequIP or MatterSim) and then call `comm->forward_comm(this)` / `reverse_comm(this)`.
On the device path (`CommKokkos::forward_comm_device`) the Kokkos buffers are resized per call, so GPU runs were correct; on the
host path (a KOKKOS build with the Serial or OpenMP backend, or `package kokkos comm host`) the same models crashed with
`malloc(): unaligned tcache chunk detected`, segmentation faults inside the model, or deadlocks.

This PR grows `buf_send` / `buf_recv` per swap when `nsize` times the swap count exceeds them, in both functions.

**Related Issue(s)**

None filed. Reproducer: a `MLIAPUnified` model that calls `data.forward_exchange(copy_from, copy_to, vec_len)` with
`vec_len >= 128` on a 108-atom cell (`-k on t 1 -sf kk`, 1 or 4 MPI ranks) crashes without the patch and runs with it;
`vec_len` 4 and 32 run either way.

**Author(s)**

Hiori Kino (GitHub nim-hrkn), The Institute of Statistical Mathematics, (e-mail: as given on the PR)

**Licensing**

By submitting this pull request, I agree, that my contribution will be included in LAMMPS and redistributed under either the
GNU General Public License version 2 (GPL v2) or the GNU Lesser General Public License version 2.1 (LGPL v2.1).

**Artificial Intelligence (AI) Tools Usage**

By submitting this pull request, I confirm that AI tools were used: the bug was located and the fix (the two buffer-growth
checks in `comm_brick.cpp` and this description) was drafted with Claude Code (Anthropic Claude); I reviewed and tested the
change (host-path ML-IAP runs with MatterSim, NequIP and MACE models on 1 and 4 MPI ranks reproduce the GPU results after
the fix).

**Backward Compatibility**

No change for inputs. Pair styles that set `comm_forward` / `comm_reverse` before `Comm::init()` are unaffected (the
checks never trigger); styles that set them later now get correctly sized buffers instead of a heap overflow.

**Implementation Notes**

The checks mirror the ones `borders()` performs (`maxforward*smax > maxsend -> grow_send`, `maxforward*rmax > maxrecv ->
grow_recv`) but use the actual `nsize` of the call and the per-swap `sendnum` / `recvnum`. `grow_send(n, 0)` frees and
reallocates (contents are not needed before packing). `CommKokkos` inherits the host path from `CommBrick`, so KOKKOS
host runs are covered without further changes. Verified with LAMMPS `stable_30Sep2026` plus this patch (KOKKOS Serial +
ML-IAP + PYTHON, shared library): `MLIAPUnified` models with `forward_exchange`/`reverse_exchange` widths 4, 32, 128 and 256
on 1 and 4 ranks; MatterSim-v1-5M, NequIP-OAM-L and MACE-MPA-0 ML-IAP models give the same energies as the GPU
(`CommKokkos` device path) run within float32 round-off; the `examples/mliap` unified LJ example is unchanged.
`make check-whitespace` passes.

**Post Submission Checklist**

- [x] The feature or features in this pull request is complete
- [x] Licensing information is complete
- [x] Corresponding author information is complete
- [x] The source code follows the LAMMPS formatting guidelines
- [x] The feature has been verified to work with the CMake based build system

**Further Information, Files, and Links**

ML-IAP Kokkos coupling: `src/KOKKOS/mliap_unified_couple_kokkos.pyx` (`forward_exchange`, `reverse_exchange`),
`src/KOKKOS/pair_mliap_kokkos.cpp` (`forward_comm`, `reverse_comm` set `comm_forward = comm_reverse = vec_len` at call time).

---

How to open it: on https://github.com/nim-hrkn/lammps choose branch `fix-pair-comm-buffer-growth-develop`, "Contribute" ->
"Open pull request" (or the "Compare & pull request" banner); base repository `lammps/lammps`, base branch `develop`;
paste the title and body above; create. The `fix-pair-comm-buffer-growth` branch (same commit on `stable_30Sep2026`) stays in
the fork for the project's own builds.
