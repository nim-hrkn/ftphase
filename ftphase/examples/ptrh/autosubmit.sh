#!/bin/bash
# Pt-Rh on mygarden6: for every MLIP wait for its smoke WorkChain; a smoke that fails only in the assembly because of the
# 2-liquid smoke spec (pk 8702, 8750, 8764; fixed in run_aiida.py on 2026-11-04) is resubmitted once (cached QHA/calphy
# jobs are reused); a smoke that finishes with exit 0 triggers the production WorkChain.
# Detached from the Claude session:  setsid nohup bash autosubmit.sh > out/autosubmit.log 2>&1 &
set -u
ROOT=/home/kino/kino/Claude/Projects/PhaseDiagram
VERDI=$ROOT/env/ftphase/bin/verdi
PY=$ROOT/env/ftphase/bin/python
RUN=$ROOT/ftphase/examples/aiida_txdiagram/run_aiida.py
OUT=$ROOT/ftphase/examples/aiida_txdiagram/out
declare -A SMOKE=([grace-2l]=8858 [nequip-oam-m]=8750 [mace-mpa-0]=8764)
declare -A RESUB=([grace-2l]=1 [nequip-oam-m]=0 [mace-mpa-0]=0)     # 1 = already the resubmitted smoke
declare -A EXTRA=([grace-2l]="" [nequip-oam-m]="" [mace-mpa-0]="--qha-computer mygardenx2")
declare -A DONE
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
        if [ "${RESUB[$m]}" = "0" ]; then
          echo "$(date) smoke $m (${SMOKE[$m]}) ended with: $head -> resubmitting the smoke with the fixed spec"
          line=$($PY $RUN --system ptrh --mlip $m --computer mygarden6 ${EXTRA[$m]} --smoke 2>&1 | tail -1)
          echo "$line"
          pk=$(echo "$line" | sed -n 's/.*pk=\([0-9]*\).*/\1/p')
          if [ -n "$pk" ]; then SMOKE[$m]=$pk; RESUB[$m]=1; left=$((left+1)); else echo "$(date) resubmission of $m failed"; DONE[$m]=1; fi
        else
          echo "$(date) smoke $m (${SMOKE[$m]}) ended without success: $head -> production not submitted"
          DONE[$m]=1
        fi ;;
      *) left=$((left+1)) ;;
    esac
  done
  [ $left -eq 0 ] && break
  sleep 120
done
echo "$(date) autosubmit finished"
