#!/bin/bash
#SBATCH -J pet-check -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o /home/kino/kino/Claude/Projects/PhaseDiagram/env/metatomic/test/pet_check.%j.out -e /home/kino/kino/Claude/Projects/PhaseDiagram/env/metatomic/test/pet_check.%j.err
unset PYTHONPATH PYTHONHOME
R=/home/kino/kino/Claude/Projects/PhaseDiagram
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $R/env/metatomic
cd $R/env/metatomic/test
DATA=$R/ftphase/examples/mlip_bench/runs/mygarden5/ace/liq/lqd_x0.30.data
for m in pet-omat-s-v1.0.0 pet-oam-l-v0.1.0; do
  M=$R/potentials/pet/$m.pt
  echo "=== $m ASE reference"; python pet_ref.py $M $DATA
  for inp in in.pet in.pet_hybrid; do
    sed "s|MODEL|$M|; s|DATA|$DATA|" $inp > ${inp}.$m
    echo "=== $m $inp kokkos"; t0=$(date +%s.%N)
    lmp -k on g 1 -sf kk -pk kokkos newton on neigh half -in ${inp}.$m 2>&1 | grep -E "^ +[0-9]+ |Loop time|ERROR|Warning|metatomic" | head -20
    echo "wall $(echo "$(date +%s.%N)-$t0" | bc) s"
  done
  echo "=== $m in.pet non-kokkos (device cuda)"
  sed "s|MODEL|$M device cuda|; s|DATA|$DATA|" in.pet > in.pet.$m.cpu
  lmp -in in.pet.$m.cpu 2>&1 | grep -E "^ +[0-9]+ |Loop time|ERROR" | head -8
done
