#!/bin/bash
#SBATCH -J mliap-width-gpu -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o gpu_width.%j.out -e gpu_width.%j.err
# GPU device path of the "declared comm width" pair mliap/kk (lmp_gpumliapw, unpatched Comm) against the production binary
# (lmp_gpumliap, patched Comm): run-0 energies of in.kk v0 (plain) and v3 (0.7 model + 0.3 ufm under hybrid/scaled/kk), 108 atoms.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials; T=$E/lammps-gpu-mliap/test; W=$E/lammps-gpu-mliap-width
cd $T; L=$W/test
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
echo "host $(hostname) job $SLURM_JOB_ID $(date)"; nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
# NequIP copy that declares its width
TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 $E/torch/bin/python -c "
import torch
m=torch.load('$P/nequip/NequIP-OAM-L-0.1.nequip.lmp.pt', weights_only=False); m.comm_width=704; torch.save(m,'$L/nequip_oeq_declared704.pt'); print('declared copy written')" 2>&1 | tail -n 1
pe() { awk '/^ *Step/{getline; printf "%s", $2; exit}' "$1"; }
for m in "ms5M mattersim $P/mattersim/mattersim-v1.0.0-5M_mliap.pt" "mace_cueq mace $P/mace/macempa0mediummodel-cueq.model-mliap_lammps.pt" "sevenn0_oeq sevenn $P/sevenn/7net-0_mliap_oeq.pt" \
         "nequipL_undeclared nequip $P/nequip/NequIP-OAM-L-0.1.nequip.lmp.pt" "nequipL_declared704 nequip $L/nequip_oeq_declared704.pt"; do
  set -- $m
  for v in 0 3; do
    $E/lammps-gpu-mliap/bin/lmp_mliap_$2.sh $KK -in in.kk -var v $v -var pot $3 -screen none -log $L/old_$1_v$v.log > $L/old_$1_v$v.err 2>&1 || true
    $W/bin/lmp_mliap_$2.sh $KK -in in.kk -var v $v -var pot $3 -screen none -log $L/new_$1_v$v.log > $L/new_$1_v$v.err 2>&1 || true
    echo "$1 v$v  production(patched Comm) pe=$(pe $L/old_$1_v$v.log)  declared-width build pe=$(pe $L/new_$1_v$v.log)  $(grep -h -m1 'ERROR' $L/new_$1_v$v.log $L/new_$1_v$v.err | cut -c1-140)"
  done
done
echo "done $(date)"
