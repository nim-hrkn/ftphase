#!/bin/bash
# examples/melt (brick, tiled) and examples/mliap unified LJ on the *_dynamic build: thermo output vs the reference logs.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; W=$E/lammps-cpu-mliap-dyn; S=$E/lammps-gpu/worktree-develop
cd $W/regress
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false CUDA_VISIBLE_DEVICES= PYTHONPATH=$S/python
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
MPIRUN=$E/ftphase/bin/mpirun; KK="-k on t 1 -sf kk -pk kokkos newton on neigh half"
thermo() { awk '/^ *Step/{f=1;next} /^Loop/{f=0} f' "$1"; }
for np in 1 4; do
  for case in "in.melt $S/examples/melt/log.8Apr21.melt.g++.$np" "in.melt_tiled $S/examples/melt/log.8Apr21.melt.g++.$np" "in.mliap.unified.lj.Ar $S/examples/mliap/log.23Sep22.mliap.unified.lj.Ar.g++.$np"; do set -- $case
    for mode in plain kk; do
      [ $mode = kk ] && A="$KK" || A=""
      $MPIRUN -np $np -x PYTHONPATH $W/bin/lmp_mliap_mattersim_cpu.sh $A -in $1 -screen none -log log.$1.$np.$mode > err.$1.$np.$mode 2>&1; rc=$?
      if diff <(thermo log.$1.$np.$mode) <(thermo $2) > /dev/null; then r="thermo = reference"; else r="DIFFERS: $(diff <(thermo log.$1.$np.$mode) <(thermo $2) | head -4 | tr '\n' ' ')"; fi
      echo "$1 np=$np $mode rc=$rc $r $(grep -c WARNING log.$1.$np.$mode) warnings"
    done
  done
done
echo "done $(date)"
