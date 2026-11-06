# env/metatomic — LAMMPS (metatensor fork, 4 Jul 2026) with `pair_style metatomic` + KOKKOS/CUDA sm_86, for the PET models

Created 2026-11-06 (not committed; recreate with):

    mamba create -p ./env/metatomic -c metatensor -c conda-forge python=3.12 \
      "lammps-metatomic=2026.07.04.mta2=cuda129_kokkos_arch_AMPERE86*mpi_openmpi*" "pytorch=*=cuda*" "cuda-version>=12.9,<13" pip
    ./env/metatomic/bin/pip install metatrain upet      # mtt export + the upet checkpoints (torch 2.13 cu129, metatomic-torch 0.1.19)

`bin/lmp` has `metatomic`, `metatomic/kk`, `hybrid/scaled`, `hybrid/scaled/kk`, `ufm` (calphy's full vocabulary on the GPU, like
`lmp_gpugrace`). Models: `potentials/pet/*.ckpt` from https://huggingface.co/lab-cosmo/upet/tree/main/models, exported with
`mtt export X.ckpt -o X.pt` in this env (the exported .pt is what LAMMPS and the ASE calculator load). LAMMPS input:
`pair_style metatomic model.pt` (+ `device cuda` without Kokkos), `pair_coeff * * 13 3` (atomic numbers per LAMMPS type).
Checks: `test/pet_check.sbatch` (ASE reference vs LAMMPS kk single point, hybrid/scaled+ufm mix, 50-step NVT); liquid timing
benchmark: `ftphase/examples/mlip_bench/prepare_liq.py`.

Verified 2026-11-06 (Slurm 23197, `test/pet_check.sbatch`, 256-atom Al-Li liquid cell, GPU): LAMMPS `metatomic/kk` single-point
energy and pressure equal the ASE `MetatomicCalculator` values to all printed digits (PET-OMat-S -833.48358 eV / -5236.33 bar,
PET-OAM-L -833.17920 eV / -4966.93 bar); `hybrid/scaled` with `ufm` runs (lambda 1 and 0.5). 50-step NVT at 256 atoms:
PET-OMat-S 0.063 s/step, PET-OAM-L 0.169 s/step (MACE-MPA-0 cueq ML-IAP 0.020, SevenNet-MF-ompa 0.064, pair_style mace 0.177).
Pitfalls: (1) `pair_style metatomic` (plain and /kk) segfaults when issued before `read_data`; calphy's executable runner writes
pair_style before read_data in the first segment, so calphy must call `bin/lmp_metatomic.sh`, which moves such a pair_style line
after the first read_data/read_restart in every `-in` script (later segments start with read_restart and are untouched).
(2) The non-Kokkos path (`device cuda`, LAMMPS on the CPU) stopped with "Neighbor list overflow, boost neigh_modify one" for
PET-OMat-S at the default `neigh_modify one 2000`; the Kokkos path needs no change. (3) The exported model prints a
`_mts_buffer_names` deprecation warning from metatensor-learn; harmless.
