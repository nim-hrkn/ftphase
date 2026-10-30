#!/bin/bash
#SBATCH -J mliap-cpu-mpi -p debug -N 1 -n 4 --hint=nomultithread
#SBATCH -o cpu_mpi.%j.out -e cpu_mpi.%j.err
# ML-IAP unified on the CPU with MPI ranks (no GPU, no -k on: the non-Kokkos coupling hands numpy arrays to the model):
# MatterSim 5M (eager export) and NequIP-OAM-L (plain export; OpenEquivariance is CUDA-only), 1 and 4 ranks, in.kk v0 (plain)
# and v3 (0.7 model + 0.3 ufm under hybrid/scaled), then 256 atoms.  Energies must equal the GPU runs (22999 / 23000):
# MatterSim 5M pe -403.17578 eV, NequIP-OAM-L -404.08095 eV (108 atoms, run 0).
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; T=$E/lammps-gpu-mliap/test
cd $T
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export OMP_NUM_THREADS=1 TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 CUDA_VISIBLE_DEVICES=
MPIRUN=$E/ftphase/bin/mpirun
echo "host $(hostname) job $SLURM_JOB_ID $(date) cpus $SLURM_CPUS_ON_NODE"
rate() { awk '/^Loop time/{t=$4} END{printf "%.4f", t/100}' "$1"; }
for m in "ms5M $E/lammps-gpu-mliap/bin/lmp_mliap_mattersim.sh $R/potentials/mattersim/mattersim-v1.0.0-5M_mliap_nocompile.pt" \
         "nequip_plain $E/lammps-gpu-mliap/bin/lmp_mliap_nequip.sh $R/potentials/nequip/NequIP-OAM-L-0.1-plain.nequip.lmp.pt"; do
  set -- $m
  for np in 1 4; do
    for v in 0 3; do
      t0=$(date +%s)
      $MPIRUN -np $np $2 -in in.kk -var v $v -var pot $3 -screen none -log cpu_$1_np${np}_v$v.log > cpu_$1_np${np}_v$v.err 2>&1 \
        || echo "FAILED $1 np=$np v$v: $(grep -m1 -E 'Error|error:|Exception' cpu_$1_np${np}_v$v.err cpu_$1_np${np}_v$v.log | head -1 | cut -c1-200)"
      echo "$1 np=$np v$v $(awk '/^ *Step/{getline; printf "pe=%s press=%s | ", $2, $3}' cpu_$1_np${np}_v$v.log) $(rate cpu_$1_np${np}_v$v.log) s/step(108)  wall $(( $(date +%s) - t0 )) s"
    done
  done
  $MPIRUN -np 4 $2 -in in.time256 -var pre "pair_style mliap unified $3 0" -var pc "pair_coeff * * Al Li" -screen none -log cpu_$1_256.log > cpu_$1_256.err 2>&1 \
    || echo "FAILED $1 256 np=4: $(grep -m1 -E 'Error|error:|Exception' cpu_$1_256.err cpu_$1_256.log | head -1 | cut -c1-200)"
  echo "$1 256 atoms np=4: $(rate cpu_$1_256.log) s/step"
done
echo "done $(date)"
