#!/bin/bash
#SBATCH -J mliap-cpu-check -p debug -N 1 --hint=nomultithread
#SBATCH -o host_cpu_check.%j.out -e host_cpu_check.%j.err
# Deployment check of lmp_cpumliap on a CPU host (mygardenx1 / mygardenx2): single-point energies of the 108-atom test cell with
# MatterSim 5M (eager), NequIP-OAM-L (plain, no-compile) and, if env/mace exists, MACE-MPA-0 fp32 (allow_cpu copy), with 1 rank
# and with all ranks of the job (sbatch -n N), plus 100 NVE steps of 256 atoms with all ranks for the speed.
# Reference (mygarden5, GPU / CPU): MatterSim -403.17578 / -403.17566, NequIP-OAM-L -404.08095 / -404.08091, MACE -403.92018 / -403.92015 eV.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; T=$E/lammps-gpu-mliap/test; L=$E/lammps-cpu-mliap/test
cd $T
export OMP_NUM_THREADS=1 TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 CUDA_VISIBLE_DEVICES= PYTHONFAULTHANDLER=1
MPIRUN=$E/ftphase/bin/mpirun; NP=${SLURM_NTASKS:-4}
KK="-k on t 1 -sf kk -pk kokkos newton on neigh half"
X="-x PYTHONFAULTHANDLER -x TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD -x CUDA_VISIBLE_DEVICES -x OMP_NUM_THREADS"
echo "host $(hostname) job $SLURM_JOB_ID $(date) ntasks $NP"
$E/lammps-cpu-mliap/bin/lmp_cpumliap -h 2>&1 | grep -E "LAMMPS \(|KOKKOS package API" | head -2
rate() { awk '/^Loop time/{t=$4} END{printf "%.4f", t/100}' "$1"; }
run1() {  # label wrapper model
  for np in 1 $NP; do
    t0=$(date +%s)
    $MPIRUN -np $np $X $2 $KK -in in.run0 -var pot $3 -screen none -log $L/host_$1_np$np.log > $L/host_$1_np$np.err 2>&1
    echo "$1 np=$np rc=$? $(awk '/^ *Step/{getline; print "pe="$2" press="$3}' $L/host_$1_np$np.log) wall $(( $(date +%s)-t0 )) s $(grep -v Warn $L/host_$1_np$np.err | grep -m1 -E 'Error|Segmentation|malloc|free\(\)|Aborted' | cut -c1-100)"
  done
  t0=$(date +%s)
  $MPIRUN -np $NP $X $2 $KK -in in.time256 -var pre "pair_style mliap unified $3 0" -var pc "pair_coeff * * Al Li" -screen none -log $L/host_$1_256.log > $L/host_$1_256.err 2>&1
  echo "$1 256 atoms np=$NP: $(rate $L/host_$1_256.log) s/step (wall $(( $(date +%s)-t0 )) s)"
}
run1 mattersim5M $E/lammps-cpu-mliap/bin/lmp_mliap_mattersim_cpu.sh $R/potentials/mattersim/mattersim-v1.0.0-5M_mliap_nocompile.pt
run1 nequipOAML $E/lammps-cpu-mliap/bin/lmp_mliap_nequip_cpu.sh $R/potentials/nequip/NequIP-OAM-L-0.1-plain-nocompile.nequip.lmp.pt
if [ -x $E/mace/bin/python ]; then
  cat > $L/lmp_mliap_mace_cpu.sh <<EOF
#!/bin/bash
export PYTHONHOME=$E/mace TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 CUDA_VISIBLE_DEVICES=
exec $E/lammps-cpu-mliap/bin/lmp_cpumliap "\$@"
EOF
  chmod +x $L/lmp_mliap_mace_cpu.sh
  run1 maceMPA0 $L/lmp_mliap_mace_cpu.sh $R/potentials/mace/macempa0mediummodel.model-mliap_lammps-f32-cpu.pt
fi
echo "done $(date)"
