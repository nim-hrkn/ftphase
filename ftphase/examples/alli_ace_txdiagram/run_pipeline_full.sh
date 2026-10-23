#!/bin/bash
# Launch example 6 (full-range ACE Al-Li T-x diagram, 64-atom SQS solids) as Slurm jobs.
# Nothing depends on the launching shell afterwards:
#   txf_solids    CPU job (4 cores)   03A QHA of 15 solid cells (about 20 min)
#   lqd_x0.6..1.0 GPU jobs (1 each)   03B calphy liquid reversible scaling, submitted by calphy
#   txf_assemble  CPU job             04-07, --dependency=afterany on all of the above -> out_full/REPORT.md
# Al-side liquids (x <= 0.5) are reused from calphy_liquid/ (example 5).
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
mkdir -p out_full
echo "launch $(date '+%F %T')" | tee -a out_full/jobs.txt

if [ -f out_full/prepare.json ]; then echo "prepare already done (out_full/prepare.json); skipping"; else
  $PY pipeline_full.py prepare 2>&1 | grep -v Warning | tee out_full/prepare.log
fi

JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 4 --hint=nomultithread --mem=12GB -J txf_solids --chdir="$HERE" \
  -o out_full/solids.slurm.out -e out_full/solids.slurm.err \
  --wrap "export OMP_NUM_THREADS=4; $PY pipeline_full.py solids")
echo "txf_solids $JOB_SOL" | tee -a out_full/jobs.txt

before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_liquid_li && calphy -i input_liquid_li_gpu.yaml ) 2>&1 | grep -v Warning | tee out_full/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_liquid_li $LIQ" | tee -a out_full/jobs.txt

DEP="afterany:$JOB_SOL"
[ -n "$LIQ" ] && DEP="$DEP:$LIQ"
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=4GB -J txf_assemble --chdir="$HERE" --dependency="$DEP" \
  -o out_full/assemble.slurm.out -e out_full/assemble.slurm.err \
  --wrap "$PY pipeline_full.py assemble")
echo "txf_assemble $JOB_ASM (dependency $DEP)" | tee -a out_full/jobs.txt
squeue -u "$USER" -o "%.7i %.22j %.9T %.8M %.12b %R" | tee -a out_full/jobs.txt
