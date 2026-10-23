#!/bin/bash
# Build LAMMPS stable_22Jul2025_update6 + conda-forge grace.patch (lammps-user-pace 2025.12.4.p1 = GRACE) + pair_hybrid_scaled_kokkos backported from 30Sep2026 with KOKKOS/CUDA (sm_86) + ML-PACE for calphy GPU runs.
# Why: GRACE (grace/fs, grace/1l,2l,3l + their /kk variants) ships inside lammps-user-pace, which the 30Sep2026
# ML-PACE.cmake does not fetch; the conda-forge feedstock patch adds it only on the 22Jul2025_update6 base, and that base
# lacks hybrid/scaled/kk (needed by calphy), so that one style is backported (type renames: t_kkacc_1d_3 -> t_f_array etc.).
# which calphy needs (reversible scaling, liquid UFM switching) as soon as -k on is given.
# Toolchain comes from env/ftphase (cuda-nvcc 12.9, gxx 14.4, openmpi 5.0, cmake).
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
ENV=$ROOT/../ftphase
source /home/kino/miniforge3/etc/profile.d/conda.sh
conda activate "$ENV"
set -u
export NVCC_WRAPPER_DEFAULT_COMPILER=x86_64-conda-linux-gnu-g++
export OMPI_CXX="$ROOT/src/lib/kokkos/bin/nvcc_wrapper"
mkdir -p "$ROOT/build" && cd "$ROOT/build"
cmake "$ROOT/src/cmake" \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_INSTALL_PREFIX="$ROOT" \
  -D CMAKE_CXX_COMPILER="$ROOT/src/lib/kokkos/bin/nvcc_wrapper" \
  -D CMAKE_CXX_STANDARD=17 \
  -D BUILD_MPI=on -D BUILD_OMP=off \
  -D LAMMPS_MACHINE=gpugrace \
  -D PKG_KOKKOS=on -D Kokkos_ENABLE_CUDA=on -D Kokkos_ENABLE_SERIAL=on -D Kokkos_ENABLE_OPENMP=off \
  -D Kokkos_ARCH_AMPERE86=on -D Kokkos_ARCH_NATIVE=off \
  -D PKG_ML-PACE=on -D NO_GRACE_TF=yes -D PKG_ML-SNAP=on -D PKG_MANYBODY=on \
  -D PKG_EXTRA-PAIR=on -D PKG_EXTRA-FIX=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-DUMP=on \
  -D PKG_MISC=on -D PKG_MOLECULE=on -D PKG_RIGID=on -D PKG_MC=on -D PKG_REPLICA=on \
  2>&1 | tee cmake.log
make -j 12 2>&1 | tee make.log
make install 2>&1 | tail -3
"$ROOT/bin/lmp_gpugrace" -h | grep -E "LAMMPS \(|KOKKOS" | head -3
