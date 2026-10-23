#!/bin/bash
# One-time AiiDA setup for the ftphase workflow on this host (mygarden5):
#   profile  ftphase   (SQLite storage, RabbitMQ broker if running, created with verdi presto;
#                       the default profile is restored to what it was before)
#   computer mygarden5 (core.local + core.slurm, work dir ~/aiida_run/ftphase)
#   codes    ftphase-qha@mygarden5 (ftphase-qha-run), calphy@mygarden5 (calphy_kernel)
#   daemon   2 workers of profile ftphase
# Idempotent: existing profile/computer/codes are kept.  Env: PhaseDiagram/env/ftphase (has aiida-core).
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
ENV="$ROOT/env/ftphase"
export PATH="$ENV/bin:$PATH"
VERDI="$ENV/bin/verdi"
PROFILE=${AIIDA_FTPHASE_PROFILE:-ftphase}
COMPUTER=${AIIDA_FTPHASE_COMPUTER:-mygarden5}
WORKDIR=${AIIDA_FTPHASE_WORKDIR:-$HOME/aiida_run/ftphase}
CONDA_SH_PATH=""
for c in "$CONDA_SH" /home/kino/miniforge3/etc/profile.d/conda.sh /home/kino/miniconda3/etc/profile.d/conda.sh; do
  [ -n "$c" ] && [ -f "$c" ] && { CONDA_SH_PATH="$c"; break; }
done
ACTIVATE="source $CONDA_SH_PATH && conda activate $ENV"

DEFAULT_BEFORE=$($VERDI profile list 2>/dev/null | sed -n 's/^\* *//p' | head -1)
if ! $VERDI profile show "$PROFILE" >/dev/null 2>&1; then
  echo "== creating profile $PROFILE"
  $VERDI presto --profile-name "$PROFILE" --email "${AIIDA_EMAIL:-kino@localhost}"
  if [ -n "$DEFAULT_BEFORE" ] && [ "$DEFAULT_BEFORE" != "$PROFILE" ]; then
    $VERDI profile set-default "$DEFAULT_BEFORE"
    echo "   default profile restored to $DEFAULT_BEFORE"
  fi
else
  echo "== profile $PROFILE exists"
fi
V="$VERDI -p $PROFILE"
$V status || true

if ! $V computer show "$COMPUTER" >/dev/null 2>&1; then
  echo "== creating computer $COMPUTER"
  mkdir -p "$WORKDIR"
  $V computer setup -n --label "$COMPUTER" --hostname localhost --description "this host via Slurm (ftphase)" \
    --transport core.local --scheduler core.slurm --work-dir "$WORKDIR" \
    --mpirun-command "mpirun -np {tot_num_mpiprocs}" --mpiprocs-per-machine 16 --default-memory-per-machine 60000000 \
    --prepend-text "unset PYTHONPATH PYTHONHOME  # the daemon exports its sys.path as PYTHONPATH; it breaks the base conda python" --append-text ""
  $V computer configure core.local "$COMPUTER" -n --safe-interval 5
  $V computer test "$COMPUTER" || true
else
  echo "== computer $COMPUTER exists"
fi

create_code () {  # label executable plugin prepend
  if $V code show "$1@$COMPUTER" >/dev/null 2>&1; then echo "== code $1@$COMPUTER exists"; return; fi
  echo "== creating code $1@$COMPUTER"
  $V code create core.code.installed -n --label "$1" --computer "$COMPUTER" --filepath-executable "$2" \
    --default-calc-job-plugin "$3" --prepend-text "$4" --append-text "" --description "$5"
}
create_code ftphase-qha "$ENV/bin/ftphase-qha-run" ftphase.qha "$ACTIVATE
export OMP_NUM_THREADS=\${SLURM_CPUS_PER_TASK:-4}" "stage 03A: relax + phonopy volume scan + QHA of one cell (ftphase.qha.phonopy_volume_scan)"
create_code calphy "$ENV/bin/calphy_kernel" ftphase.calphy "$ACTIVATE
export OMP_NUM_THREADS=1" "stage 03B: calphy 2.3.0 kernel (reversible scaling / Frenkel-Ladd), LAMMPS CPU or KOKKOS GPU (env/lammps-gpu)"

echo "== daemon"
$V daemon status >/dev/null 2>&1 || $V daemon start "${AIIDA_FTPHASE_WORKERS:-2}"
$V daemon status
$V code list
