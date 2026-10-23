# env/lammps-gpu-grace — LAMMPS with GRACE on the GPU (built 2026-10-23)

`bin/lmp_gpugrace` = LAMMPS **stable_22Jul2025_update6** + the conda-forge feedstock `grace.patch`
(lammps-user-pace v.2025.12.4.p1, which contains the GRACE pair styles) + `src/KOKKOS/pair_hybrid_scaled_kokkos.{cpp,h}`
backported from stable_30Sep2026, KOKKOS/CUDA (sm_86), ML-PACE (`NO_GRACE_TF`: the TensorFlow styles `grace`,
`grace/*layer/*` are compiled out), EXTRA-PAIR (`ufm`), MC, RIGID etc.  Toolchain and runtime libraries come from
`env/ftphase` (cuda-nvcc 12.9, gxx 14, OpenMPI 5, **libcublas-dev 12.9 added on 2026-10-23** because the GRACE Kokkos
styles call cuBLAS).  Build: `./build.sh` (about 25 min on 12 cores; `build.log`).

Why a second build: `env/lammps-gpu` (30Sep2026) has `hybrid/scaled/kk` but its ML-PACE.cmake does not fetch the
GRACE sources, and the GRACE Kokkos files of the feedstock patch do not compile against the 30Sep2026 Kokkos type
names (`t_kkacc_1d_3`, no `tdual_virial_array`).  The 22Jul2025_update6 base takes the patch cleanly but lacks
`hybrid/scaled/kk`, which calphy needs for every run except the solid Frenkel-Ladd `fe` step; that one style was
backported with these renames: `AT::t_kkacc_1d_3 -> AT::t_f_array`, `AT::t_kkacc_1d -> AT::t_float_1d`,
`DAT::tdual_kkacc_1d{,_3} -> DAT::tdual_float_1d / tdual_f_array`, `KK_ACC_FLOAT -> F_FLOAT`,
`DAT::t_kkfloat_1d_3_lr_randomread -> DAT::t_x_array_randomread`, `DAT::tdual_double_1d -> DAT::tdual_xfloat_1d`
(forward-comm buffer), `HostKK -> Host`, `Pair::hybrid_index` line removed, `Force::pair_styles().contains()` ->
`force->pair_map->count()`.

Styles present: `grace/fs`, `grace/fs/kk`, `grace/1l/kk`, `grace/2l/kk`, `grace/3l/kk` (+ `/cpu/kk`, `/fp32`, `/mixed`
variants), `pace`, `pace/kk`, `pace/extrapolation/kk`, `hybrid/scaled`, `hybrid/scaled/kk`, `ufm`.

## Model files (`potentials/grace/`)

* `GRACE-FS-OAM.yaml` — exported on mygardenx1 from the foundation-model checkpoint:
  `grace_models checkpoint GRACE-FS-OAM`, then in `~/.cache/grace/checkpoints/GRACE-FS-OAM/`
  `grace_utils -p model.yaml -c checkpoint export -sf -n GRACE-FS-OAM.yaml` (tensorpotential; `grace_models download`
  only gives the TensorFlow saved model).  89 elements, 6 A cutoff, Academic Software License.
* `GRACE-1L-OMAT-medium-base-fp64-kokkos.npz` (82 MB, not in git) — `grace_models download --kokkos
  GRACE-1L-OMAT-medium-base-fp64`; the OAM/OMAT `FS`/`1L`/`2L` models have no kokkos export, the `*-medium-base`
  (uqv6) family has.  `grace/1l/kk` reads this npz; `grace/1l` (TensorFlow) is not built here.

## Tests (`test_grace.sh` -> `test/`, fcc Al0.7Li0.3, 50 NVE steps, GPU shared with a running calphy job)

| run | atoms | PE step 0 (eV) | PE step 50 (eV) | MD loop time (s) |
|---|---|---|---|---|
| grace/fs, CPU 1 rank | 256 | -859.20112 | -847.66925 | 1.59 |
| grace/fs/kk, GPU | 256 | -859.20112 | -847.66925 | 0.70 |
| grace/1l/kk, GPU | 256 | -850.2103 | -839.10633 | 1.37 |
| grace/fs, CPU 4 ranks | 2048 | -6717.6183 | -6626.4799 | 4.94 |
| grace/fs/kk, GPU 1 rank | 2048 | -6717.6183 | -6626.4799 | 2.57 |
| hybrid/scaled 0.7 grace/fs + 0.3 ufm, CPU 4 ranks | 2048 | -4692.4363 | -4591.2109 | 5.51 |
| hybrid/scaled/kk (grace/fs/kk + ufm), GPU | 2048 | -4692.4363 | -4591.2109 | 3.17 |
| grace/1l/kk (medium, fp64), GPU | 2048 | -6643.3671 | -6555.5434 | 8.25 |

GPU energies are identical to the CPU ones in every digit; the calphy mix (`hybrid/scaled/kk` with `ufm` on the
host) runs with `-k on g 1 -sf kk -pk kokkos newton on neigh half`.  Speed (RTX 3060 busy with another job):
GPU 1 rank = 1.9x CPU 4 ranks = 5.4x CPU 1 rank for grace/fs.  Use `env/ftphase/bin/mpirun` for the CPU runs: the
Intel MPI `mpirun` on PATH starts N singletons.
