#!/bin/bash
# env/torch: conda env for libtorch-type MLIPs (SevenNet, MACE) as ASE calculators for the QHA stage, plus the libtorch
# used to build LAMMPS with pair_style e3gnn / mace (env/lammps-torch).  python 3.12, torch cu128 wheels.
set -eo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
source /home/kino/miniforge3/etc/profile.d/conda.sh
mamba create -y -p "$ROOT/env/torch" -c conda-forge python=3.12 phonopy ase pymatgen spglib scipy pandas matplotlib-base pyyaml cmake ninja gxx=14 openmpi "cuda-nvcc>=12.8,<13" "cuda-cudart-dev>=12.8,<13" cuda-version=12.8
conda activate "$ROOT/env/torch"
pip install torch --index-url https://download.pytorch.org/whl/cu128
pip install sevenn mace-torch
pip install -e "$ROOT/ftphase" --no-deps
python -c "import torch, sevenn, mace; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'sevenn', sevenn.__version__, 'mace', mace.__version__)"
