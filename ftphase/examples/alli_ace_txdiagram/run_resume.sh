#!/bin/bash
# Resume example 5 after a crash/reboot: rerun only the liquid compositions without a
# finished sweep (see pipeline.py resume), then re-assemble.  Solids are reused if
# out/03A_status.json exists, otherwise the solids job is resubmitted too.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "resume $(date '+%F %T')" | tee -a out/jobs.txt
DEP="afterany"
if [ ! -f out/03A_status.json ]; then
  JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 4 --hint=nomultithread --mem=8GB -J tx_solids --chdir="$HERE" -o out/solids.slurm.out -e out/solids.slurm.err --wrap "export OMP_NUM_THREADS=4; $PY pipeline.py solids")
  echo "tx_solids $JOB_SOL" | tee -a out/jobs.txt; DEP="$DEP:$JOB_SOL"
fi
TODO=$($PY pipeline.py resume 2>&1 | grep -v Warning | tee out/resume.log | sed -n 's/^RESUME_TODO //p')
if [ -n "$TODO" ]; then
  before=$(squeue -h -u "$USER" -o %i | sort)
  ( cd calphy_liquid && calphy -i input_liquid_gpu_resume.yaml ) 2>&1 | grep -v Warning | tee -a out/calphy_submit.log
  sleep 5
  after=$(squeue -h -u "$USER" -o %i | sort)
  LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
  echo "calphy_liquid resume ($TODO) $LIQ" | tee -a out/jobs.txt
  [ -n "$LIQ" ] && DEP="$DEP:$LIQ"
fi
[ "$DEP" = "afterany" ] && DEP=""
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=4GB -J tx_assemble --chdir="$HERE" ${DEP:+--dependency=$DEP} -o out/assemble.slurm.out -e out/assemble.slurm.err --wrap "$PY pipeline.py assemble")
echo "tx_assemble $JOB_ASM (dependency ${DEP:-none})" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.22j %.9T %.8M %.12b %R" | tee -a out/jobs.txt
