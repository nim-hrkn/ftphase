# env/patches — local patches to third-party MLIP packages (apply after `pip install`, see `env/torch_setup.sh`)

Policy (user decision 2026-10-30): every change we need in an installed MLIP package to make it run in LAMMPS is kept here as a
unified diff against the released version, with the reason, so the environment can be rebuilt on another host and the fix can be
reported upstream. Apply with `patch -p1 -d <site-packages> < env/patches/<file>.patch`.

| patch | package | why |
|---|---|---|
| `nequip-0.19.1-lmp_mliap_wrapper-cpu-kokkos.patch` | nequip 0.19.1, `nequip/integrations/lammps_mliap/lmp_mliap_wrapper.py` | the ML-IAP wrapper chooses `device = "cuda"` whenever the LAMMPS data object comes from the Kokkos coupling. With a Kokkos build on the OpenMP/Serial backend (`env/lammps-cpu-mliap/bin/lmp_cpumliap`, needed on CPU hosts because only the Kokkos coupling provides `forward_exchange`) this raises "No CUDA GPUs are available". The patch adds `and torch.cuda.is_available()`. |

| `lammps-30Sep2026-comm_brick-pair-comm-buffers.patch` | LAMMPS stable_30Sep2026, `src/comm_brick.cpp` (applied in `env/lammps-gpu/src`, used by the `env/lammps-cpu-mliap` build) | `CommBrick::forward_comm(Pair*)` / `reverse_comm(Pair*)` pack `nsize*sendnum` doubles into `buf_send` without checking its size; the buffers are sized in `borders()` from `maxforward`, which `Comm::init()` records from `pair->comm_forward` **at init**. `pair mliap/kk` sets `comm_forward = vec_len` only when the model calls `forward_exchange` (feature width known at run time), so on the host path (CPU Kokkos build, or any Kokkos build with `comm host`) a width above ~32 overflows the heap: MatterSim/NequIP/MACE crashed with `malloc(): unaligned tcache chunk`, segfaults in e3nn or autograd, or futex deadlocks (reproduced with a 108-atom cell: vec_len 4/32 fine, 128/256 crash; 2026-10-30). The device path (`forward_comm_device`) resizes Kokkos buffers per call and was never affected, which is why the GPU runs were correct. The patch grows `buf_send`/`buf_recv` per swap when `nsize*count` exceeds them. Candidate for an upstream PR. |

Not patched (worked as released): mace-torch 0.3.16 ML-IAP wrapper (export bypass script `env/lammps-gpu-mliap/test/mace_to_mliap.py`
instead of `mace_create_lammps_model --format mliap`), sevenn 0.13 (`-oeq` export only), mattersim 1.2.5 on the GPU.
