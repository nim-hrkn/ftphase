"""Reproduce Zhang et al. 2027 Fig. 3b / Table 1 (phase-label classification accuracy) from the TDBs of the Zenodo deposit
10.5281/zenodo.20918696, with the grids of the deposit's notebook 06-compare_phasediagram.ipynb.
    python classify.py <deposit dir> [--methods ...] [--out out/classification.tsv]
At each (x, T) grid point the set of equilibrium phases (duplicates numbered, as in the notebook) is compared with the
Modified_CPDDB reference; accuracy = fraction of equal sets.  Extra TDBs (e.g. our own MLIPs) can be given as name=path.
"""
import argparse, json, os, sys, time
from collections import Counter
import numpy as np
from pycalphad import Database, equilibrium, variables as v

GRIDS = {  # notebook 06: (x element, dx, T_lo, T_hi, dT)
    "Ru-Si": ("SI", 0.02, 500, 2500, 40), "Mo-Rh": ("RH", 0.02, 1000, 2600, 30), "Al-Zn": ("ZN", 0.02, 50, 900, 20),
    "Cu-Mg": ("MG", 0.02, 400, 1200, 20), "Cu-Pt": ("PT", 0.02, 500, 1200, 20), "W-Re": ("W", 0.01, 100, 3500, 35)}
METHODS = ["DFT", "grace-2L-SMAX", "grace-2L-OAM-L", "SevenNet-omni", "Nequip-OAM-XL", "eSEN-uma-s-1p1", "grace-2L-MP", "ORB-v3", "Nequip-MP-L"]


def phase_sets(tdb, system):
    xel, dx, tlo, thi, dt = GRIDS[system]
    db = Database(tdb); els = [e for e in db.elements if e != "/-"]
    cond = {v.X(xel): (0, 1, dx), v.T: (tlo, thi, dt), v.P: 101325, v.N: 1}
    eq = equilibrium(db, els, list(db.phases.keys()), cond)
    out = []
    for row in eq.Phase.values.reshape((-1, eq.Phase.values.shape[-1])):
        c = Counter(p for p in row if p); s = set()
        for p, n in c.items():
            s.add(p.upper()); s.update(f"{p}_{i + 1}".upper() for i in range(n - 1))
        out.append(frozenset(s))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("deposit"); ap.add_argument("--methods", nargs="*", default=METHODS)
    ap.add_argument("--systems", nargs="*", default=list(GRIDS)); ap.add_argument("--extra", nargs="*", default=[], help="name=dir with <system>.tdb files")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "classification.tsv"))
    ap.add_argument("--dense", action="store_true", help="paper grid: 100 composition x 100 temperature points instead of the notebook grids"); a = ap.parse_args()
    if a.dense:
        for k, (xel, dx, tlo, thi, dt) in GRIDS.items():
            GRIDS[k] = (xel, 1 / 99.0 - 1e-9, tlo, thi, (thi - tlo) / 99.0)
    extra = dict(e.split("=", 1) for e in a.extra)
    rows = []
    for system in a.systems:
        t0 = time.time(); ref = phase_sets(os.path.join(a.deposit, "Modified_CPDDB", f"{system}.tdb"), system)
        for m in list(a.methods) + list(extra):
            tdb = os.path.join(extra[m] if m in extra else os.path.join(a.deposit, m), f"{system}.tdb")
            if not os.path.exists(tdb):
                continue
            try:
                ps = phase_sets(tdb, system); acc = float(np.mean([p == q for p, q in zip(ref, ps)]))
            except Exception as e:
                acc = float("nan"); print(system, m, "failed:", str(e)[:120], flush=True)
            rows.append((system, m, acc, len(ref))); print(f"{system:6s} {m:16s} {acc:.3f}  ({time.time() - t0:.0f} s)", flush=True)
    with open(a.out, "w") as f:
        f.write("system\tmethod\taccuracy\tn_grid\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    # unweighted mean over systems per method (Table 1)
    ms = sorted(set(r[1] for r in rows), key=lambda m: (list(a.methods) + list(extra)).index(m))
    print("\nmean over systems:")
    for m in ms:
        vals = [r[2] for r in rows if r[1] == m]; print(f"{m:16s} {np.nanmean(vals):.3f}  (n={len(vals)})")


if __name__ == "__main__":
    main()
