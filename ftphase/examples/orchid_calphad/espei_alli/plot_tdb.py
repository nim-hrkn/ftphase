"""Plot a TDB with pycalphad's binplot, the ORCHID ZPF datasets on top (espei dataplot), and the SGTE reference boundaries.

    ../../../../env/pycalphad/bin/python plot_tdb.py alli-mcmc.tdb out/alli_mcmc.png [--ref AlLi-20Lon] [--T 300 1100]
"""

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from espei.datasets import load_datasets, recursive_glob  # noqa: E402
from espei.plot import dataplot  # noqa: E402
from pycalphad import Database, binplot, variables as v  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SGTE = os.path.join(PROJECT, "data", "orchid-v2026.10", "phase-diagrams", "orchid-phase-diagrams-v2026.10", "phase-diagrams", "sgte")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tdb")
    ap.add_argument("out")
    ap.add_argument("--ref", default="AlLi-20Lon")
    ap.add_argument("--T", nargs=2, type=float, default=[300, 1100])
    ap.add_argument("--dT", type=float, default=5.0)
    ap.add_argument("--no-data", action="store_true")
    args = ap.parse_args()
    dbf = Database(args.tdb)
    comps = ["AL", "LI", "VA"]
    phases = sorted(dbf.phases.keys())
    fig = plt.figure(figsize=(7.5, 6))
    ax = fig.add_subplot(111)
    conds = {v.N: 1, v.P: 101325, v.T: (args.T[0], args.T[1], args.dT), v.X("LI"): (0, 1, 0.01)}
    binplot(dbf, comps, phases, conds, plot_kwargs={"ax": ax, "tielines": False})
    if not args.no_data:
        ds = load_datasets(recursive_glob(os.path.join(HERE, "datasets"), "*.json"))
        try:
            dataplot(comps, phases, conds, ds, ax=ax)
        except Exception as e:  # dataplot is fragile for __HYPERPLANE__ entries; the diagram is still useful
            print("dataplot skipped:", e)
    ref = os.path.join(SGTE, args.ref + ".json")
    if os.path.exists(ref):
        d = json.load(open(ref, encoding="utf-8"))
        for region in d.get("regions") or []:
            for side in region:
                ax.plot(side["x"], side["T"], color="k", lw=0.8, alpha=0.8)
        for inv in d.get("invariants") or []:
            xs = [p["x"] for p in inv["points"]]
            ax.plot([min(xs), max(xs)], [inv["T"]] * 2, color="k", lw=0.8, ls="--")
    ax.set(xlim=(0, 1), ylim=tuple(args.T), xlabel="x_Li", ylabel="T (K)", title=f"{os.path.basename(args.tdb)} (black: SGTE {args.ref})")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.out, dpi=120)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
