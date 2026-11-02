#!/bin/bash
# Detached (nohup) continuation of the "smoke first" pattern, safe against the Claude session ending:
#   smoke_chain_release.sh <smoke WorkChain pk> "<space-separated CalcJob pks of the smoke>" [production --mlip name]
# Waits until none of the smoke's Slurm jobs (aiida-<pk>) is queued or running, releases the jobs listed in
# held_aiida_jobs.txt (hold-ed so the smoke could go first), and, if the smoke WorkChain finished with exit 0 and a
# production --mlip name is given, fetches the smoke results and submits the production WorkChain.
# Log: smoke_chain_release.<pk>.log next to this script.
R=/home/kino/kino/Claude/Projects/PhaseDiagram; S=$R/env/lammps-gpu-mliap/test
PK=$1; PKS=$2; PROD=${3:-}
export PATH=$R/env/ftphase/bin:$PATH
LOG=$S/smoke_chain_release.$PK.log
PAT=$(echo $PKS | sed 's/ /|/g; s/|$//')
echo "$(date) waiting for smoke $PK jobs ($PAT)" >> $LOG
until [ "$(squeue -h -o %j | grep -cE "^aiida-($PAT)$")" = 0 ]; do sleep 60; done
if [ -s $S/held_aiida_jobs.txt ]; then
  scontrol release $(tr '\n' ' ' < $S/held_aiida_jobs.txt) && echo "$(date) released $(wc -l < $S/held_aiida_jobs.txt) held jobs" >> $LOG && rm -f $S/held_aiida_jobs.txt
fi
sleep 180
st=$(verdi -p ftphase process status $PK 2>/dev/null | head -1); echo "$(date) $st" >> $LOG
if echo "$st" | grep -q "Finished \[0\]"; then
  $R/env/ftphase/bin/python $R/ftphase/examples/aiida_txdiagram/fetch_results.py $PK >> $LOG 2>&1
  if [ -n "$PROD" ]; then
    echo "$(date) smoke passed -> submitting production --mlip $PROD" >> $LOG
    $R/env/ftphase/bin/python $R/ftphase/examples/aiida_txdiagram/run_aiida.py --mlip $PROD >> $LOG 2>&1
  fi
else
  echo "$(date) smoke $PK did not finish cleanly; production not submitted" >> $LOG
fi
