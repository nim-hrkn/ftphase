#!/bin/bash
# detached: wait for the PET-OAM-L smoke WorkChain (pk $1) and, if it finishes with exit 0, submit the production run.
R=/home/kino/kino/Claude/Projects/PhaseDiagram
V="$R/env/ftphase/bin/verdi -p ftphase"
PK=$1; LOG=$R/env/metatomic/test/smoke_chain_pet.$PK.log
unset PYTHONPATH PYTHONHOME
while true; do
  st=$($V process status $PK 2>/dev/null | head -1)
  echo "$(date '+%F %T') $st" >> $LOG
  case "$st" in
    *"Finished [0]"*) echo "smoke passed; submitting production" >> $LOG
      cd $R/ftphase/examples/aiida_txdiagram && $R/env/ftphase/bin/python run_aiida.py --system alli --mlip pet-oam-l >> $LOG 2>&1; break;;
    *Finished*|*Excepted*|*Killed*) echo "smoke did not pass: $st" >> $LOG; break;;
  esac
  sleep 120
done
