#!/bin/bash
# Copy the ftphase package, example scripts and the small input data to a compute host
# (default mygardenx1) under the same project path.  Large outputs (out_*, calphy job
# folders, conda envs, LAMMPS builds) are excluded.  Usage: ftphase/tools/sync_to_host.sh [host]
set -eo pipefail
HOST=${1:-mygardenx1}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
DEST=/home/kino/kino/Claude/Projects/PhaseDiagram
rsync -az \
  --exclude 'out/' --exclude 'out_*/' --exclude 'calphy_*/' --exclude '__pycache__/' --exclude '*.egg-info/' --exclude '.pytest_cache/' \
  "$ROOT/ftphase/" "$HOST:$DEST/ftphase/"
rsync -az --mkpath "$ROOT/pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/" "$HOST:$DEST/pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/"
rsync -az --mkpath "$ROOT/potentials/" "$HOST:$DEST/potentials/"   # NIST EAM files (nial, agcu)
rsync -az "$ROOT/CLAUDE.md" "$HOST:$DEST/CLAUDE.md"
echo "synced to $HOST:$DEST"
