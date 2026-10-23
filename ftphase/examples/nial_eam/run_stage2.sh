#!/bin/bash
# Stage 2 of example 7 (after run_pipeline.sh): calphy TI for all solid cells, QHA solids recomputed with the
# converged phonon mesh, frozen liquid repeats resumed with a higher sweep end, then re-assembly.
# Everything is Slurm; nothing depends on this shell afterwards.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "stage2 $(date '+%F %T') on $(hostname)" | tee -a out/jobs.txt
DEP="afterany"
# (a) QHA solids again with the converged mesh (old results kept in out/qha_mesh4/)
if [ ! -d out/qha_mesh4 ]; then mkdir -p out/qha_mesh4 && mv out/03A_* out/qha_mesh4/ 2>/dev/null || true; fi
JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 8 --mem=16GB -J nial_solids --chdir="$HERE" -o out/solids2.slurm.out -e out/solids2.slurm.err --wrap "export OMP_NUM_THREADS=8; $PY pipeline.py solids")
echo "nial_solids(mesh) $JOB_SOL" | tee -a out/jobs.txt; DEP="$DEP:$JOB_SOL"
# (b) calphy TI for the solids
[ -f out/02A_solids_ti.json ] || $PY pipeline.py prepare_solids_ti 2>&1 | grep -v Warning | tee -a out/prepare.log
before=$(squeue -h -u "$USER" -o %i | sort)
( cd calphy_solid && calphy -i input_solid.yaml ) 2>&1 | grep -v Warning | tee -a out/calphy_submit.log
sleep 5
after=$(squeue -h -u "$USER" -o %i | sort)
SOL=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
echo "calphy_solid $SOL" | tee -a out/jobs.txt; [ -n "$SOL" ] && DEP="$DEP:$SOL"
# (c) frozen liquid repeats: higher sweep end
[ -f calphy_liquid/t_override.json ] || echo '{"lqd_x0.70_r1": 1450.0, "lqd_x0.80_r1": 1500.0}' > calphy_liquid/t_override.json
TODO=$($PY pipeline.py resume 2>&1 | grep -v Warning | tee -a out/resume.log | sed -n 's/^RESUME_TODO //p')
if [ -n "$TODO" ]; then
  before=$(squeue -h -u "$USER" -o %i | sort)
  ( cd calphy_liquid && calphy -i input_liquid_resume.yaml ) 2>&1 | grep -v Warning | tee -a out/calphy_submit.log
  sleep 5
  after=$(squeue -h -u "$USER" -o %i | sort)
  LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
  echo "calphy_liquid resume ($TODO) $LIQ" | tee -a out/jobs.txt; [ -n "$LIQ" ] && DEP="$DEP:$LIQ"
fi
# (d) assemble
cp out/REPORT.md out/REPORT_stage1_qha.md 2>/dev/null || true
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=8GB -J nial_assemble --chdir="$HERE" --dependency="$DEP" -o out/assemble.slurm.out -e out/assemble.slurm.err --wrap "$PY pipeline.py assemble")
echo "nial_assemble $JOB_ASM (dependency $DEP)" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.26j %.9T %.8M %.5C %R" | head -8 | tee -a out/jobs.txt
