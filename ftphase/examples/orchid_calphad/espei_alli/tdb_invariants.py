"""Invariant reactions and a few landmarks of a binary TDB with pycalphad's mapping (same engine as ORCHID-Diagrams).

    python tdb_invariants.py alli-mcmc.tdb [--T 300 1100] [--x LI] [--solvus-T 700]

Prints the three-phase nodes (T, phases, compositions), the melting points of the pure elements, the congruent
maximum of each compound/ordered phase and the terminal solubility at --solvus-T, as a JSON block."""

import argparse
import json

import numpy as np
from pycalphad import Database, equilibrium, variables as v
from pycalphad.mapping import BinaryStrategy


def phase_sets_along_x(dbf, comps, phases, T, xcomp, nx=201):
    eq = equilibrium(dbf, comps, phases, {v.N: 1, v.P: 101325, v.T: T, v.X(xcomp): (0, 1, 1.0 / (nx - 1))})
    out = []
    for i in range(eq.X_LI.shape[-2] if False else len(eq.coords["X_" + xcomp])):
        ph = sorted(set(p for p in eq.Phase.values[0, 0, 0, i] if p))
        out.append(ph)
    return eq.coords["X_" + xcomp].values, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tdb")
    ap.add_argument("--T", nargs=2, type=float, default=[300, 1100])
    ap.add_argument("--x", default="LI")
    ap.add_argument("--solvus-T", type=float, default=700.0)
    args = ap.parse_args()
    dbf = Database(args.tdb)
    els = sorted(e for e in dbf.elements if e not in ("VA", "/-"))
    comps = els + ["VA"]
    phases = sorted(dbf.phases)
    conds = {v.N: 1, v.P: 101325, v.T: (args.T[0], args.T[1], 10), v.X(args.x): (0, 1, 0.01)}
    strat = BinaryStrategy(dbf, comps, phases, conds)
    strat.do_map()
    invariants = []
    for region in strat.get_invariant_data(v.X(args.x), v.T):
        pts = []
        T = None
        for sp in region.data:
            ph = getattr(sp, "phase", None) or getattr(sp, "phase_name", None)
            xv = float(np.ravel(getattr(sp, "x"))[0])
            T = float(np.ravel(getattr(sp, "y"))[0])
            pts.append((ph, xv))
        pts.sort(key=lambda t: t[1])
        invariants.append({"T": round(T, 1), "points": [{"phase": p, "x": round(x, 4)} for p, x in pts]})
    invariants.sort(key=lambda d: -d["T"])
    # grid scan (ORCHID style): phase-set sequence along x at every T; a change of the set of two-phase pairs between
    # neighbouring T rows brackets an invariant (same definition as the project's 07_invariants.tsv)
    dT, dx = 5.0, 0.005
    eq = equilibrium(dbf, comps, phases, {v.N: 1, v.P: 101325, v.T: (args.T[0], args.T[1] + 0.1, dT), v.X(args.x): (0, 1, dx)})
    Tg = eq.coords["T"].values
    rows = []
    for it in range(len(Tg)):
        pairs = set()
        for ix in range(eq.Phase.values.shape[3]):
            ph = tuple(sorted(set(p for p in eq.Phase.values[0, 0, it, ix] if p)))
            if len(ph) == 2:
                pairs.add(ph)
        rows.append(pairs)
    grid_changes = []
    for it in range(len(Tg) - 1):
        gone = rows[it] - rows[it + 1]
        new = rows[it + 1] - rows[it]
        if gone or new:
            grid_changes.append({"T_low": float(Tg[it]), "T_high": float(Tg[it + 1]),
                                 "pairs_vanish_on_heating": ["+".join(p) for p in sorted(gone)],
                                 "pairs_appear_on_heating": ["+".join(p) for p in sorted(new)]})
    res = {"tdb": args.tdb, "invariants_mapping": invariants, "grid_pair_changes": grid_changes}
    Ts = np.arange(args.T[0], args.T[1] + 0.1, 2.0)
    # pure-element melting: first T where LIQUID is stable at x=0 / x=1
    for xval, label in [(0.0, els[0] if args.x != els[0] else els[1]), (1.0, args.x)]:
        eq = equilibrium(dbf, comps, phases, {v.N: 1, v.P: 101325, v.T: (args.T[0], args.T[1], 2.0), v.X(args.x): max(min(xval, 0.999), 0.001)})
        liq = [float(t) for t, row in zip(eq.coords["T"].values, eq.Phase.values[0, 0, :, 0]) if "LIQUID" in row]
        res[f"T_melt_{label}"] = min(liq) if liq else None
    # solvus of the first terminal phase at solvus_T: largest x of the single-phase terminal region from x=0
    xs, sets = phase_sets_along_x(dbf, comps, phases, args.solvus_T, args.x)
    first = sets[0]
    xmax = 0.0
    for x, s in zip(xs, sets):
        if s == first and len(s) == 1:
            xmax = float(x)
        else:
            break
    res[f"terminal_phase_x0"] = first
    res[f"solvus_x_at_{int(args.solvus_T)}K"] = xmax
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
