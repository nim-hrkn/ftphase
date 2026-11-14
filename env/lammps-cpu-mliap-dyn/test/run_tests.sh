#!/bin/bash
# Tests of the forward_comm_dynamic / reverse_comm_dynamic variant (Plimpton's proposal of 2026-11-13 on PR #5301):
# CommBrick/CommTiled forward_comm(Pair *) unchanged from develop, pair mliap/kk calls the *_dynamic methods.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; W=$E/lammps-cpu-mliap-dyn; T=$E/lammps-gpu-mliap/test
cd $W/test
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 CUDA_VISIBLE_DEVICES=
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
MPIRUN=$E/ftphase/bin/mpirun; KK="-k on t 1 -sf kk -pk kokkos newton on neigh half"
PYTHONPATH=$W/test $E/torch/bin/python -c "import exch_model; exch_model.Exch().pickle(\"exch.pkl\"); print(\"wrote exch.pkl\")"
echo "== exchange test: width / comm_style / ranks"
for w in 4 32 128 256 300 704; do
  for cs in brick tiled; do for np in 1 4; do
    export EXCH_VECLEN=$w; unset EXCH_DECLARE
    PYTHONPATH=$W/test $MPIRUN -np $np -x EXCH_VECLEN -x PYTHONPATH $W/bin/lmp_mliap_mattersim_cpu.sh $KK -in in.exch -var cs $cs -screen none -log exch_${w}_${cs}_$np.log > exch_${w}_${cs}_$np.err 2>&1; rc=$?
    echo "width $w $cs np=$np rc=$rc | $(grep -m1 'EXCH k=' exch_${w}_${cs}_$np.err | cut -c1-120) $(grep -h -m1 'ERROR' exch_${w}_${cs}_$np.log exch_${w}_${cs}_$np.err | cut -c1-150)"
  done; done
done
echo "== real models (reference 108 atoms: MatterSim 5M -403.1757, NequIP-OAM-L -404.0809 eV)"
for m in "ms5M $W/bin/lmp_mliap_mattersim_cpu.sh $R/potentials/mattersim/mattersim-v1.0.0-5M_mliap_nocompile.pt" \
         "nequipL $W/bin/lmp_mliap_nequip_cpu.sh $R/potentials/nequip/NequIP-OAM-L-0.1-plain-nocompile.nequip.lmp.pt"; do set -- $m
  for np in 1 4; do for v in 0 3; do
    $MPIRUN -np $np $2 $KK -in $T/in.kk -var v $v -var pot $3 -screen none -log kk_$1_np${np}_v$v.log > kk_$1_np${np}_v$v.err 2>&1 || echo "FAILED $1 np=$np v$v: $(grep -h -m1 -E 'ERROR|Error|Exception' kk_$1_np${np}_v$v.err kk_$1_np${np}_v$v.log | head -1 | cut -c1-200)"
    echo "$1 np=$np v$v $(awk '/^ *Step/{getline; printf "pe=%s press=%s | ", $2, $3}' kk_$1_np${np}_v$v.log)"
  done; done
  $MPIRUN -np 4 $2 $KK -in $T/in.run0_tiled -var pot $3 -screen none -log tiled_$1.log > tiled_$1.err 2>&1; echo "$1 tiled np=4 $(awk '/^ *Step/{getline; printf "pe=%s", $2}' tiled_$1.log)"
done
echo "done $(date)"
