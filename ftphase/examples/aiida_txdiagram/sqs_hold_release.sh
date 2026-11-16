#!/bin/bash
# Detached helper (2026-11-16): the GPUs are FIFO and filled with the Ni-Al SevenNet-MF-ompa stage-2 TI jobs (aiida-17567..17684, days).
# Hold the PENDING ones on mygarden5/6 so that the QHA jobs of the common-SQS Al-Li WorkChains (out/fccsqsi_pks.txt) run as soon as the
# running TI job ends; release the held jobs when all those WorkChains have terminated.  Log: out/sqs_hold_release.log
R=/home/kino/kino/Claude/Projects/PhaseDiagram; H=$R/ftphase/examples/aiida_txdiagram; export PATH=$R/env/ftphase/bin:$PATH; LOG=$H/out/sqs_hold_release.log
PKS=$(sed 's/PKS=//' $H/out/fccsqsi_pks.txt)
for host in mygarden5 mygarden6; do
  if [ $host = mygarden5 ]; then run() { bash -c "$1"; }; else run() { ssh mygarden6 "$1"; }; fi
  ids=$(run "squeue -h -t PENDING -o '%i %j'" | awk '{split($2,a,"-"); if (a[1]=="aiida" && a[2]>=17567 && a[2]<=17684) print $1}' | tr '\n' ' ')
  [ -n "$ids" ] && run "scontrol hold $ids" && echo "$(date) $host held: $ids" >> $LOG; echo "$host $ids" >> $H/out/sqs_held_ids.txt
done
while :; do
  st=$(python - <<PY 2>/dev/null | tail -1
from aiida import load_profile, orm
load_profile("ftphase"); ns=[orm.load_node(int(p)) for p in "$PKS".split()]
print("ALLDONE" if all(n.is_terminated for n in ns) else "running", sum(n.is_terminated for n in ns), len(ns))
PY
)
  case "$st" in ALLDONE*) break;; esac; sleep 300
done
echo "$(date) $st -> releasing" >> $LOG
while read host ids; do [ -z "$ids" ] && continue; if [ $host = mygarden5 ]; then scontrol release $ids; else ssh mygarden6 "scontrol release $ids"; fi; echo "$(date) $host released: $ids" >> $LOG; done < $H/out/sqs_held_ids.txt
