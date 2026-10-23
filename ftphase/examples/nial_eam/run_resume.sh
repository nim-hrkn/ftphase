#!/bin/bash
# Resume example 7 after a crash/reboot: rerun unfinished liquids (pipeline.py resume; a frozen
# composition can get a higher sweep end via calphy_liquid/t_override.json, e.g. {"lqd_x0.30": 1250.0}),
# rerun the solids job only if cells are missing, then re-assemble.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "resume $(date '+%F %T') on $(hostname)" | tee -a out/jobs.txt
DEP="afterany"
N_OK=$($PY -c "import json,os; p='out/03A_status.json'; print(sum(1 for s in json.load(open(p)) if s['ok']) if os.path.exists(p) else 0)")
N_ALL=$($PY -c "import json; print(len(json.load(open('out/02A_solids.json'))))")
if [ "$N_OK" -lt "$N_ALL" ]; then
  JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 8 --mem=16GB -J nial_solids --chdir="$HERE" -o out/solids.slurm.out -e out/solids.slurm.err --wrap "export OMP_NUM_THREADS=8; $PY pipeline.py solids")
  echo "nial_solids $JOB_SOL ($N_OK/$N_ALL cells done before)" | tee -a out/jobs.txt; DEP="$DEP:$JOB_SOL"
fi
TODO=$($PY pipeline.py resume 2>&1 | grep -v Warning | tee -a out/resume.log | sed -n 's/^RESUME_TODO //p')
if [ -n "$TODO" ]; then
  before=$(squeue -h -u "$USER" -o %i | sort)
  ( cd calphy_liquid && calphy -i input_liquid_resume.yaml ) 2>&1 | grep -v Warning | tee -a out/calphy_submit.log
  sleep 5
  after=$(squeue -h -u "$USER" -o %i | sort)
  LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
  echo "calphy_liquid resume ($TODO) $LIQ" | tee -a out/jobs.txt
  [ -n "$LIQ" ] && DEP="$DEP:$LIQ"
fi
[ "$DEP" = "afterany" ] && DEP=""
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=8GB -J nial_assemble --chdir="$HERE" ${DEP:+--dependency=$DEP} -o out/assemble.slurm.out -e out/assemble.slurm.err --wrap "$PY pipeline.py assemble")
echo "nial_assemble $JOB_ASM (dependency ${DEP:-none})" | tee -a out/jobs.txt
squeue -u "$USER" -o "%.7i %.26j %.9T %.8M %.5C %R" | head -12 | tee -a out/jobs.txt
