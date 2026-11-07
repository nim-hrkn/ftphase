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

## Added 2026-11-07: PET (metatomic/kk) and DPA-3 (deepmd plugin), liquid only (`prepare_liq.py`, mygarden5, same lqd_x0.30 job)

| MLIP | route | liquid wall | LAMMPS loop s/step (256 atoms, 20k MD steps of segments 0-1) | liquid / ACE |
|---|---|---|---|---|
| PET-OMat-S (25.9M, OMat24 only) | `env/metatomic/bin/lmp_metatomic.sh`, `metatomic/kk` | 152 min (Slurm 23203) | 0.040 | 16 |
| PET-OAM-L (255M, OMat24 -> sAlex+MPtrj) | same | 585 min (Slurm 23204) | 0.161 | 62 |
| DPA-3.1-3M, MPtrj branch (3.27M) | `env/deepmd/bin/lmp_deepmd.sh`, `pair_style deepmd` (torch on the GPU, LAMMPS on the CPU) | 548 min (Slurm 23206) | 0.149 | 58 |

| DPA4-Plus-OMat24 v20260805 (8.8M, OMat24 only) | `env/deepmd32/bin/lmp_deepmd.sh`, `pair_style deepmd X.pt2` (AOTInductor on the GPU, LAMMPS on the CPU) | 477 min (Slurm 23222) | 0.135 | 50 |
| DPA4-Air-OMat24 v20260805 (5.1M, OMat24 only) | same | 219 min (Slurm 23223) | 0.062 | 23 |

Notes: the PET-OAM-L time equals the `pair_style mace` MACE-MPA-0 run (573 min) and is 7.7x the ML-IAP+cuEquivariance MACE
production (76 min); PET-OMat-S sits between SevenNet-0 (35 min) and SevenNet-MF-ompa (204 min). The wall time includes
calphy's melting check, NPT equilibration and the 3 x (forward + backward) 10k-step switches; the s/step is from LAMMPS'
"Loop time" lines of the first two segments. The Matbench DPA-3.1-3M-FT checkpoint cannot run in LAMMPS (frozen without
`border_op` by a private deepmd-kit version; see `env/deepmd/README.md`), so the public pretrained DPA-3.1-3M's MPtrj branch
was frozen with deepmd-kit 3.1.3 instead. calphy's binary preflight does not see plugin styles: `CALPHY_SKIP_PREFLIGHT=1`.
