#!/bin/bash
#SBATCH -J mliap-cueq -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o bench_cueq.%j.out -e bench_cueq.%j.err
# MACE-MPA-0 fp32 through ML-IAP unified: cuEquivariance export (mace_create_lammps_model --format mliap, cuequivariance 0.13 in env/mace)
# vs the e3nn export (test/mace_to_mliap.py), GPU held exclusively: correctness (in.kk v0 plain, v1 hybrid/scaled lambda=1, v3 ufm mix)
# and s/step on 108 and 256 atoms.  Reference e3nn fp32 (Slurm 22988): pe -403.92018, 0.037 / 0.090 s/step.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials/mace; T=$E/lammps-gpu-mliap/test
cd $T
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
[ -s held_aiida_jobs.txt ] && scontrol release $(tr "\n" " " < held_aiida_jobs.txt) && echo "released $(wc -l < held_aiida_jobs.txt) held AiiDA jobs" && rm -f held_aiida_jobs.txt
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
LMP=$E/lammps-gpu-mliap/bin/lmp_mliap_mace.sh
echo "host $(hostname) job $SLURM_JOB_ID $(date)"; nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv,noheader
rate() { awk '/^Loop time/{t=$4} END{printf "%.4f", t/100}' "$1"; }
for m in "cueq $P/macempa0mediummodel-cueq.model-mliap_lammps.pt" "e3nn $P/macempa0mediummodel.model-mliap_lammps-f32.pt"; do
  set -- $m
  for v in 0 1 3; do
    t0=$(date +%s)
    $LMP $KK -in in.kk -var v $v -var pot $2 -screen none -log kk_mace_$1_v$v.log > kk_mace_$1_v$v.err 2>&1 || echo "FAILED $1 v$v: $(grep -v Warn kk_mace_$1_v$v.err | grep -m1 -iE 'error|exception' | cut -c1-160)"
    echo "$1 v$v $(awk '/^ *Step/{getline; printf "pe=%s press=%s | ", $2, $3}' kk_mace_$1_v$v.log) $(rate kk_mace_$1_v$v.log) s/step(108)  wall $(( $(date +%s) - t0 )) s"
  done
  $LMP $KK -in in.time256 -var pre "pair_style mliap unified $2 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_mace_$1.log > t256_mace_$1.err 2>&1 || echo "FAILED 256 $1: $(grep -v Warn t256_mace_$1.err | grep -m1 -iE 'error|exception' | cut -c1-160)"
  echo "$1 256 atoms: $(rate t256_mace_$1.log) s/step"
done
echo "done $(date)"
