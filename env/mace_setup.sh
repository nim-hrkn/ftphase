#!/bin/bash
# env/mace: MACE needs e3nn 0.4.4 while sevenn 0.13 needs e3nn 0.6, so MACE gets its own env (torch cu128 wheels).
set -eo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
source /home/kino/miniforge3/etc/profile.d/conda.sh
mamba create -y -p "$ROOT/env/mace" -c conda-forge python=3.12 phonopy ase pymatgen spglib scipy pandas matplotlib-base pyyaml cmake ninja gxx=14 openmpi "cuda-nvcc>=12.8,<13" "cuda-cudart-dev>=12.8,<13" cuda-version=12.8 git
conda activate "$ROOT/env/mace"
pip install torch --index-url https://download.pytorch.org/whl/cu128
pip install mace-torch
# 2026-11-03: cuEquivariance 0.13 (NVIDIA CUDA kernels for the e3nn tensor products). mace_create_lammps_model --format mliap then
# exports a cueq model: ML-IAP 0.0198 s/step at 256 atoms vs 0.090 for the e3nn export (Slurm 23174), same energies.
pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu12
pip install cupy-cuda12x                                                        # ML-IAP Kokkos coupling
pip install --no-deps --no-build-isolation "$ROOT/env/lammps-gpu/src/python"   # pure-Python lammps package (MLIAPUnified base class)
pip install -e "$ROOT/ftphase" --no-deps
python -c "import torch, mace; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'mace', mace.__version__)"
