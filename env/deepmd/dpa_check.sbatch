#!/bin/bash
#SBATCH -J dpa-check -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o /home/kino/kino/Claude/Projects/PhaseDiagram/env/deepmd/dpa_check.%j.out -e /home/kino/kino/Claude/Projects/PhaseDiagram/env/deepmd/dpa_check.%j.err
unset PYTHONPATH PYTHONHOME
R=/home/kino/kino/Claude/Projects/PhaseDiagram
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $R/env/deepmd
cd $R/env/deepmd
DATA=$R/ftphase/examples/mlip_bench/runs/mygarden5/ace/liq/lqd_x0.30.data
M=$R/potentials/deepmd/dpa-3.1-3m-ft.pth
echo "=== ASE reference"; python test_ref.py $M $DATA 2>&1 | grep natoms
for inp in in.dpa in.dpa_hybrid; do
  sed "s|MODEL|$M|; s|DATA|$DATA|" $inp > ${inp}.run
  echo "=== $inp"; t0=$(date +%s.%N)
  $R/env/deepmd/bin/lmp_deepmd.sh -in ${inp}.run 2>&1 | grep -E "^ +[0-9]+ |Loop time|ERROR|Warning|plugin|deepmd" | head -20
  echo "wall $(echo "$(date +%s.%N)-$t0" | bc) s"
done
nvidia-smi --query-gpu=name --format=csv,noheader
