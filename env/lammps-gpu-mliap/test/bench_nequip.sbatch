#!/bin/bash
#SBATCH -J mliap-nequip -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o bench_nequip.%j.out -e bench_nequip.%j.err
# NequIP-OAM-L 0.1 (nequip 0.19.1, nequip-prepare-lmp-mliap export) through ML-IAP unified in lmp_gpumliap, GPU held exclusively:
# ASE reference from an AOTInductor compile of the same package on this GPU, correctness under hybrid/scaled/kk (in.kk v0..v3),
# and s/step for 100 NVE steps on 108 and 256 atoms; OpenEquivariance compiled / OEQ no-compile / plain exports.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials/nequip; T=$E/lammps-gpu-mliap/test
M=${M:-NequIP-OAM-L-0.1}; SRC=${SRC:-nequip.net:mir-group/NequIP-OAM-L:0.1}   # sbatch --export=ALL,M=NequIP-OAM-M-0.1,SRC=$P/NequIP-OAM-M-0.1.nequip.zip
if [ "$M" != NequIP-OAM-L-0.1 ]; then mkdir -p $T/$M; cp -n $T/in.kk $T/in.time256 $T/conf.data $T/nequip_ref.py $T/$M/ 2>/dev/null; cd $T/$M; else cd $T; fi
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
LMP=$E/lammps-gpu-mliap/bin/lmp_mliap_nequip.sh
PY=$E/torch/bin/python
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
export CPATH=$E/torch/include:${CPATH:-}   # AOTInductor's device_utils.h needs cuda.h (env/ftphase has it only under targets/x86_64-linux/include)
# the AiiDA GPU jobs listed in held_aiida_jobs.txt were scontrol hold-ed at submission so this job gets the GPU first; release them now
[ -s held_aiida_jobs.txt ] && scontrol release $(tr "\n" " " < held_aiida_jobs.txt) && echo "released $(wc -l < held_aiida_jobs.txt) held AiiDA jobs" && rm -f held_aiida_jobs.txt
echo "host $(hostname) job $SLURM_JOB_ID $(date)"; nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv,noheader
echo "other GPU processes: $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"
rate() { awk '/^Loop time/{t=$4} END{printf "%.4f", t/100}' "$1"; }
echo "--- ASE reference: nequip-compile aotinductor --target ase on this GPU"
rm -f nequip_ref.txt
t0=$(date +%s)
$E/torch/bin/nequip-compile $SRC $P/$M-ase.nequip.pt2 --mode aotinductor --device cuda --target ase > compile_nequip.log 2>&1 \
  && $PY nequip_ref.py $P/$M-ase.nequip.pt2 "$M (AOTI, cuda)" cuda 2>&1 | grep -v Warn | tail -1 || { echo "ASE reference FAILED"; tail -3 compile_nequip.log; }
echo "compile+ref wall $(( $(date +%s) - t0 )) s"
echo "--- correctness (run 0 pe / press): v0 plain, v1 hs lambda=1, v2 hs lambda=1.222, v3 0.7 model + 0.3 ufm; then s/step of the 100-step NVE run (108 atoms)"
for m in "oeq $P/$M.nequip.lmp.pt" "oeq_nocompile $P/$M-nocompile.nequip.lmp.pt" "plain $P/$M-plain.nequip.lmp.pt"; do
  set -- $m
  [ -f $2 ] || { echo "missing $2"; continue; }
  for v in 0 1 2 3; do
    t0=$(date +%s)
    $LMP $KK -in in.kk -var v $v -var pot $2 -screen none -log kk_nq_$1_v$v.log > kk_nq_$1_v$v.err 2>&1 || echo "FAILED $1 v$v: $(grep -m1 -iE 'error|exception' kk_nq_$1_v$v.err kk_nq_$1_v$v.log | head -1)"
    echo "$1 v$v $(awk '/^ *Step/{getline; printf "pe=%s press=%s | ", $2, $3}' kk_nq_$1_v$v.log) $(rate kk_nq_$1_v$v.log) s/step(108)  wall $(( $(date +%s) - t0 )) s"
  done
done
echo "--- 256 atoms, 100 NVE steps"
for m in "oeq $P/$M.nequip.lmp.pt" "plain $P/$M-plain.nequip.lmp.pt"; do
  set -- $m
  [ -f $2 ] || continue
  $LMP $KK -in in.time256 -var pre "pair_style mliap unified $2 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_nq_$1.log > t256_nq_$1.err 2>&1 || echo "FAILED 256 $1: $(grep -m1 -iE 'error|exception' t256_nq_$1.err t256_nq_$1.log | head -1)"
  echo "$1 256 atoms: $(rate t256_nq_$1.log) s/step"
done
nvidia-smi --query-gpu=memory.used --format=csv,noheader
echo "done $(date)"
