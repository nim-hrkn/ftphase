#!/bin/bash
# Resume example 6 after a crash/reboot: rerun unfinished Li-side liquids (pipeline_full.py resume),
# rerun the solids job only if its status file is missing (finished cells are kept), then re-assemble.
# To change the sweep end temperature of one liquid, write calphy_liquid_li/t_override.json, e.g. {"lqd_x0.60": 800.0}.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
PY="$ROOT/env/ftphase/bin/python"
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { source "$c"; break; }
done
conda activate "$ROOT/env/ftphase"
cd "$HERE"
echo "resume $(date '+%F %T')" | tee -a out_full/jobs.txt
DEP="afterany"
N_OK=$($PY -c "import json,os; p='out_full/03A_status.json'; print(sum(1 for s in json.load(open(p)) if s['ok']) if os.path.exists(p) else 0)")
N_ALL=$($PY -c "import json; print(len(json.load(open('out_full/02A_solids.json'))))")
if [ "$N_OK" -lt "$N_ALL" ]; then
  JOB_SOL=$(sbatch --parsable -p debug -n 1 -c 4 --hint=nomultithread --mem=12GB -J txf_solids --chdir="$HERE" -o out_full/solids.slurm.out -e out_full/solids.slurm.err --wrap "export OMP_NUM_THREADS=4; $PY pipeline_full.py solids")
  echo "txf_solids $JOB_SOL ($N_OK/$N_ALL cells done before)" | tee -a out_full/jobs.txt; DEP="$DEP:$JOB_SOL"
fi
TODO=$($PY pipeline_full.py resume 2>&1 | grep -v Warning | tee out_full/resume.log | sed -n 's/^RESUME_TODO //p')
if [ -n "$TODO" ]; then
  before=$(squeue -h -u "$USER" -o %i | sort)
  ( cd calphy_liquid_li && calphy -i input_liquid_li_gpu_resume.yaml ) 2>&1 | grep -v Warning | tee -a out_full/calphy_submit.log
  sleep 5
  after=$(squeue -h -u "$USER" -o %i | sort)
  LIQ=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
  echo "calphy_liquid_li resume ($TODO) $LIQ" | tee -a out_full/jobs.txt
  [ -n "$LIQ" ] && DEP="$DEP:$LIQ"
fi
if [ -f out_full/02B_liquids_more.json ]; then
  TODO2=$($PY pipeline_full.py resume_more 2>&1 | grep -v Warning | tee -a out_full/resume.log | sed -n 's/^RESUME_TODO //p')
  if [ -n "$TODO2" ]; then
    before=$(squeue -h -u "$USER" -o %i | sort)
    ( cd calphy_liquid_more && calphy -i input_liquid_more_gpu_resume.yaml ) 2>&1 | grep -v Warning | tee -a out_full/calphy_submit.log
    sleep 5
    after=$(squeue -h -u "$USER" -o %i | sort)
    LIQ2=$(comm -13 <(echo "$before") <(echo "$after") | paste -sd: -)
    echo "calphy_liquid_more resume ($TODO2) $LIQ2" | tee -a out_full/jobs.txt
    [ -n "$LIQ2" ] && DEP="$DEP:$LIQ2"
  fi
fi
[ "$DEP" = "afterany" ] && DEP=""
JOB_ASM=$(sbatch --parsable -p debug -n 1 -c 2 --mem=4GB -J txf_assemble --chdir="$HERE" ${DEP:+--dependency=$DEP} -o out_full/assemble.slurm.out -e out_full/assemble.slurm.err --wrap "$PY pipeline_full.py assemble")
echo "txf_assemble $JOB_ASM (dependency ${DEP:-none})" | tee -a out_full/jobs.txt
squeue -u "$USER" -o "%.7i %.22j %.9T %.8M %.12b %R" | tee -a out_full/jobs.txt
