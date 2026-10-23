#!/bin/bash
# Launch example 7 (Ni-Al, Mishin 2009 EAM) as Slurm jobs on the current host (meant for mygardenx1, CPU).
# After this returns nothing depends on the shell:
#   nial_solids  CPU job (8 cores)       03A QHA of all solid cells
#   lqd_x*       CPU jobs (16 ranks)     03B calphy liquid reversible scaling (+ repeats), submitted by calphy
#   nial_assemble CPU job                04-07, --dependency=afterany on all of the above -> out/REPORT.md
# Resume after a crash with ./run_resume.sh.  NIAL_CORES (default 16) sets the ranks per calphy job.
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
echo "launch $(date '+%F %T') on $(hostname)" | tee -a out/jobs.txt
if [ -f out/prepare.json ]; then echo "prepare already done (out/prepare.json); skipping"; else
  $PY pipeline.py prepare 2>&1 | grep -v Warning | tee out/prepare.log
fi
JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 8 --mem=16GB -J nial_solids --chdir="$HERE" \
  -o out/solids.slurm.out -e out/solids.slurm.err --wrap "export OMP_NUM_THREADS=8; $PY pipeline.py solids")
echo "nial_solids $JOB_SOL" | tee -a out/jobs.txt
before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_liquid && calphy -i input_liquid.yaml ) 2>&1 | grep -v Warning | tee out/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_liquid $LIQ" | tee -a out/jobs.txt
DEP="afterany:$JOB_SOL"
[ -n "$LIQ" ] && DEP="$DEP:$LIQ"
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=8GB -J nial_assemble --chdir="$HERE" --dependency="$DEP" \
  -o out/assemble.slurm.out -e out/assemble.slurm.err --wrap "$PY pipeline.py assemble")
echo "nial_assemble $JOB_ASM (dependency $DEP)" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.26j %.9T %.8M %.5C %R" | head -12 | tee -a out/jobs.txt
