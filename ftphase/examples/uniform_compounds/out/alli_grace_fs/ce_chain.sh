#!/bin/bash
# GRACE-FS Al-Li defect Monte Carlo for one compound: waits for the running cells job, then check -> fit -> (harvest -> cells -> check -> fit) x3 -> mc
cd "$(dirname "$0")/../.."; export OMP_NUM_THREADS=${NT:-4}; P=../../../env/ftphase/bin/python; O=out/alli_grace_fs; c=$1
while pgrep -f "defect_ce_m[c].py alli_grace_fs $c cells" >/dev/null; do sleep 60; done
{ $P defect_ce_mc.py alli_grace_fs $c check; $P defect_ce_mc.py alli_grace_fs $c fit || exit 1
for it in 1 2 3; do $P defect_ce_mc.py alli_grace_fs $c harvest; $P defect_ce_mc.py alli_grace_fs $c cells; $P defect_ce_mc.py alli_grace_fs $c check; $P defect_ce_mc.py alli_grace_fs $c fit; done
$P defect_ce_mc.py alli_grace_fs $c mc; echo CHAIN_DONE; } > $O/ce_${c}_chain.log 2>&1
