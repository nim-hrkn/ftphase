"""Command line: ``ftphase check``, ``ftphase diagram``, ``ftphase hull0k``."""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd


def _cmd_check(a):
    from .records import FreeEnergyTable

    t = FreeEnergyTable.from_tsv(a.table)
    probs = t.check()
    print(f"{len(t)} rows, phases {t.phases()}, T {t.temperatures().min():g}-{t.temperatures().max():g} K")
    for p in probs:
        print("PROBLEM:", p)
    return 1 if probs else 0


def _cmd_diagram(a):
    from .records import FreeEnergyTable
    from .assemble import builder_from_table, interpolate_T
    from .diagram import scan, invariants, plot_tx, write_records

    t = FreeEnergyTable.from_tsv(a.table)
    Ts = np.arange(a.tmin, a.tmax + 1e-9, a.dt)
    ti = interpolate_T(t, Ts)
    b = builder_from_table(ti, fit=a.fit, poly_order=a.order)
    reg = scan(b, np.sort(ti.temperatures()))
    inv = invariants(reg)
    write_records(a.out, reg, {"table": a.table, "fit": a.fit, "order": a.order, "T": [a.tmin, a.tmax, a.dt]})
    print(reg.to_string(index=False, max_rows=40))
    print("\ninvariants:\n", inv.to_string(index=False) if len(inv) else "none")
    if a.png:
        import matplotlib
        matplotlib.use("Agg")
        ax = plot_tx(reg)
        ax.figure.savefig(a.png, dpi=150, bbox_inches="tight")
        print("wrote", a.png)
    return 0


def _cmd_hull0k(a):
    from .validate import hull_0K, compare_ground_states

    df = pd.read_csv(a.table, sep="\t")
    h = hull_0K(df["name"], df["x"], df["e"])
    print(h.to_string(index=False))
    if a.known:
        print(compare_ground_states(h, a.known.split(",")).to_string(index=False))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="ftphase")
    sp = p.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check", help="validate a free-energy table (TSV)"); c.add_argument("table"); c.set_defaults(f=_cmd_check)
    d = sp.add_parser("diagram", help="T-x diagram from a free-energy table")
    d.add_argument("table"); d.add_argument("--tmin", type=float, required=True); d.add_argument("--tmax", type=float, required=True); d.add_argument("--dt", type=float, default=5.0)
    d.add_argument("--fit", default="spline"); d.add_argument("--order", type=int, default=4); d.add_argument("--out", default="two_phase_regions.tsv"); d.add_argument("--png", default=None)
    d.set_defaults(f=_cmd_diagram)
    h = sp.add_parser("hull0k", help="0 K convex hull from a TSV with columns name,x,e"); h.add_argument("table"); h.add_argument("--known", default=""); h.set_defaults(f=_cmd_hull0k)
    a = p.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
