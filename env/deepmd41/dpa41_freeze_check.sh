#!/bin/bash
# Freeze DPA-4.1-Max-OAM (user-downloaded figshare 70537500 -> potentials/deepmd/dpa4/dpa-4.1-max-oam-inference.pt) to the AOTInductor
# .pt2 on THIS GPU and compare LAMMPS (plugin) with the deepmd ASE calculator; run after env/deepmd41/build.sh.
# Usage: ./dpa41_freeze_check.sh          (on the GPU node; takes the shared GPU for ~10 min)   or   sbatch --gres=gpu:1 ... this script
R=/home/kino/kino/Claude/Projects/PhaseDiagram
E=$R/env/deepmd41
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E
export CUDA_HOME=$E; export PATH=$E/bin:$PATH   # conda CUDA 13.2 toolkit in the env root (headers linked into include/)
export OMP_NUM_THREADS=4 DP_INTRA_OP_PARALLELISM_THREADS=4 DP_INTER_OP_PARALLELISM_THREADS=1
cd $R/potentials/deepmd/dpa4
M=dpa-4.1-max-oam; DATA=$R/ftphase/examples/mlip_bench/runs/mygarden5/ace/liq/lqd_x0.30.data
if [ ! -f $M.pt2 ]; then
  echo "=== freeze $M"; t0=$(date +%s)
  # dp cuts the -o name at its first "." (dpa-4.1-max-oam -> dpa-4.pt2), so freeze under a dot-free name and rename
  DP_TRITON_INFER=2 DP_TF32_INFER=0 dp --pt freeze -c $M-inference.pt -o dpa41maxoam > freeze_$M.log 2>&1; echo "freeze exit $? after $(( $(date +%s)-t0 )) s (48 min on the RTX 3060)"
  mv dpa41maxoam.pt2 $M.pt2
fi
ls -la $M.pt2
echo "=== ASE reference"; python $R/env/deepmd32/test_ref.py $M.pt2 $DATA 2>&1 | grep natoms
for inp in in.dpa in.dpa_hybrid; do
  sed "s|MODEL|$R/potentials/deepmd/dpa4/$M.pt2|; s|DATA|$DATA|" $R/env/deepmd32/$inp > $E/${inp}.$M
  echo "=== $inp"; t0=$(date +%s.%N)
  $E/bin/lmp_deepmd.sh -in $E/${inp}.$M 2>&1 | grep -E "^ +[0-9]+ |Loop time|ERROR|Exception|implib|error" | head -12
  echo "wall $(echo "$(date +%s.%N)-$t0" | bc) s"
done
