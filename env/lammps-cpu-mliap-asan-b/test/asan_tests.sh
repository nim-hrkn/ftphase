#!/bin/bash
# AddressSanitizer runs of the exchange-only model: plan-B build (expect no report) and unmodified stable_30Sep2026 (expect heap-buffer-overflow for wide exchanges).
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 CUDA_VISIBLE_DEVICES=
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
export ASAN_OPTIONS=detect_leaks=0:abort_on_error=0:halt_on_error=1:verify_asan_link_order=0
export OMPI_MCA_memory=^patcher PRTE_MCA_memory=^patcher
MPIRUN=$E/ftphase/bin/mpirun; KK="-k on t 1 -sf kk -pk kokkos newton on neigh half"
for b in b stable; do
  W=$E/lammps-cpu-mliap-asan-$b; cd $W/test
  PYTHONPATH=$W/test $E/torch/bin/python -c "import exch_model; exch_model.Exch().pickle('exch.pkl')"
  echo "== build $b"
  for case in "4 -" "32 -" "128 -" "256 -" "300 512" "704 704"; do set -- $case
    for cs in brick tiled; do for np in 1 4; do
      [ $b = stable ] && [ "$2" != "-" ] && D="" || D=""
      export EXCH_VECLEN=$1; X="-x EXCH_VECLEN -x PYTHONPATH -x ASAN_OPTIONS -x OMPI_MCA_memory"; if [ "$2" != "-" ]; then export EXCH_DECLARE=$2; X="$X -x EXCH_DECLARE"; else unset EXCH_DECLARE; fi
      PYTHONPATH=$W/test $MPIRUN -np $np $X $W/bin/lmp.sh $KK -in in.exch -var cs $cs -screen none -log asan_$1_$2_${cs}_$np.log > asan_$1_$2_${cs}_$np.err 2>&1; rc=$?
      echo "width $1 declared $2 $cs np=$np rc=$rc | asan: $(grep -h -m1 -o 'AddressSanitizer: [a-z-]*' asan_$1_$2_${cs}_$np.err || echo none) | $(grep -h -m1 -o 'in LAMMPS_NS::[A-Za-z:_]*' asan_$1_$2_${cs}_$np.err | head -1) | $(grep -m1 -o 'forward_ok=[A-Za-z]*' asan_$1_$2_${cs}_$np.err) $(grep -h -m1 'ERROR' asan_$1_$2_${cs}_$np.log | cut -c1-70)"
    done; done
  done
done
echo "done $(date)"
