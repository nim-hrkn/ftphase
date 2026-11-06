#!/bin/bash
# wrapper: conda-forge LAMMPS 29Aug2024 of env/deepmd with the deepmd-kit 3.1.3 plugin auto-loaded (LAMMPS_PLUGIN_PATH);
# pair_style deepmd <model.pth> runs the PyTorch model on the GPU by itself (no Kokkos); LAMMPS integrates on the CPU.
R=/home/kino/kino/Claude/Projects/PhaseDiagram/env/deepmd
export LAMMPS_PLUGIN_PATH=$R/lib/deepmd_lmp
export LD_LIBRARY_PATH=$R/lib:$R/lib/python3.12/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
exec $R/bin/lmp_mpi "$@"
