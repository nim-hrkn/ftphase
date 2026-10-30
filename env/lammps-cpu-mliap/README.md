# env/lammps-cpu-mliap — CPU twin of lmp_gpumliap (KOKKOS Serial + ML-IAP Python), 2026-10-30

`bin/lmp_cpumliap` = LAMMPS stable_30Sep2026 (source `env/lammps-gpu/src`, **with the CommBrick patch below**) with KOKKOS (Serial backend,
no CUDA, no OpenMP) + ML-PACE + ML-IAP(`MLIAP_ENABLE_PYTHON`) + PYTHON, shared library, conda toolchain of env/ftphase (gxx 14, OpenMPI 5),
embedded Python = env/torch (`build.sh`). `bin/lmp_cpumliapsys` (`build_sys.sh`) is the same with the system g++ 13 / OpenMPI 4.1 (run it with
`/usr/bin/mpirun`); it was built to rule out the conda C++ runtime and behaves identically.

Why a Kokkos build for the CPU: the ML-IAP wrappers of MatterSim / NequIP / MACE call `data.forward_exchange` / `reverse_exchange`
(ghost-atom feature exchange between MPI ranks for message passing), which only the Kokkos coupling provides (`mliap_unified_couple_kokkos`;
on the host it hands numpy views and torch CPU tensors work directly). The plain coupling of a non-Kokkos run fails with
`'MLIAPDataPy' object has no attribute 'forward_exchange'` (Slurm 23008). Run with `-k on t 1 -sf kk -pk kokkos newton on neigh half`
and `mpirun -np N` (one thread per rank; `OMP_NUM_THREADS=1`).

## The bug that made every MLIP model crash on the CPU (fixed by `env/patches/lammps-30Sep2026-comm_brick-pair-comm-buffers.patch`)

Symptoms (both builds, 1 and 4 ranks): MatterSim `RuntimeError: unknown parameter type` then `malloc(): unaligned tcache chunk detected`;
MACE segfault inside an e3nn fully connected layer; NequIP a c10 error in `mul` followed by a crash in the unwinder, or a futex deadlock with the
system libgcc_s preloaded. Not the cause (all tested): OpenMP runtimes (a Kokkos OpenMP build hung for a second reason, two libgomp copies),
conda vs system libstdc++/libgcc_s, two libpython copies, PYTORCH_JIT, torch itself (matmul, Linear, autograd, index_add, e3nn FC / tensor
products and TorchScript all run inside LAMMPS: `test/dbg_*.py`), the numpy views of the coupling (`test/dbg_ints.py`: dtypes and index
ranges correct; the test cell `conf.data` is pure Al, so `elems` all 0 is right).

Root cause (`test/dbg_exchange.py`, vec_len 4 and 32 fine, 128 and 256 crash): `CommBrick::forward_comm(Pair *)` / `reverse_comm(Pair *)`
pack `nsize*sendnum` doubles into `buf_send` without a size check; the buffers are sized in `borders()` from `maxforward`, which
`Comm::init()` takes from `pair->comm_forward` **at init**, but `pair mliap/kk` sets `comm_forward = vec_len` only inside `forward_exchange`
(feature width known at run time: 64-256 for these models). The device path (`CommKokkos::forward_comm_device`) resizes its Kokkos buffers
per call, so the GPU runs were always correct. The patch grows `buf_send`/`buf_recv` per swap when `nsize*count` exceeds them (both
functions). Candidate for an upstream LAMMPS PR (develop branch; the device path and `comm_forward` semantics are unchanged).

## Results on the patched binary (108-atom test cell, `run 0`, `in.run0`; GPU values from Slurm 22999 / 23000 / 22988)

