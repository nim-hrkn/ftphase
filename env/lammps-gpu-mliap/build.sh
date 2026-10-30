#!/bin/bash
# Build LAMMPS stable_30Sep2026 (same source tree as env/lammps-gpu) with KOKKOS/CUDA (sm_86)
# + ML-PACE + ML-IAP/ML-SNAP + PYTHON (MLIAP_ENABLE_PYTHON) as a shared library + lmp_gpumliap.
# Why: ML-IAP "unified" lets libtorch MLIPs (MACE, SevenNet, MatterSim, NequIP) run inside LAMMPS
# on the GPU through the Kokkos coupling (forward_exchange for message passing), and calphy needs
# hybrid/scaled/kk, which the conda-forge 22Jul2025 build lacks. The embedded Python is env/torch
# (python 3.12 + torch + cupy + sevenn); env/mace (same 3.12) is used through PYTHONHOME at run time.
# Pitfalls met: with BUILD_SHARED_LIBS CMake links through a response file that nvcc_wrapper cannot expand
# ("cannot specify '-o' with '-c' ... with multiple files"), hence the RESPONSE_FILE flags; and with
# env/ftphase activated FindPython picked ftphase's libpython, hence the explicit Python_* paths.
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
SRC=$ROOT/../lammps-gpu/src
ENV=$ROOT/../ftphase
PY=$ROOT/../torch/bin/python
source /home/kino/miniforge3/etc/profile.d/conda.sh
conda activate "$ENV"
set -u
export NVCC_WRAPPER_DEFAULT_COMPILER=x86_64-conda-linux-gnu-g++
export OMPI_CXX="$SRC/lib/kokkos/bin/nvcc_wrapper"
# LAMMPS source patch (env/patches/README.md, 2026-10-30): CommBrick pair comm buffer growth. Needed for the host path of the
# Kokkos ML-IAP forward_exchange (CPU build env/lammps-cpu-mliap); harmless for the device path used here. The installed
# lmp_gpumliap of 2026-10-30 predates the patch (same source tree otherwise).
patch -p1 -N -r - -d "$SRC" < "$ROOT/../patches/lammps-30Sep2026-comm_brick-pair-comm-buffers.patch" || true
mkdir -p "$ROOT/build" && cd "$ROOT/build"
cmake "$SRC/cmake" \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_INSTALL_PREFIX="$ROOT" \
  -D CMAKE_CXX_COMPILER="$SRC/lib/kokkos/bin/nvcc_wrapper" \
  -D CMAKE_CXX_STANDARD=17 \
  -D BUILD_MPI=on -D BUILD_OMP=off -D BUILD_SHARED_LIBS=on \
  -D LAMMPS_MACHINE=gpumliap \
  -D PKG_KOKKOS=on -D Kokkos_ENABLE_CUDA=on -D Kokkos_ENABLE_SERIAL=on -D Kokkos_ENABLE_OPENMP=off \
  -D Kokkos_ARCH_AMPERE86=on -D Kokkos_ARCH_NATIVE=off \
  -D PKG_ML-PACE=on -D PKG_ML-SNAP=on -D PKG_ML-IAP=on -D MLIAP_ENABLE_PYTHON=on \
  -D PKG_PYTHON=on -D Python_EXECUTABLE="$PY" -D PYTHON_EXECUTABLE="$PY" \
  -D Python_ROOT_DIR="$ROOT/../torch" -D Python_LIBRARY="$ROOT/../torch/lib/libpython3.12.so" -D Python_INCLUDE_DIR="$ROOT/../torch/include/python3.12" \
  -D CMAKE_CXX_USE_RESPONSE_FILE_FOR_OBJECTS=OFF -D CMAKE_CXX_USE_RESPONSE_FILE_FOR_LIBRARIES=OFF \
  -D CMAKE_INSTALL_RPATH="\$ORIGIN/../lib" -D CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
  -D PKG_MANYBODY=on \
  -D PKG_EXTRA-PAIR=on -D PKG_EXTRA-FIX=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-DUMP=on \
  -D PKG_MISC=on -D PKG_MOLECULE=on -D PKG_RIGID=on -D PKG_MC=on -D PKG_REPLICA=on \
  2>&1 | tee cmake.log
make -j 8 2>&1 | tee make.log
make install 2>&1 | tail -3
"$ROOT/bin/lmp_gpumliap" -h | grep -E "LAMMPS \(|KOKKOS|Installed" | head -4
