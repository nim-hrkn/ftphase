#!/bin/bash
# Variant of build.sh with the *system* toolchain (Ubuntu 24.04 g++ 13.3, OpenMPI 4.1.6 from apt, cmake 3.28) instead of the conda
# toolchain of env/ftphase: lmp_cpumliapsys. Why: the conda build loads conda's libstdc++ 6.0.36 / libgcc_s (via RPATH) while the torch
# wheel in env/torch is tested against the system runtimes (plain env/torch python loads the system libstdc++ 6.0.33); the MLIP models
# crash on the CPU inside the conda build but run in plain python. Embedded Python = env/torch (its own libpython, one copy in the process).
# Run with /usr/bin/mpirun (system OpenMPI), e.g.  /usr/bin/mpirun -np 4 bin/lmp_cpumliapsys -k on t 1 -sf kk -pk kokkos newton on neigh half -in in.lmp
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
SRC=$ROOT/../lammps-gpu/src
PY=$ROOT/../torch/bin/python
unset PYTHONPATH PYTHONHOME CONDA_PREFIX
export PATH=/usr/bin:/bin
mkdir -p "$ROOT/build_sys" && cd "$ROOT/build_sys"
/usr/bin/cmake "$SRC/cmake" \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_INSTALL_PREFIX="$ROOT" \
  -D CMAKE_C_COMPILER=/usr/bin/gcc -D CMAKE_CXX_COMPILER=/usr/bin/g++ \
  -D MPI_CXX_COMPILER=/usr/bin/mpicxx -D MPI_C_COMPILER=/usr/bin/mpicc \
  -D CMAKE_CXX_STANDARD=17 \
  -D BUILD_MPI=on -D BUILD_OMP=off -D BUILD_SHARED_LIBS=on \
  -D LAMMPS_MACHINE=cpumliapsys \
  -D PKG_KOKKOS=on -D Kokkos_ENABLE_CUDA=off -D Kokkos_ENABLE_SERIAL=on -D Kokkos_ENABLE_OPENMP=off \
  -D Kokkos_ARCH_NATIVE=off \
  -D PKG_ML-PACE=on -D PKG_ML-SNAP=on -D PKG_ML-IAP=on -D MLIAP_ENABLE_PYTHON=on \
  -D PKG_PYTHON=on -D Python_EXECUTABLE="$PY" -D PYTHON_EXECUTABLE="$PY" \
  -D Python_ROOT_DIR="$ROOT/../torch" -D Python_LIBRARY="$ROOT/../torch/lib/libpython3.12.so" -D Python_INCLUDE_DIR="$ROOT/../torch/include/python3.12" \
  -D CMAKE_INSTALL_RPATH="\$ORIGIN/../lib" -D CMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF \
  -D PKG_MANYBODY=on \
  -D PKG_EXTRA-PAIR=on -D PKG_EXTRA-FIX=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-DUMP=on \
  -D PKG_MISC=on -D PKG_MOLECULE=on -D PKG_RIGID=on -D PKG_MC=on -D PKG_REPLICA=on \
  2>&1 | tee cmake.log
make -j 8 2>&1 | tee make.log
make install 2>&1 | tail -3
# only libpython comes from env/torch (symlinked next to liblammps); libstdc++, libgcc_s, libmpi resolve to the system ones
ln -sf "$ROOT/../torch/lib/libpython3.12.so.1.0" "$ROOT/lib/libpython3.12.so.1.0"
"$ROOT/bin/lmp_cpumliapsys" -h | grep -E "LAMMPS \(|KOKKOS package API" | head -3
ldd "$ROOT/bin/lmp_cpumliapsys" | grep -E "python|stdc|gcc_s|mpi" | head -6