| model (CPU export) | 1 rank | 4 ranks | GPU (lmp_gpumliap) |
|---|---|---|---|
| MatterSim-v1 5M (`_mliap_nocompile.pt`) | −403.17566 eV, −3403.46 bar | −403.1757 eV, −3403.46 bar | −403.17578 eV, −3403.39 bar |
| MACE-MPA-0 fp32 (`-mliap_lammps-f32-cpu.pt`: the pickled `config.allow_cpu` set to True; the `MACE_ALLOW_CPU` env var is read only at export) | −403.92015, 607.40 | −403.92016, 607.37 | −403.92018, 607.46 |
| NequIP-OAM-L (`-plain-nocompile.nequip.lmp.pt`; OEQ is CUDA-only, torch.compile fails on the CPU under g++ 13) | −404.08091, 2017.67 | −404.08096, 2017.67 | −404.08095, 2017.74 |

Differences are float32 round-off (0.1-1 µeV/atom). The 4-rank runs decompose the 108-atom cell into 4 domains with ghost exchange
(`forward_exchange`/`reverse_exchange` through the host comm), i.e. multi-rank ML-IAP is verified here for all three models.
LJ control models (`test/mliap_torch_lj*.py`, forces analytic or by autograd) reproduce the numpy example to all digits on 1 and 4 ranks;
LAMMPS ML-IAP force convention: `update_pair_forces(fij)` with `fij = +1/2 dE/drij`.
Speed on the CPU (Slurm 23010, 4 cores of mygarden5, `test/cpu_mpi_kk.23010.out`; 100 NVE steps, s/step; `hybrid/scaled/kk` 0.7 model + 0.3 ufm
costs the same as the plain model):

| | 1 rank, 108 atoms | 4 ranks, 108 atoms | 4 ranks, 256 atoms | GPU (lmp_gpumliap, 256 atoms) |
|---|---|---|---|---|
| MatterSim-v1 5M (eager) | 0.458 | 0.218 | 0.726 | 0.040 (compiled) |
| NequIP-OAM-L (plain, eager) | 2.40 | 1.07 | 2.98 | 0.029 (OpenEquivariance) |

4 ranks give 2.1-2.2x over 1 rank; the RTX 3060 is 18x (MatterSim) to 100x (NequIP, thanks to OEQ) faster than 4 CPU cores. A calphy
liquid (about 200,000 steps) with MatterSim on 4 CPU cores would take about 40 h, so the CPU route is for hosts without a GPU (mygardenx1
with 64 cores: untested scaling) and for correctness checks, not for production on this host.

## Other CPU pitfalls met
- nequip 0.19.1's ML-IAP wrapper picks `device = "cuda"` whenever the data object comes from the Kokkos coupling: patched to require
  `torch.cuda.is_available()` (`env/patches/nequip-0.19.1-lmp_mliap_wrapper-cpu-kokkos.patch`).
- `mpirun` does not forward the environment to the ranks; the wrappers set `PYTHONHOME` etc. themselves, otherwise use `-x VAR`.
- A Kokkos OpenMP build (`BUILD_OMP=on`) hangs in the MatterSim forward pass: two OpenMP runtimes in one process (conda libgomp of the LAMMPS
  build and the libgomp bundled in the torch wheel). Keep Kokkos Serial + MPI ranks.
- `pkill -f <pattern>` from a shell whose command line contains the pattern kills the shell.

Files: `build.sh`, `build_sys.sh`, `bin/lmp_mliap_mattersim_cpu.sh`, `bin/lmp_mliap_nequip_cpu.sh`, `test/cpu_mpi_kk.sbatch`, the `test/dbg_*.py`
diagnostics and `test/mliap_torch_lj*.py` controls, `test/in.torch_lj*.Ar`; `env/lammps-gpu-mliap/test/cpu_mpi.sbatch` (non-Kokkos CPU test).
Deployment to mygardenx1/x2: copy `bin/` + `lib/` (generic x86-64, conda OpenMPI 5 of env/ftphase) and add mattersim / nequip / cupy-cuda12x /
the lammps python package to their env/torch (`env/torch_setup.sh`), then apply `env/patches`.
