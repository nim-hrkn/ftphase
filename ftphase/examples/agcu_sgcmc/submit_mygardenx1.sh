#!/bin/bash
# Run the Ag-Cu SGC MC sweeps (sgcmc.py prepare) on mygardenx1 as Slurm jobs, 8 MPI ranks each, all in parallel.
#   ./submit_mygardenx1.sh            sync the project code to mygardenx1, prepare the inputs there, sbatch one job per run
#   ./submit_mygardenx1.sh --fetch    copy runs/*/sweep.dat back and run the analysis locally
# Nothing depends on the launching shell: Slurm on mygardenx1 runs the jobs; results are runs/<tag>/sweep.dat.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
HOST=mygardenx1
REL=ftphase/examples/agcu_sgcmc
RANKS=${SGC_RANKS:-8}
if [ "$1" = "--fetch" ]; then
  mkdir -p "$HERE/runs"
  rsync -av --include='*/' --include='sweep.dat' --include='log.lammps' --include='*.slurm.*' --exclude='*' "$HOST:$ROOT/$REL/runs/" "$HERE/runs/"
  "$ROOT/env/ftphase/bin/python" "$HERE/sgcmc.py" analyse
  exit 0
fi
"$ROOT/ftphase/tools/sync_to_host.sh" "$HOST"
ssh "$HOST" "source /home/kino/miniconda3/etc/profile.d/conda.sh && conda activate $ROOT/env/ftphase && cd $ROOT/$REL && python sgcmc.py prepare && \
  for d in runs/T*_*; do tag=\$(basename \$d); \
    sbatch --parsable -p debug -n $RANKS --hint=nomultithread --mem=8GB -J sgc_\$tag --chdir=\$PWD/\$d -o slurm.out -e slurm.err \
      --wrap 'mpirun -np $RANKS lmp_mpi -in in.sgc -log log.lammps -screen none' | sed \"s/^/\$tag /\"; done | tee runs/jobs.txt; squeue -u \$USER"
