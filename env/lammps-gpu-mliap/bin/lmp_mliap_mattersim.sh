#!/bin/bash
# wrapper: lmp_gpumliap with the embedded Python pointed at env/torch (mattersim 1.2.5 + torch + cupy + lammps python package);
# TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD because ML-IAP unified models are pickled objects. Use as calphy lammps_executable.
# Models: potentials/mattersim/mattersim-v1.0.0-{5M,1M}_mliap.pt (test/mattersim_to_mliap.py).
export PYTHONHOME=/home/kino/kino/Claude/Projects/PhaseDiagram/env/torch
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
# MatterSimMLIAP torch.compiles the model at the first force call (~20 s on the RTX 3060); calphy launches LAMMPS ~20 times per job,
# so keep the inductor caches on disk (per user, shared by all jobs).
export TORCHINDUCTOR_FX_GRAPH_CACHE=1 TORCHINDUCTOR_AUTOGRAD_CACHE=1
export TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/torchinductor_mattersim}
exec /home/kino/kino/Claude/Projects/PhaseDiagram/env/lammps-gpu-mliap/bin/lmp_gpumliap "$@"
