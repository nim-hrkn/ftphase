#!/bin/bash
# Build LAMMPS stable_30Sep2026 (same source tree as env/lammps-gpu) with KOKKOS/OpenMP (no CUDA) + ML-PACE + ML-IAP/ML-SNAP
# + PYTHON (MLIAP_ENABLE_PYTHON) as a shared library + lmp_cpumliap: the CPU twin of env/lammps-gpu-mliap.
# Why: the ML-IAP wrappers of MatterSim and NequIP call data.forward_exchange / reverse_exchange (ghost-atom feature exchange
# for message passing), which only the Kokkos coupling (mliap_unified_couple_kokkos, host arrays as numpy when the device is
# the CPU) provides; the plain coupling of a non-Kokkos run has no such method, so multi-rank CPU runs need `-k on t 1 -sf kk`
# on a Kokkos build.  Generic x86-64 (no Kokkos_ARCH_NATIVE) so the binary can be copied to mygardenx1 / mygardenx2.
# Embedded Python = env/torch (python 3.12 + torch + mattersim + nequip); PYTHONHOME selects the env at run time.
# Kokkos SERIAL only, BUILD_OMP off (2026-10-30): the first build with Kokkos OpenMP + BUILD_OMP hung inside the MatterSim forward
# pass on the CPU (two OpenMP runtimes in one process: libgomp of the conda gcc 14 used for LAMMPS and the libgomp bundled in the
# torch wheel). Parallelism on the CPU is MPI ranks only (-k on t 1 -sf kk), one thread per rank.
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
SRC=$ROOT/../lammps-gpu/src
ENV=$ROOT/../ftphase
PY=$ROOT/../torch/bin/python
source /home/kino/miniforge3/etc/profile.d/conda.sh
conda activate "$ENV"
set -u
# LAMMPS source patch (env/patches/README.md): CommBrick pair forward/reverse comm must grow its buffers to the width the pair
# style asks for at call time; without it the host path of the Kokkos ML-IAP forward_exchange overflows the heap for feature
# widths above ~32 (MatterSim / NequIP / MACE crashed on the CPU). Idempotent: -N skips an already applied patch.
patch -p1 -N -r - -d "$SRC" < "$ROOT/../patches/lammps-30Sep2026-comm_brick-pair-comm-buffers.patch" || true
mkdir -p "$ROOT/build" && cd "$ROOT/build"
cmake "$SRC/cmake" \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_INSTALL_PREFIX="$ROOT" \
  -D CMAKE_CXX_COMPILER=x86_64-conda-linux-gnu-g++ \
  -D CMAKE_CXX_STANDARD=17 \
  -D BUILD_MPI=on -D BUILD_OMP=off -D BUILD_SHARED_LIBS=on \
  -D LAMMPS_MACHINE=cpumliap \
  -D PKG_KOKKOS=on -D Kokkos_ENABLE_CUDA=off -D Kokkos_ENABLE_SERIAL=on -D Kokkos_ENABLE_OPENMP=off \
  -D Kokkos_ARCH_NATIVE=off \
  -D PKG_ML-PACE=on -D PKG_ML-SNAP=on -D PKG_ML-IAP=on -D MLIAP_ENABLE_PYTHON=on \
  -D PKG_PYTHON=on -D Python_EXECUTABLE="$PY" -D PYTHON_EXECUTABLE="$PY" \
  -D Python_ROOT_DIR="$ROOT/../torch" -D Python_LIBRARY="$ROOT/../torch/lib/libpython3.12.so" -D Python_INCLUDE_DIR="$ROOT/../torch/include/python3.12" \
  -D CMAKE_INSTALL_RPATH="\$ORIGIN/../lib" -D CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
  -D PKG_MANYBODY=on \
  -D PKG_EXTRA-PAIR=on -D PKG_EXTRA-FIX=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-DUMP=on \
  -D PKG_MISC=on -D PKG_MOLECULE=on -D PKG_RIGID=on -D PKG_MC=on -D PKG_REPLICA=on \
  2>&1 | tee cmake.log
make -j 8 2>&1 | tee make.log
make install 2>&1 | tail -3
"$ROOT/bin/lmp_cpumliap" -h | grep -E "LAMMPS \(|KOKKOS|Installed" | head -4
