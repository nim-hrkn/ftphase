#!/bin/bash
# Submit the extra liquid runs of example 6 (below 700 K and independent repeats) as GPU Slurm jobs
# and a dependent re-assembly.  Independent of the launching session.  Resume with run_resume_full.sh.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "launch more $(date '+%F %T')" | tee -a out_full/jobs.txt
if [ -f out_full/02B_liquids_more.json ]; then echo "prepare_more already done; skipping"; else
  $PY pipeline_full.py prepare_more 2>&1 | grep -v Warning | tee out_full/prepare_more.log
fi
before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_liquid_more && calphy -i input_liquid_more_gpu.yaml ) 2>&1 | grep -v Warning | tee -a out_full/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_liquid_more $LIQ" | tee -a out_full/jobs.txt
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=4GB -J txf_assemble --chdir="$HERE" ${LIQ:+--dependency=afterany:$LIQ} \
  -o out_full/assemble.slurm.out -e out_full/assemble.slurm.err --wrap "$PY pipeline_full.py assemble")
echo "txf_assemble $JOB_ASM (dependency afterany:$LIQ)" | tee -a out_full/jobs.txt
squeue -u "$USER" -o "%.7i %.26j %.9T %.8M %.12b %R" | head -8 | tee -a out_full/jobs.txt
