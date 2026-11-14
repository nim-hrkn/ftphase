#!/bin/bash
# Detached (nohup) fallback for the SevenNet-MF-ompa Ni-Al stage-1 B2 solid TI (pk 16318, 3456 atoms): the 2048-atom fcc-Al job
# already uses 10.3 GB of the 12 GB GPU, so the B2 cell is expected to run out of memory.  User decision 2026-11-14: let it try,
# and if it dies with an out-of-memory error resubmit it as 3x3x3 of the 54-atom cell (1458 atoms, --min-atoms 1400).
# Log: out/nial_sevenn_mf_ompa/b2_oom_fallback.log
R=/home/kino/kino/Claude/Projects/PhaseDiagram; H=$R/ftphase/examples/aiida_txdiagram; PK=${1:-16318}
export PATH=$R/env/ftphase/bin:$PATH
LOG=$H/out/nial_sevenn_mf_ompa/b2_oom_fallback.log
echo "$(date) watching pk $PK" >> $LOG
while :; do
  st=$(python - <<PY 2>/dev/null | tail -1
from aiida import load_profile, orm
load_profile("ftphase"); n = orm.load_node($PK)
print(("done %s" % n.exit_status) if n.is_terminated else "running")
PY
)
  case "$st" in done*) break;; esac
  sleep 300
done
echo "$(date) pk $PK terminated: $st" >> $LOG
if [ "$st" = "done 0" ]; then echo "$(date) finished ok with 3456 atoms, nothing to do" >> $LOG; exit 0; fi
W=$(python -c "
from aiida import load_profile, orm
load_profile('ftphase'); print(orm.load_node($PK).get_remote_workdir())" 2>/dev/null | tail -1)
if grep -rqi "out of memory\|CUDA error: out of memory\|OutOfMemory\|bad_alloc" $W 2>/dev/null; then
  echo "$(date) out of memory in $W -> resubmitting s08_B2 with 1458 atoms" >> $LOG
  python -c "
from aiida import load_profile, orm
load_profile('ftphase'); orm.load_node($PK).base.caching.is_valid_cache = False" >> $LOG 2>&1
  cd $H && python mlip_solids_ti.py submit --names nial_sevenn_mf_ompa --only s08_B2 --min-atoms 1400 2>&1 | grep -v WARNING >> $LOG
else
  echo "$(date) failed for another reason (no out-of-memory message in $W); not resubmitted: $(tail -n 3 $W/calphy.err 2>/dev/null | tr '\n' ' ' | cut -c1-300)" >> $LOG
fi
