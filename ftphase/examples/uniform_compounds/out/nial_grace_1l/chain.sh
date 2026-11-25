#!/bin/bash
# GRACE-1L Ni-Al defect cells, one GPU: usage chain.sh "<compounds>" [wait-pattern]
cd "$(dirname "$0")/../.."; export OMP_NUM_THREADS=2; P=../../../env/ftphase/bin/python; O=out/nial_grace_1l
if [ -n "$2" ]; then while pgrep -f "$2" >/dev/null; do sleep 60; done; fi
for c in $1; do [ "$c" = "B2first" ] && { $P run_defects.py nial_grace_1l multi B2 > $O/B2_multi.log 2>&1; continue; }; $P run_defects.py nial_grace_1l single $c > $O/${c}_single.log 2>&1; $P run_defects.py nial_grace_1l multi $c > $O/${c}_multi.log 2>&1; done; echo done > $O/chain_$(hostname).done
