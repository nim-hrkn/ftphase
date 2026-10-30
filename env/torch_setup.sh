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
# 2026-10-30: MatterSim (ML-IAP wrapper mattersim.lammps.mliap_wrapper) and the ML-IAP runtime deps. The PyPI torchvision pulled in by
# mattersim does not match torch 2.11.0 ("operator torchvision::nms does not exist"): take torchvision/torchaudio from the cu128 index.
pip install mattersim cupy-cuda12x
pip install --force-reinstall --no-deps --index-url https://download.pytorch.org/whl/cu128 torchvision torchaudio
pip install --no-deps --no-build-isolation "$ROOT/env/lammps-gpu/src/python"   # pure-Python lammps package (MLIAPUnified base class)
# 2026-10-30: NequIP / Allegro (ML-IAP export: nequip-prepare-lmp-mliap nequip.net:mir-group/NequIP-OAM-L:0.1 X.nequip.lmp.pt --modifiers enable_OpenEquivariance)
pip install nequip nequip-allegro        # 0.19.1 / 0.8.3; adds lightning, keeps torch/e3nn/sevenn/mattersim unchanged
# local patches to the installed MLIP packages (env/patches/README.md lists them and why)
SP=$(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
for p in "$ROOT"/env/patches/*.patch; do patch -p1 -N -d "$SP" < "$p"; done
pip install -e "$ROOT/ftphase" --no-deps
python -c "import torch, sevenn, mace; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'sevenn', sevenn.__version__, 'mace', mace.__version__)"
