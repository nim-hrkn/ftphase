#!/bin/bash
# Stage 5 of example 7 (mygardenx1): redo the calphy solid TI with >= 2000-atom cells (MIN_TI_ATOMS) and higher sweep
# caps (T_TI: fccAl 1250, fccNi 1950, B2 2000, L1_2 1900 K), then re-assemble.  Removes two artefacts of stage 3/4:
# the 256-atom Frenkel-Ladd finite-size error (+50-70 K on melting points) and phases vanishing at the sweep cap.
# Old solid TI runs are kept in calphy_solid_stage3/.  Everything is Slurm; nothing depends on this shell.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "stage5 $(date '+%F %T') on $(hostname)" | tee -a out/jobs.txt
if [ -d calphy_solid ] && [ ! -d calphy_solid_stage3 ]; then mv calphy_solid calphy_solid_stage3; fi
cp out/02A_solids_ti.json out/02A_solids_ti_stage3.json 2>/dev/null || true
cp out/REPORT.md out/REPORT_stage4_pre5.md 2>/dev/null || true
$PY pipeline.py prepare_solids_ti 2>&1 | grep -v Warning | tee -a out/prepare.log
before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_solid && calphy -i input_solid.yaml ) 2>&1 | grep -v Warning | tee -a out/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
SOL=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_solid(2000 atoms) $SOL" | tee -a out/jobs.txt
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=8GB -J nial_assemble5 --chdir="$HERE" --dependency="afterany:$SOL" -o out/assemble5.slurm.out -e out/assemble5.slurm.err \
  --wrap "$PY pipeline.py assemble && $PY reassemble_ws.py")
echo "nial_assemble5 $JOB_ASM (afterany:$SOL)" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.28j %.9T %.8M %.5C" | head -12 | tee -a out/jobs.txt
