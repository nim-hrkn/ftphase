#!/bin/bash
#SBATCH -J mliap-dyn-gpu -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o gpu_dyn.%j.out -e gpu_dyn.%j.err
# GPU device path of the forward_comm_dynamic / reverse_comm_dynamic build (lmp_gpumliapdyn, develop + PR #5301 as of 2026-11-14)
# against the production binary (lmp_gpumliap): run-0 energies of in.kk v0 (plain) and v3 (0.7 model + 0.3 ufm, hybrid/scaled/kk),
# 108 atoms, plus the same with comm_style tiled (in.run0_tiled).
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials; T=$E/lammps-gpu-mliap/test; W=$E/lammps-gpu-mliap-dyn
cd $T; L=$W/test
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
echo "host $(hostname) job $SLURM_JOB_ID $(date)"; nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
pe() { awk '/^ *Step/{getline; printf "%s", $2; exit}' "$1"; }
for m in "ms5M mattersim $P/mattersim/mattersim-v1.0.0-5M_mliap.pt" "mace_cueq mace $P/mace/macempa0mediummodel-cueq.model-mliap_lammps.pt" "sevenn0_oeq sevenn $P/sevenn/7net-0_mliap_oeq.pt" \
         "nequipL nequip $P/nequip/NequIP-OAM-L-0.1.nequip.lmp.pt"; do
  set -- $m
  for v in 0 3; do
    $E/lammps-gpu-mliap/bin/lmp_mliap_$2.sh $KK -in in.kk -var v $v -var pot $3 -screen none -log $L/old_$1_v$v.log > $L/old_$1_v$v.err 2>&1 || true
    $W/bin/lmp_mliap_$2.sh $KK -in in.kk -var v $v -var pot $3 -screen none -log $L/new_$1_v$v.log > $L/new_$1_v$v.err 2>&1 || true
    echo "$1 v$v  production pe=$(pe $L/old_$1_v$v.log)  dynamic build pe=$(pe $L/new_$1_v$v.log)  $(grep -h -m1 'ERROR' $L/new_$1_v$v.log $L/new_$1_v$v.err | cut -c1-140)"
  done
  $W/bin/lmp_mliap_$2.sh $KK -in in.run0_tiled -var pot $3 -screen none -log $L/new_$1_tiled.log > $L/new_$1_tiled.err 2>&1 || true
  echo "$1 tiled  dynamic build pe=$(pe $L/new_$1_tiled.log)  $(grep -h -m1 'ERROR' $L/new_$1_tiled.log $L/new_$1_tiled.err | cut -c1-140)"
done
echo "done $(date)"
