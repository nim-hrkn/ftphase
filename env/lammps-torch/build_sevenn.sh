#!/bin/bash
# LAMMPS stable_2Aug2023_update3 + SevenNet pair styles (e3gnn, e3gnn/parallel) with libtorch from env/torch (cu128).
# The torch-based pair style runs on the GPU by itself; no KOKKOS and no hybrid/scaled/kk needed, so calphy's hybrid/scaled
# (EXTRA-PAIR) and ufm / ti/spring (EXTRA-FIX) come from the plain packages.  Output: env/lammps-torch/bin/lmp_sevenn
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd); P=$ROOT/../..
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate "$P/env/torch"; set -u
cd "$ROOT"
if [ ! -d lammps_sevenn ]; then
  git clone https://github.com/lammps/lammps.git lammps_sevenn --branch stable_2Aug2023_update3 --depth=1
  sevenn patch_lammps ./lammps_sevenn --oeq
fi
export TORCH_CUDA_ARCH_LIST="8.6"
mkdir -p build_sevenn && cd build_sevenn
cmake ../lammps_sevenn/cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX="$ROOT" -D LAMMPS_MACHINE=sevenn \
  -D CMAKE_PREFIX_PATH="$(python -c 'import torch;print(torch.utils.cmake_prefix_path)');$CONDA_PREFIX" -D MKL_INCLUDE_DIR=/tmp \
  -D CUDA_TOOLKIT_ROOT_DIR="$CONDA_PREFIX" -D CUDAToolkit_ROOT="$CONDA_PREFIX" -D CMAKE_CUDA_COMPILER="$CONDA_PREFIX/bin/nvcc" \
  -D CUDA_TOOLKIT_INCLUDE="$CONDA_PREFIX/targets/x86_64-linux/include" -D CUDA_INCLUDE_DIRS="$CONDA_PREFIX/targets/x86_64-linux/include" -D CUDA_CUDART_LIBRARY="$CONDA_PREFIX/lib/libcudart.so" \
  -D BUILD_MPI=on -D BUILD_OMP=off -D CMAKE_CXX_STANDARD=17 \
  -D PKG_EXTRA-PAIR=on -D PKG_EXTRA-FIX=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-DUMP=on -D PKG_MANYBODY=on \
  -D PKG_MISC=on -D PKG_MOLECULE=on -D PKG_RIGID=on -D PKG_MC=on -D PKG_REPLICA=on 2>&1 | tee cmake.log
make -j 12 2>&1 | tee make.log
make install 2>&1 | tail -2
"$ROOT/bin/lmp_sevenn" -h | grep -E "LAMMPS \(|e3gnn|hybrid/scaled|ufm|ti/spring" | head -5
