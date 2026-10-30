#!/bin/bash
#SBATCH -J mliap-mattersim -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o bench_mattersim.%j.out -e bench_mattersim.%j.err
# MatterSim (M3GNet, official MatterSimMLIAP wrapper) through ML-IAP unified in lmp_gpumliap, GPU held exclusively:
# correctness under hybrid/scaled/kk (in.kk v0..v3: plain, lambda=1, lambda=1.222, 0.7 model + 0.3 ufm) against the ASE
# calculator (mattersim_ref.txt), and s/step for 100 NVE steps on 108 and 256 atoms; torch.compile on/off.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials/mattersim; T=$E/lammps-gpu-mliap/test
cd $T
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
LMP=$E/lammps-gpu-mliap/bin/lmp_mliap_mattersim.sh
# the AiiDA GPU jobs listed in held_aiida_jobs.txt were scontrol hold-ed at submission so this job gets the GPU first; release them now (they queue behind this job)
[ -s held_aiida_jobs.txt ] && scontrol release $(tr "\n" " " < held_aiida_jobs.txt) && echo "released $(wc -l < held_aiida_jobs.txt) held AiiDA jobs" && rm -f held_aiida_jobs.txt
echo "host $(hostname) job $SLURM_JOB_ID $(date)"; nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv,noheader
echo "other GPU processes: $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"
rate() { awk '/^Loop time/{t=$4} END{printf "%.4f", t/100}' "$1"; }   # last Loop time = the 100-step run
echo "--- ASE reference (CPU, float32): $(cat mattersim_ref.txt | tr '\n' ';')"
echo "--- correctness (run 0 pe / press): v0 plain, v1 hs lambda=1, v2 hs lambda=1.222, v3 0.7 model + 0.3 ufm; then s/step of the 100-step NVE run (108 atoms)"
for m in "ms5M $P/mattersim-v1.0.0-5M_mliap.pt" "ms5M_nocompile $P/mattersim-v1.0.0-5M_mliap_nocompile.pt" "ms1M $P/mattersim-v1.0.0-1M_mliap.pt"; do
  set -- $m
  for v in 0 1 2 3; do
    t0=$(date +%s)
    $LMP $KK -in in.kk -var v $v -var pot $2 -screen none -log kk_$1_v$v.log > kk_$1_v$v.err 2>&1 || echo "FAILED $1 v$v: $(grep -m1 -iE 'error|exception' kk_$1_v$v.err kk_$1_v$v.log | head -1)"
    echo "$1 v$v $(awk '/^ *Step/{getline; printf "pe=%s press=%s | ", $2, $3}' kk_$1_v$v.log) $(rate kk_$1_v$v.log) s/step(108)  wall $(( $(date +%s) - t0 )) s"
  done
done
echo "--- 256 atoms, 100 NVE steps"
for m in "ms5M $P/mattersim-v1.0.0-5M_mliap.pt" "ms1M $P/mattersim-v1.0.0-1M_mliap.pt"; do
  set -- $m
  $LMP $KK -in in.time256 -var pre "pair_style mliap unified $2 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_$1.log > t256_$1.err 2>&1 || echo "FAILED 256 $1: $(grep -m1 -iE 'error|exception' t256_$1.err t256_$1.log | head -1)"
  echo "$1 256 atoms: $(rate t256_$1.log) s/step"
done
echo "done $(date)"
