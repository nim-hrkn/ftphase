#!/bin/bash
# wrapper: lmp_gpumliap with the embedded Python pointed at env/torch (nequip 0.19.1 + nequip-allegro 0.8.3 + openequivariance + cupy +
# lammps python package); TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD because ML-IAP unified models are pickled objects. Use as calphy lammps_executable.
# Models: potentials/nequip/*.nequip.lmp.pt (nequip-prepare-lmp-mliap nequip.net:mir-group/NequIP-OAM-L:0.1 X.nequip.lmp.pt --modifiers enable_OpenEquivariance).
export PYTHONHOME=/home/kino/kino/Claude/Projects/PhaseDiagram/env/torch
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
# the nequip ML-IAP wrapper torch.compiles at the first force call; keep the inductor caches on disk across calphy's ~20 LAMMPS launches per job
export TORCHINDUCTOR_FX_GRAPH_CACHE=1 TORCHINDUCTOR_AUTOGRAD_CACHE=1
export TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/torchinductor_nequip}
exec /home/kino/kino/Claude/Projects/PhaseDiagram/env/lammps-gpu-mliap/bin/lmp_gpumliap "$@"
