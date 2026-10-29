# GPU timing of the MLIPs under identical conditions (2026-10-29)

`prepare.py` reran one QHA job and one liquid calphy job of the comparison WorkChains for each MLIP, alone on an idle
node with 1 GPU (RTX 3060, driver 595.99.02) and 4 CPUs, once on mygarden5 and once on mygarden6.
QHA = cell s03_fcc (fcc Al28Li4, phonopy 2x2x2 = 256 atoms, 9 volumes, mesh 60 A, cell relaxation first);
liquid = lqd_x0.30 (256 atoms, calphy ts 1100 -> 700 K, 10k + 10k/10k steps, 3 iterations, 1 MPI rank).
Raw numbers: `times_all.tsv` (seconds).

| MLIP | QHA m5 / m6 | liquid m5 / m6 | liquid mean | liquid / ACE |
|---|---|---|---|---|
| ACE (pace/kk) | 36 s / 62 s | 8.5 / 10.5 min | 9.5 min | 1 |
| GRACE-FS-OAM (grace/fs/kk) | 18.1 / 18.2 min | 25.1 / 26.1 min | 25.6 min | 2.7 |
| SevenNet-0 (e3gnn + oeq) | 2.0 / 2.0 min | 37.6 / 31.7 min | 34.7 min | 3.7 |
| SevenNet-MF-ompa (e3gnn + oeq) | 18.8 / 18.9 min | 197 / 212 min | 204 min | 21 |
| GRACE-1L-OMAT (grace/1l/kk/fp32) | 2.5 / 2.4 min | (comparison run: 28 min) | 28 min | 2.9 |
| GRACE-2L-OMAT (grace/2l/kk/fp32) | (comparison run: 0.9 min) | (comparison run: 98 min) | 98 min | 10 |
| MACE-MPA-0 (mace, float32) | 3.0 / 3.0 min | (comparison run: 573 min) | 573 min | 60 |

Notes: QHA for ACE and GRACE-FS runs through the conda LAMMPS Kokkos build, whose CUDA kernels are compiled for
compute capability 5.0 (JIT on the 8.6 card); GRACE-FS QHA on the CPU took 0.3 min in the comparison runs, so for
these two the CPU is the better QHA device. The liquid jobs of the comparison WorkChains also had an exclusive GPU (Slurm --gres=gpu:1); for the four MLIPs
measured here they agree with the remeasurement within 10 % (ACE 8 vs 9.5 min, GRACE-FS 26 vs 25.6, SevenNet-0 32 vs
34.7, SevenNet-MF-ompa 195 vs 204), so for GRACE-1L, GRACE-2L and MACE-MPA-0 the comparison-run liquid times are used.
Their QHA ran on the GPU here except GRACE-2L (comparison run, also on the GPU).
