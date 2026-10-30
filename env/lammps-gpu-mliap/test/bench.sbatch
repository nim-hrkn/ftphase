#!/bin/bash
#SBATCH -J mliap-bench -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o bench.%j.out -e bench.%j.err
# ML-IAP unified (lmp_gpumliap, Kokkos coupling) vs the libtorch pair styles (lmp_mace / lmp_sevenn):
# correctness inside hybrid/scaled (run 0: plain, lambda=1, lambda=1.222, 0.7 model + 0.3 ufm) and
# s/step for 100 NVE steps on 108 and 256 atoms, all with the GPU held exclusively by this job.

R=/home/kino/kino/Claude/Projects/PhaseDiagram; E=$R/env; P=$R/potentials; T=$E/lammps-gpu-mliap/test
cd $T
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate $E/ftphase; set -u   # OpenMPI, CUDA runtime (set -u only after activate: its hooks use unset vars)
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 MACE_ALLOW_CPU=false
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
LMP=$E/lammps-gpu-mliap/bin/lmp_gpumliap
until [ -x $LMP ] && ! pgrep -f lammps-gpu-mliap/build.sh >/dev/null; do sleep 30; done   # wait for the build to finish
echo "host $(hostname) job $SLURM_JOB_ID $(date)"; nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv,noheader
echo "other GPU processes: $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"
rate() { awk '/^Loop time/{t=$4} END{printf "%.4f", t/100}' "$1"; }   # last Loop time = the 100-step run
pe0() { awk '/^ *Step/{getline; print $2; exit}' "$1"; }
echo "--- correctness (run 0 pe / press): v0 plain, v1 hs lambda=1, v2 hs lambda=1.222, v3 0.7 model + 0.3 ufm"
for m in "mace64 $P/mace/macempa0mediummodel.model-mliap_lammps.pt $E/mace" "mace32 $P/mace/macempa0mediummodel.model-mliap_lammps-f32.pt $E/mace" "sevenn0 $P/sevenn/7net-0_mliap.pt $E/torch" "sevenn0oeq $P/sevenn/7net-0_mliap_oeq.pt $E/torch"; do
  set -- $m
  for v in 0 1 2 3; do
    PYTHONHOME=$3 $LMP $KK -in in.kk -var v $v -var pot $2 -screen none -log kk_$1_v$v.log > kk_$1_v$v.err 2>&1 || echo "FAILED $1 v$v: $(grep -m1 -iE 'error|exception' kk_$1_v$v.err kk_$1_v$v.log | head -1)"
    echo "$1 v$v $(awk '/^ *Step/{getline; printf "pe=%s press=%s | ", $2, $3}' kk_$1_v$v.log) $(rate kk_$1_v$v.log) s/step(108)"
  done
done
echo "--- libtorch pair styles, 108 atoms"
$E/lammps-torch/bin/lmp_mace.sh -in in.time.mace -var ps "mace no_domain_decomposition" -var pot $P/mace/macempa0mediummodel.model-lammps.pt -screen none -log pm_mace64.log > pm_mace64.err 2>&1; echo "pair mace fp64 pe0=$(pe0 pm_mace64.log) $(rate pm_mace64.log) s/step"
$E/lammps-torch/bin/lmp_mace.sh -in in.time.mace -var ps "mace no_domain_decomposition" -var pot $P/mace/macempa0mediummodel.model-lammps-f32.pt -screen none -log pm_mace32.log > pm_mace32.err 2>&1; echo "pair mace fp32 pe0=$(pe0 pm_mace32.log) $(rate pm_mace32.log) s/step"
$E/lammps-torch/bin/lmp_sevenn.sh -in in.time -var ps e3gnn -var pot $P/sevenn/7net-0_oeq.pt -screen none -log pm_e3gnn_oeq.log > pm_e3gnn_oeq.err 2>&1; echo "pair e3gnn oeq pe0=$(pe0 pm_e3gnn_oeq.log) $(rate pm_e3gnn_oeq.log) s/step"
LD_LIBRARY_PATH=$E/torch/lib/python3.12/site-packages/torch/lib:$E/torch/lib $E/lammps-torch/bin/lmp_sevenn_nooeq -in in.time -var ps e3gnn -var pot $P/sevenn/7net-0.pt -screen none -log pm_e3gnn_nooeq.log > pm_e3gnn_nooeq.err 2>&1; echo "pair e3gnn no-oeq pe0=$(pe0 pm_e3gnn_nooeq.log) $(rate pm_e3gnn_nooeq.log) s/step"
echo "--- 256 atoms"
PYTHONHOME=$E/mace $LMP $KK -in in.time256 -var pre "pair_style mliap unified $P/mace/macempa0mediummodel.model-mliap_lammps.pt 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_kk_mace64.log > t256_kk_mace64.err 2>&1; echo "mliap mace fp64 256: pe0=$(pe0 t256_kk_mace64.log) $(rate t256_kk_mace64.log) s/step"
PYTHONHOME=$E/mace $LMP $KK -in in.time256 -var pre "pair_style mliap unified $P/mace/macempa0mediummodel.model-mliap_lammps-f32.pt 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_kk_mace32.log > t256_kk_mace32.err 2>&1; echo "mliap mace fp32 256: pe0=$(pe0 t256_kk_mace32.log) $(rate t256_kk_mace32.log) s/step"
PYTHONHOME=$E/torch $LMP $KK -in in.time256 -var pre "pair_style mliap unified $P/sevenn/7net-0_mliap.pt 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_kk_sevenn0.log > t256_kk_sevenn0.err 2>&1; PYTHONHOME=$E/torch $LMP $KK -in in.time256 -var pre "pair_style mliap unified $P/sevenn/7net-0_mliap_oeq.pt 0" -var pc "pair_coeff * * Al Li" -screen none -log t256_kk_sevenn0oeq.log > t256_kk_sevenn0oeq.err 2>&1; echo "mliap sevenn0 oeq 256: pe0=$(pe0 t256_kk_sevenn0oeq.log) $(rate t256_kk_sevenn0oeq.log) s/step"
echo "mliap sevenn0 256: pe0=$(pe0 t256_kk_sevenn0.log) $(rate t256_kk_sevenn0.log) s/step"
$E/lammps-torch/bin/lmp_mace.sh -in in.time256.mace -var pre "pair_style mace no_domain_decomposition" -var pc "pair_coeff * * $P/mace/macempa0mediummodel.model-lammps.pt Al Li" -screen none -log t256_pm_mace64.log > t256_pm_mace64.err 2>&1; echo "pair mace fp64 256: pe0=$(pe0 t256_pm_mace64.log) $(rate t256_pm_mace64.log) s/step"
$E/lammps-torch/bin/lmp_mace.sh -in in.time256.mace -var pre "pair_style mace no_domain_decomposition" -var pc "pair_coeff * * $P/mace/macempa0mediummodel.model-lammps-f32.pt Al Li" -screen none -log t256_pm_mace32.log > t256_pm_mace32.err 2>&1; echo "pair mace fp32 256: pe0=$(pe0 t256_pm_mace32.log) $(rate t256_pm_mace32.log) s/step"
$E/lammps-torch/bin/lmp_sevenn.sh -in in.time256 -var pre "pair_style e3gnn" -var pc "pair_coeff * * $P/sevenn/7net-0_oeq.pt Al Li" -screen none -log t256_pm_e3gnn.log > t256_pm_e3gnn.err 2>&1; echo "pair e3gnn oeq 256: pe0=$(pe0 t256_pm_e3gnn.log) $(rate t256_pm_e3gnn.log) s/step"
echo "done $(date)"
