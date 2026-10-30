#!/bin/bash
# wrapper: lmp_cpumliap (KOKKOS OpenMP, no CUDA) with the embedded Python pointed at env/torch (nequip 0.19.1 + torch + lammps python package).
# Use the plain export (potentials/nequip/*-plain.nequip.lmp.pt): OpenEquivariance is CUDA-only.
# Run with `-k on t 1 -sf kk -pk kokkos newton on neigh half` so the Kokkos coupling (ghost exchange) is used on the CPU.
export PYTHONHOME=/home/kino/kino/Claude/Projects/PhaseDiagram/env/torch
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
export CUDA_VISIBLE_DEVICES=
export TORCHINDUCTOR_FX_GRAPH_CACHE=1 TORCHINDUCTOR_AUTOGRAD_CACHE=1
export TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/torchinductor_nequip_cpu}
exec /home/kino/kino/Claude/Projects/PhaseDiagram/env/lammps-cpu-mliap/bin/lmp_cpumliap "$@"
