#!/bin/bash
# AddressSanitizer runs of the exchange-only model on the forward_comm_dynamic / reverse_comm_dynamic build (expect no report).
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 CUDA_VISIBLE_DEVICES=
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
export ASAN_OPTIONS=detect_leaks=0:abort_on_error=0:halt_on_error=1:verify_asan_link_order=0
export OMPI_MCA_memory=^patcher PRTE_MCA_memory=^patcher
MPIRUN=$E/ftphase/bin/mpirun; KK="-k on t 1 -sf kk -pk kokkos newton on neigh half"
W=$E/lammps-cpu-mliap-asan-dyn; cd $W/test
PYTHONPATH=$W/test $E/torch/bin/python -c "import exch_model; exch_model.Exch().pickle('exch.pkl')"
for w in 4 32 128 256 300 704; do
  for cs in brick tiled; do for np in 1 4; do
    export EXCH_VECLEN=$w; X="-x EXCH_VECLEN -x PYTHONPATH -x ASAN_OPTIONS -x OMPI_MCA_memory"
    PYTHONPATH=$W/test $MPIRUN -np $np $X $W/bin/lmp.sh $KK -in in.exch -var cs $cs -screen none -log asan_${w}_${cs}_$np.log > asan_${w}_${cs}_$np.err 2>&1; rc=$?
    echo "width $w $cs np=$np rc=$rc | asan: $(grep -h -m1 -o 'AddressSanitizer: [a-z-]*' asan_${w}_${cs}_$np.err || echo none) | $(grep -h -m1 -o 'in LAMMPS_NS::[A-Za-z:_]*' asan_${w}_${cs}_$np.err | head -1) | $(grep -m1 -o 'forward_ok=[A-Za-z]*' asan_${w}_${cs}_$np.err) $(grep -h -m1 'ERROR' asan_${w}_${cs}_$np.log | cut -c1-70)"
  done; done
done
# melt under ASan too: the unchanged forward_comm(Pair *) path
cp $E/lammps-cpu-mliap-dyn/regress/in.melt $E/lammps-cpu-mliap-dyn/regress/in.melt_tiled . 
for i in in.melt in.melt_tiled; do $MPIRUN -np 4 -x ASAN_OPTIONS -x OMPI_MCA_memory $W/bin/lmp.sh -in $i -screen none -log asan_$i.log > asan_$i.err 2>&1; echo "$i np=4 rc=$? asan: $(grep -h -m1 -o 'AddressSanitizer: [a-z-]*' asan_$i.err || echo none)"; done
echo "done $(date)"
