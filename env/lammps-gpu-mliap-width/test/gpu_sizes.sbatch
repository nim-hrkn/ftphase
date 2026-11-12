#!/bin/bash
#SBATCH -J mliap-width-sizes -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o gpu_sizes.%j.out -e gpu_sizes.%j.err
# Find the largest exchange width of each unified model (declare a width, run, raise it to the width named in the error until the
# run passes) and compare the energies of the declared-width build with the production binary (in.kk v0 plain, v3 hybrid/scaled + ufm).
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials; T=$E/lammps-gpu-mliap/test; W=$E/lammps-gpu-mliap-width
cd $T; L=$W/test
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u
export LD_LIBRARY_PATH=$(echo "${LD_LIBRARY_PATH:-}" | tr ":" "\n" | grep -v "/opt/intel" | paste -sd: -)
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
echo "host $(hostname) job $SLURM_JOB_ID $(date)"
pe() { awk '/^ *Step/{getline; printf "%s", $2; exit}' "$1"; }
for m in "nequipS nequip torch $P/nequip/NequIP-OAM-S-0.1.nequip.lmp.pt" "nequipM nequip torch $P/nequip/NequIP-OAM-M-0.1.nequip.lmp.pt" "nequipL nequip torch $P/nequip/NequIP-OAM-L-0.1.nequip.lmp.pt" "nequipL_plain nequip torch $P/nequip/NequIP-OAM-L-0.1-plain.nequip.lmp.pt" "ms1M mattersim torch $P/mattersim/mattersim-v1.0.0-1M_mliap.pt" "ms5M mattersim torch $P/mattersim/mattersim-v1.0.0-5M_mliap.pt" \
         "mace_e3nn_f32 mace mace $P/mace/macempa0mediummodel.model-mliap_lammps-f32.pt" "mace_cueq mace mace $P/mace/macempa0mediummodel-cueq.model-mliap_lammps.pt"; do
  set -- $m; name=$1; wr=$2; env=$3; src=$4; w=1; hist=""
  for it in 1 2 3 4 5 6 7 8; do
    TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 $E/$env/bin/python -c "
import torch
m=torch.load('$src', weights_only=False); m.comm_width=$w; torch.save(m,'$L/decl_$name.pt')" > $L/decl_$name.log 2>&1
    $W/bin/lmp_mliap_$wr.sh $KK -in in.kk -var v 0 -var pot $L/decl_$name.pt -screen none -log $L/decl_${name}_v0.log > $L/decl_${name}_v0.err 2>&1
    nw=$(grep -h -o "exchange width [0-9]*" $L/decl_${name}_v0.log $L/decl_${name}_v0.err | head -1 | awk '{print $3}')
    hist="$hist $w"; [ -z "$nw" ] && break; w=$nw
  done
  $W/bin/lmp_mliap_$wr.sh $KK -in in.kk -var v 3 -var pot $L/decl_$name.pt -screen none -log $L/decl_${name}_v3.log > $L/decl_${name}_v3.err 2>&1
  for v in 0 3; do $E/lammps-gpu-mliap/bin/lmp_mliap_$wr.sh $KK -in in.kk -var v $v -var pot $src -screen none -log $L/prod_${name}_v$v.log > $L/prod_${name}_v$v.err 2>&1; done
  echo "$name: declared widths tried:$hist -> max exchange width $w | v0 production $(pe $L/prod_${name}_v0.log) declared $(pe $L/decl_${name}_v0.log) | v3 production $(pe $L/prod_${name}_v3.log) declared $(pe $L/decl_${name}_v3.log) | $(grep -h -m1 'ERROR' $L/decl_${name}_v3.log | cut -c1-100)"
done
echo "done $(date)"
