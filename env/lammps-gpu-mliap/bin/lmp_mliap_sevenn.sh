#!/bin/bash
# wrapper: lmp_gpumliap with the embedded Python pointed at env/torch (sevenn + torch + cupy + lammps python package);
# TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD because ML-IAP unified models are pickled objects. Use as calphy lammps_executable.
export PYTHONHOME=/home/kino/kino/Claude/Projects/PhaseDiagram/env/torch
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
export MACE_ALLOW_CPU=false
exec /home/kino/kino/Claude/Projects/PhaseDiagram/env/lammps-gpu-mliap/bin/lmp_gpumliap "$@"
