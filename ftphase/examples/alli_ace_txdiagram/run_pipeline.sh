#!/bin/bash
# Launch example 5 (ACE Al-Li T-x diagram from stage 01) entirely as Slurm jobs.
# After this script returns, nothing depends on the launching shell or session:
#   tx_solids   CPU job (4 cores)   03A QHA of all solid cells
#   lqd_x*      GPU jobs (1 each)   03B calphy liquid reversible scaling, submitted by calphy itself
#   tx_assemble CPU job             04-07, --dependency=afterany on all of the above
# Usage: ./run_pipeline.sh            (re-run: delete out/ and calphy_liquid/lqd_* first)
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
mkdir -p out
echo "launch $(date '+%F %T')" | tee -a out/jobs.txt

# 01 / 02A / 02B on the login node (about a minute, CPU)
if [ -f out/prepare.json ]; then echo "prepare already done (out/prepare.json); skipping"; else
  $PY pipeline.py prepare 2>&1 | grep -v Warning | tee out/prepare.log
fi

# 03A solids: one CPU job
JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 4 --hint=nomultithread --mem=8GB -J tx_solids --chdir="$HERE" \
  -o out/solids.slurm.out -e out/solids.slurm.err \
  --wrap "export OMP_NUM_THREADS=4; $PY pipeline.py solids")
echo "tx_solids $JOB_SOL" | tee -a out/jobs.txt

# 03B liquids: calphy submits one GPU job per composition; collect their ids
before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_liquid && calphy -i input_liquid_gpu.yaml ) 2>&1 | grep -v Warning | tee out/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_liquid $LIQ" | tee -a out/jobs.txt

# 04-07 assemble after everything (afterany: runs even if a liquid job failed, and reports what is missing)
DEP="afterany:$JOB_SOL"
[ -n "$LIQ" ] && DEP="$DEP:$LIQ"
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=4GB -J tx_assemble --chdir="$HERE" --dependency="$DEP" \
  -o out/assemble.slurm.out -e out/assemble.slurm.err \
  --wrap "$PY pipeline.py assemble")
echo "tx_assemble $JOB_ASM (dependency $DEP)" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.22j %.9T %.8M %.12b %R" | tee -a out/jobs.txt
