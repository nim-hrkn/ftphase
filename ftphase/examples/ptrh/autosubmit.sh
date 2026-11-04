#!/bin/bash
# Submit the Pt-Rh production WorkChains on mygarden6 as soon as the corresponding smoke run finishes with exit 0.
# Detached from the Claude session:  setsid nohup bash autosubmit.sh > out/autosubmit.log 2>&1 &
# Smoke pks (2026-11-04): grace-2l 8702, nequip-oam-m 8750, mace-mpa-0 8764.
set -u
ROOT=/home/kino/kino/Claude/Projects/PhaseDiagram
VERDI=$ROOT/env/ftphase/bin/verdi
PY=$ROOT/env/ftphase/bin/python
RUN=$ROOT/ftphase/examples/aiida_txdiagram/run_aiida.py
declare -A SMOKE=([grace-2l]=8702 [nequip-oam-m]=8750 [mace-mpa-0]=8764)
declare -A EXTRA=([grace-2l]="" [nequip-oam-m]="" [mace-mpa-0]="--qha-computer mygardenx2")
declare -A DONE
bash $ROOT/ftphase/tools/sync_to_host.sh mygardenx2 >/dev/null 2>&1 && echo "$(date) synced mygardenx2"
while true; do
  left=0
  for m in "${!SMOKE[@]}"; do
    [ -n "${DONE[$m]:-}" ] && continue
    head=$($VERDI -p ftphase process status ${SMOKE[$m]} 2>/dev/null | head -1)
    case "$head" in
      *"Finished [0]"*)
        echo "$(date) smoke $m (${SMOKE[$m]}) passed -> submitting production"
        $PY $RUN --system ptrh --mlip $m --computer mygarden6 ${EXTRA[$m]} 2>&1 | tail -1
        DONE[$m]=1 ;;
      *Finished*|*Excepted*|*Killed*|*Failed*)
        echo "$(date) smoke $m (${SMOKE[$m]}) ended without success: $head -> not submitted"
        DONE[$m]=1 ;;
      *) left=$((left+1)) ;;
    esac
  done
  [ $left -eq 0 ] && break
  sleep 120
done
echo "$(date) autosubmit finished"
