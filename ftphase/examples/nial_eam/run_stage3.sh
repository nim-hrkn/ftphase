#!/bin/bash
# Stage 3 of example 7: wider B2 / L1_2 defect sampling (QHA + calphy TI for the new cells) and re-assembly.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "stage3 $(date '+%F %T') on $(hostname)" | tee -a out/jobs.txt
[ -f calphy_solid/input_solid_more.yaml ] || $PY pipeline.py prepare_more_defects 2>&1 | grep -v Warning | tee -a out/prepare.log
JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 8 --mem=16GB -J nial_solids --chdir="$HERE" -o out/solids3.slurm.out -e out/solids3.slurm.err --wrap "export OMP_NUM_THREADS=8; $PY pipeline.py solids")
echo "nial_solids(more defects) $JOB_SOL" | tee -a out/jobs.txt
before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_solid && calphy -i input_solid_more.yaml ) 2>&1 | grep -v Warning | tee -a out/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
SOL=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_solid more $SOL" | tee -a out/jobs.txt
cp out/REPORT.md out/REPORT_stage2.md 2>/dev/null || true; cp out/07_phase_diagram.png out/07_phase_diagram_stage2.png 2>/dev/null || true
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=8GB -J nial_assemble --chdir="$HERE" --dependency=afterany:$JOB_SOL${SOL:+:$SOL} -o out/assemble.slurm.out -e out/assemble.slurm.err --wrap "$PY pipeline.py assemble")
echo "nial_assemble $JOB_ASM" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.26j %.9T %.8M %.5C %R" | head -6 | tee -a out/jobs.txt
