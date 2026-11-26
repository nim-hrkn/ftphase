#!/bin/bash
# lattice route for one GRACE-FS compound: (harvest_lattice -> cells -> check -> compare -> fit) x2 -> lattice
export CE_RANK_DEFICIT=${CE_RANK_DEFICIT:-0}; cd "$(dirname "$0")/../.."; export OMP_NUM_THREADS=${NT:-4}; P=../../../env/ftphase/bin/python; c=$1
{ for it in 1 2; do $P defect_ce_mc.py alli_grace_fs $c harvest_lattice; $P defect_ce_mc.py alli_grace_fs $c cells; $P defect_ce_mc.py alli_grace_fs $c check; $P defect_ce_mc.py alli_grace_fs $c compare; $P defect_ce_mc.py alli_grace_fs $c fit; done; $P defect_ce_mc.py alli_grace_fs $c lattice; echo CHAIN_DONE; } > out/alli_grace_fs/ce_${c}_latchain.log 2>&1
