#!/bin/bash
# env/deepmd41: deepmd-kit at the commit the DPA-4.1 Matbench models were run with (1ded5d2, 2026-11), built from source
# with torch 2.13.0+cu132 (as in matbench-discovery models/deepmd/dpa41-env/pyproject.toml), the CUDA custom ops (DP_VARIANT=cuda,
# pip CUDA 13.2 toolkit: nvcc + CCCL + runtime under site-packages/nvidia/cu13) and the LAMMPS plugin (DP_LAMMPS_VERSION ->
# cmake FetchContent of LAMMPS stable_22Jul2025_update2, matching the PyPI `lammps[mpi]~=2025.7.22.2.0` wheel of the lmp extra).
#   mamba create -p ./env/deepmd41 -c conda-forge python=3.12 pip cmake ninja
#   ./env/deepmd41/bin/pip install "torch==2.13.0+cu132" --index-url https://download.pytorch.org/whl/cu132
#   ./env/deepmd41/build.sh
set -e
R=/home/kino/kino/Claude/Projects/PhaseDiagram
E=$R/env/deepmd41
PIP=$E/bin/pip
CU=$E/lib/python3.12/site-packages/nvidia/cu13
$PIP install "nvidia-cuda-nvcc==13.2.*" "nvidia-cuda-cccl==13.2.*" "nvidia-cuda-runtime==13.2.*" \
    scikit-build-core packaging dependency_groups setuptools-scm hatch-fancy-pypi-readme "e3nn==0.6.0" numpy ase "tensorflow-cpu==2.18.1"
# tensorflow-cpu: the C++ interface that carries the LAMMPS plugin (DP_LAMMPS_VERSION) sets USE_TF_PYTHON_LIBS and insists on
# TensorFlow headers (Findtensorflow.cmake FATAL_ERROR with DP_ENABLE_TENSORFLOW=0), so TF is built in as in the PyPI wheels
test -x $CU/bin/nvcc && test -f $CU/include/nv/target
# the pip CUDA wheels ship only versioned sonames (libcudart.so.13 ...); CMake's FindCUDAToolkit wants the unversioned names
for f in $CU/lib/lib*.so.[0-9]*; do b=$(basename $f); u=${b%%.so.*}.so; [ -e $CU/lib/$u ] || ln -s $b $CU/lib/$u; done
ls -l $CU/lib/libcudart.so
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
# CUDA compiler: the conda-forge CUDA 13.2 toolkit in the env root (cuda-nvcc, cuda-cudart-dev, cuda-cccl, cuda-nvrtc-dev, cuda-version=13.2);
# the pip nvidia-cuda-nvcc 13.2.86 failed CMake's compiler identification (its ptxas rejected the PTX: "Unsupported .version 9.5; current version is '9.2'")
#   mamba install -p ./env/deepmd41 -c conda-forge "cuda-nvcc=13.2" "cuda-cudart-dev=13.2" "cuda-cccl=13.2" "cuda-nvrtc-dev=13.2" "cuda-version=13.2"
test -x $E/bin/nvcc
# torch's TorchConfig uses the legacy FindCUDA module, which wants headers under <root>/include; conda puts them in targets/x86_64-linux/include
mkdir -p $E/include; for f in $E/targets/x86_64-linux/include/*; do b=$(basename $f); [ -e $E/include/$b ] || ln -s ../targets/x86_64-linux/include/$b $E/include/$b; done
export CUDA_PATH=$E
# CUDA libraries the ops link: libcublas-dev (CUDA::cublasLt) and libcufft-dev (CUDA::cufft) from conda-forge, same cuda-version=13.2
#   mamba install -p ./env/deepmd41 -c conda-forge libcublas-dev libcufft-dev "cuda-version=13.2"
test -f $E/targets/x86_64-linux/include/cublas_v2.h && test -f $E/targets/x86_64-linux/include/cufft.h
# MPI: use the pip mpich (5.0.2, installed with lammps[mpi]) instead of the Intel oneAPI MPI that FindMPI picked up via I_MPI_ROOT
$PIP install mpich "lammps[mpi]~=2025.7.22.2.0"
unset I_MPI_ROOT MPI_HOME; export MPI_HOME=$E MPI_C_COMPILER=$E/bin/mpicc MPI_CXX_COMPILER=$E/bin/mpicxx
export CUDAToolkit_ROOT=$E CUDA_HOME=$E
export PATH=$E/bin:/usr/bin:/bin
export CC=/usr/bin/gcc CXX=/usr/bin/g++ CUDACXX=$E/bin/nvcc
export DP_ENABLE_TENSORFLOW=1 DP_ENABLE_PYTORCH=1 DP_ENABLE_PADDLE=0 DP_VARIANT=cuda CMAKE_BUILD_PARALLEL_LEVEL=8
export DP_LAMMPS_VERSION=stable_22Jul2025_update2
export CMAKE_ARGS="-DCMAKE_CUDA_ARCHITECTURES=86 -DCUDAToolkit_ROOT=$E"
$PIP install --no-build-isolation -v \
    "deepmd-kit[torch,lmp] @ git+https://github.com/deepmodeling/deepmd-kit@1ded5d2429467fb16cb1d6c3d3059fac881f82a7"
$E/bin/python -c "import deepmd, torch; print('deepmd', deepmd.__version__, 'torch', torch.__version__)"
ls $E/lib/python3.12/site-packages/deepmd/lib/
