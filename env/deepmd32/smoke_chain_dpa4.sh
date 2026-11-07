#!/bin/bash
# detached: wait for the DPA4 smoke WorkChain (pk $1) and, if it finishes with exit 0, submit the production run with --mlip $2.
R=/home/kino/kino/Claude/Projects/PhaseDiagram
V="$R/env/ftphase/bin/verdi -p ftphase"
PK=$1; MLIP=$2; LOG=$R/env/deepmd32/smoke_chain_dpa4.$PK.log
unset PYTHONPATH PYTHONHOME
while true; do
  st=$($V process status $PK 2>/dev/null | head -1)
  echo "$(date '+%F %T') $st" >> $LOG
  case "$st" in
    *"Finished [0]"*) echo "smoke passed; submitting production --mlip $MLIP" >> $LOG
      cd $R/ftphase/examples/aiida_txdiagram && $R/env/ftphase/bin/python run_aiida.py --system alli --mlip $MLIP >> $LOG 2>&1; break;;
    *Finished*|*Excepted*|*Killed*) echo "smoke did not pass: $st" >> $LOG; break;;
  esac
  sleep 120
done
