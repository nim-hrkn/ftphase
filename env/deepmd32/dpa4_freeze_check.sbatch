#!/bin/bash
#SBATCH -J dpa4-freeze -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o /home/kino/kino/Claude/Projects/PhaseDiagram/env/deepmd32/dpa4_freeze_check.%j.out -e /home/kino/kino/Claude/Projects/PhaseDiagram/env/deepmd32/dpa4_freeze_check.%j.err
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
R=/home/kino/kino/Claude/Projects/PhaseDiagram
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $R/env/deepmd32
export OMP_NUM_THREADS=4 DP_INTRA_OP_PARALLELISM_THREADS=4 DP_INTER_OP_PARALLELISM_THREADS=1
export CUDA_HOME=$R/env/deepmd32/lib/python3.12/site-packages/nvidia/cu13   # pip CUDA 13 toolkit (unified layout: bin/nvcc, include/cuda.h, lib) for the AOTInductor freeze
export PATH=$CUDA_HOME/bin:$PATH
cd $R/potentials/deepmd/dpa4
DATA=$R/ftphase/examples/mlip_bench/runs/mygarden5/ace/liq/lqd_x0.30.data
for v in Air Plus; do
  M=DPA4-$v-OMat24-v20260805
  echo "=== freeze $M"; t0=$(date +%s)
  DP_TRITON_INFER=2 DP_TF32_INFER=0 dp --pt freeze -c $M.pt -o $M 2>&1 | grep -v WARNING | tail -n 3
  echo "freeze took $(( $(date +%s)-t0 )) s"; ls -la $M.pt2 2>/dev/null
  echo "=== ASE reference ($M.pt2)"; python $R/env/deepmd32/test_ref.py $M.pt2 $DATA 2>&1 | grep natoms
  for inp in in.dpa in.dpa_hybrid; do
    sed "s|MODEL|$R/potentials/deepmd/dpa4/$M.pt2|; s|DATA|$DATA|" $R/env/deepmd32/$inp > $R/env/deepmd32/${inp}.$M
    echo "=== $M $inp"; t0=$(date +%s.%N)
    $R/env/deepmd32/bin/lmp_deepmd.sh -in $R/env/deepmd32/${inp}.$M 2>&1 | grep -E "^ +[0-9]+ |Loop time|ERROR|Exception|error" | head -12
    echo "wall $(echo "$(date +%s.%N)-$t0" | bc) s"
  done
done
