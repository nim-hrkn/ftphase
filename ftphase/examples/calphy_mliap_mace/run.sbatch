#!/bin/bash
#SBATCH -J mliap-calphy -p debug -N 1 -n 1 --hint=nomultithread --gres=gpu:1 --mem=16G
#SBATCH -o run.%j.out -e run.%j.err
# One calphy liquid run (MACE-MPA-0 fp32 through ML-IAP unified, lmp_gpumliap) with the same
# resources as the AiiDA CalcJob pk 4356 (1 task, 1 GPU, env/ftphase, calphy_kernel in executable mode).
R=/home/kino/kino/Claude/Projects/PhaseDiagram
cd "${SLURM_SUBMIT_DIR:-$R/ftphase/examples/calphy_mliap_mace}"   # $0 is slurmd's copy of the script
source /home/kino/miniforge3/etc/profile.d/conda.sh && conda activate $R/env/ftphase
set -u
export OMP_NUM_THREADS=1
unset PYTHONPATH
echo "host $(hostname) job $SLURM_JOB_ID start $(date)"
nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv,noheader
echo "other GPU processes: $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"

# pre-check: the liquid cell with pair_style mliap unified, plain and under hybrid/scaled/kk, without atom_modify
# (calphy cannot add init commands; the ML-IAP path needs no atom map)
LMP=$R/env/lammps-gpu-mliap/bin/lmp_mliap_mace.sh
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
MODEL=$R/potentials/mace/macempa0mediummodel.model-mliap_lammps-f32.pt
cat > precheck.lmp <<EOF
units metal
boundary p p p
atom_style atomic
read_data lqd_x0.00.data
mass 1 26.9815
mass 2 6.94
thermo_style custom step pe press vol
pair_style mliap unified $MODEL 0
pair_coeff * * Al Li
run 0
variable lam equal 1.0
pair_style hybrid/scaled v_lam mliap unified $MODEL 0
pair_coeff * * mliap Al Li
run 0
EOF
$LMP $KK -in precheck.lmp -screen none -log precheck.log > precheck.err 2>&1 || { echo "precheck FAILED"; tail -5 precheck.err precheck.log; exit 1; }
awk '/^ *Step/{getline; print "precheck pe press vol:", $2, $3, $4}' precheck.log

t0=$(date +%s)
calphy_kernel -i input.yaml -k 0 > calphy.out 2> calphy.err
rc=$?
echo "calphy_kernel exit $rc, wall $(( $(date +%s) - t0 )) s, end $(date)"
ls lqd_x0.00-ts-*/report.yaml 2>/dev/null && cat lqd_x0.00-ts-*/report.yaml
exit $rc
