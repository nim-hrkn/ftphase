#!/bin/bash
# LAMMPS with pair_style mace (ACEsuit/lammps fork, branch mace) + libtorch from env/mace (cu128).  Output: bin/lmp_mace (+ wrapper).
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd); P=$ROOT/../..
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate "$P/env/mace"; set -u
cd "$ROOT"
[ -d lammps_mace ] || git clone --branch mace --depth=1 https://github.com/ACEsuit/lammps lammps_mace
for f in "$CONDA_PREFIX"/targets/x86_64-linux/include/*; do b=$(basename "$f"); [ -e "$CONDA_PREFIX/include/$b" ] || ln -s "../targets/x86_64-linux/include/$b" "$CONDA_PREFIX/include/$b"; done
mkdir -p build_mace && cd build_mace
cmake ../lammps_mace/cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX="$ROOT" -D LAMMPS_MACHINE=mace \
  -D CMAKE_PREFIX_PATH="$(python -c 'import torch;print(torch.utils.cmake_prefix_path)');$CONDA_PREFIX" -D MKL_INCLUDE_DIR=/tmp \
  -D CUDA_TOOLKIT_ROOT_DIR="$CONDA_PREFIX" -D CUDAToolkit_ROOT="$CONDA_PREFIX" -D CMAKE_CUDA_COMPILER="$CONDA_PREFIX/bin/nvcc" -D CUDA_nvrtc_LIBRARY="$CONDA_PREFIX/lib/libnvrtc.so" -D CUDA_NVRTC_LIB="$CONDA_PREFIX/lib/libnvrtc.so" \
  -D BUILD_MPI=on -D BUILD_OMP=off -D CMAKE_CXX_STANDARD=17 -D PKG_ML-MACE=on -D CMAKE_POLICY_VERSION_MINIMUM=3.5 \
  -D PKG_EXTRA-PAIR=on -D PKG_EXTRA-FIX=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-DUMP=on -D PKG_MANYBODY=on \
  -D PKG_MISC=on -D PKG_MOLECULE=on -D PKG_RIGID=on -D PKG_MC=on -D PKG_REPLICA=on 2>&1 | tee cmake.log
make -j 12 2>&1 | tee make.log
make install 2>&1 | tail -1
TL=$(python -c 'import torch, os; print(os.path.join(os.path.dirname(torch.__file__), "lib"))')
cat > "$ROOT/bin/lmp_mace.sh" <<EOW
#!/bin/bash
# libtorch on the library path, and "atom_modify map yes" prepended to the -in script: pair_style mace segfaults
# without an atom map, and calphy 2.3's executable runner rejects atom_modify as an md.init_commands entry
export LD_LIBRARY_PATH=$TL:$CONDA_PREFIX/lib:\${LD_LIBRARY_PATH:-}
args=("\$@")
for ((i=0; i<\${#args[@]}; i++)); do
  if [ "\${args[\$i]}" = "-in" ] && [ -f "\${args[\$((i+1))]}" ]; then
    f="\${args[\$((i+1))]}"; t="\${f}.mace.lmp"
    { echo "atom_modify map yes"; cat "\$f"; } > "\$t"; args[\$((i+1))]="\$t"
  fi
done
exec $ROOT/bin/lmp_mace "\${args[@]}"
EOW
#!/bin/bash
export LD_LIBRARY_PATH=$TL:$CONDA_PREFIX/lib:\${LD_LIBRARY_PATH:-}
exec $ROOT/bin/lmp_mace "\$@"
EOW
chmod +x "$ROOT/bin/lmp_mace.sh"
"$ROOT/bin/lmp_mace.sh" -h | sed -n '/Pair styles/,/Fix styles/p' | tr ' ' '\n' | grep -E "^(mace|hybrid/scaled|ufm)" | sort -u | tr '\n' ' '
