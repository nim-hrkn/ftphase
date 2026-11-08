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
    scikit-build-core packaging dependency_groups setuptools-scm hatch-fancy-pypi-readme "e3nn==0.6.0" numpy ase
test -x $CU/bin/nvcc && test -f $CU/include/nv/target
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
export CUDAToolkit_ROOT=$CU CUDA_HOME=$CU
export PATH=$CU/bin:$E/bin:/usr/bin:/bin
export CC=/usr/bin/gcc CXX=/usr/bin/g++ CUDACXX=$CU/bin/nvcc
export DP_ENABLE_TENSORFLOW=0 DP_ENABLE_PYTORCH=1 DP_ENABLE_PADDLE=0 DP_VARIANT=cuda CMAKE_BUILD_PARALLEL_LEVEL=8
export DP_LAMMPS_VERSION=stable_22Jul2025_update2
export CMAKE_ARGS="-DCMAKE_CUDA_ARCHITECTURES=86 -DCUDAToolkit_ROOT=$CU"
$PIP install --no-build-isolation -v \
    "deepmd-kit[torch,lmp] @ git+https://github.com/deepmodeling/deepmd-kit@1ded5d2429467fb16cb1d6c3d3059fac881f82a7"
$E/bin/python -c "import deepmd, torch; print('deepmd', deepmd.__version__, 'torch', torch.__version__)"
ls $E/lib/python3.12/site-packages/deepmd/lib/
