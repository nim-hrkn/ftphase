"""Side-by-side phase-field maps: SGTE reference assessment (left) and an ESPEI TDB (right), same colours per phase set.

    ../../../../env/pycalphad/bin/python plot_compare.py alli-mcmc.tdb out/compare_mcmc.png [--ref AlLi-20Lon] [--T 300 1100]

Left: the stable phase set on the (x, T) grid stored in ORCHID-Diagrams for the reference TDB (pycalphad 0.11.2,
x step 0.01, T step 10 K).  Right: the same grid computed with pycalphad from the given TDB.  Every cell is coloured by
its phase set (phase names normalised: BCC_4SL/B32_BCC -> ALLI_B32, FCC_4SL -> FCC_A1), one legend for both panels.
Black markers on the right are the ORCHID ZPF data used in the fit (one marker per phase of each tie-line with a
printed composition; crosses: handbook phase-field points; dots: derived liquid points)."""

import argparse
import glob
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from pycalphad import Database, equilibrium, variables as v  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SGTE = os.path.join(PROJECT, "data", "orchid-v2026.10", "phase-diagrams", "orchid-phase-diagrams-v2026.10", "phase-diagrams", "sgte")
NORM = {"BCC_4SL": "ALLI_B32", "B32_BCC": "ALLI_B32", "FCC_4SL": "FCC_A1", "A1_FCC": "FCC_A1", "A2_BCC": "BCC_A2"}
PALETTE = ["#f2f2f2", "#5b9bd5", "#70ad47", "#f4a259", "#a05195", "#d45087", "#888888", "#2f4b7c", "#ffa600", "#665191", "#003f5c",
           "#8dd3c7", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#bc80bd", "#ccebc5", "#ffffb3", "#e41a1c", "#377eb8"]


def norm_label(label):
    parts = sorted(set(NORM.get(p.split("#")[0], p.split("#")[0]) for p in label.split("+") if p))
    return "+".join(parts)


def sgte_grid(ref, T_lo, T_hi):
    d = json.load(open(os.path.join(SGTE, ref + ".json"), encoding="utf-8"))
    g = d["grid"]
    labels = [norm_label(l) for l in g["labels"]]
    xs = np.arange(g["x_points"]) * g["x_step"]
    rows = []
    Ts = []
    for i, row in enumerate(g["rows"]):
        T = g["T0"] + i * g["dT"]
        if T < T_lo - 1e-6 or T > T_hi + 1e-6:
            continue
        line = []
        for idx, n in row:
            line += [labels[idx]] * n
        rows.append(line)
        Ts.append(T)
    return xs, np.array(Ts), rows


def tdb_grid(dbf, comps, phases, T_lo, T_hi, dT=10.0, dx=0.01):
    eq = equilibrium(dbf, comps, phases, {v.N: 1, v.P: 101325, v.T: (T_lo, T_hi + 0.1, dT), v.X("LI"): (0, 1.0 + 1e-9, dx)})
    Ts = eq.coords["T"].values
    xs = eq.coords["X_LI"].values
    rows = []
    for it in range(len(Ts)):
        line = []
        for ix in range(len(xs)):
            ph = [p for p in eq.Phase.values[0, 0, it, ix] if p]
            line.append(norm_label("+".join(ph)))
        rows.append(line)
    return xs, Ts, rows


def draw_map(ax, xs, Ts, rows, code, cmap, dx, dT):
    arr = np.array([[code[l] for l in line] for line in rows])
    ax.pcolormesh(np.append(xs, xs[-1] + dx) - dx / 2, np.append(Ts, Ts[-1] + dT) - dT / 2, arr, cmap=cmap, vmin=-0.5, vmax=len(cmap.colors) - 0.5, shading="flat")


def data_points(ax):
    files = glob.glob(os.path.join(HERE, "datasets", "**", "*.json"), recursive=True)
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        if d.get("output") != "ZPF":
            continue
        Ts = d["conditions"]["T"]
        Ts = Ts if isinstance(Ts, list) else [Ts]
        tags = d.get("tags", [])
        marker = "x" if "assessed_phase_diagram" in tags else ("." if "derived" in tags else "o")
        for T, region in zip(Ts, d["values"]):
            for phase, _, xv in region:
                if xv and xv[0] is not None:
                    ax.plot(xv[0], T, marker, color="k", ms=6 if marker != "." else 4, mfc="none" if marker == "o" else "k", mew=1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tdb")
    ap.add_argument("out")
    ap.add_argument("--ref", default="AlLi-20Lon")
    ap.add_argument("--T", nargs=2, type=float, default=[300, 1100])
    ap.add_argument("--no-data", action="store_true")
    args = ap.parse_args()
    dbf = Database(args.tdb)
    comps = ["AL", "LI", "VA"]
    phases = sorted(dbf.phases)
    xs1, Ts1, rows1 = sgte_grid(args.ref, *args.T)
    xs2, Ts2, rows2 = tdb_grid(dbf, comps, phases, *args.T)
    labels = sorted(set(l for r in rows1 + rows2 for l in r), key=lambda l: (l == "", l.count("+"), l))
    if "" in labels:
        labels.remove("")
        labels = [""] + labels
    code = {l: i for i, l in enumerate(labels)}
    fixed = {"": "#ffffff", "FCC_A1": "#ffe08a", "LIQUID": "#cdb4db", "ALLI_B32": "#70ad47", "AL2LI3": "#5b9bd5", "AL4LI9": "#1b9e77",
             "ALLI2": "#e6ab02", "BCC_A2": "#a6761d",
             "ALLI_B32+FCC_A1": "#fb8072", "FCC_A1+LIQUID": "#f4a259", "ALLI_B32+LIQUID": "#80b1d3", "AL2LI3+ALLI_B32": "#2f4b7c",
             "AL2LI3+LIQUID": "#ffa600", "AL2LI3+AL4LI9": "#d45087", "AL4LI9+LIQUID": "#8dd3c7", "AL4LI9+ALLI_B32": "#003f5c",
             "AL2LI3+ALLI2": "#888888", "ALLI2+LIQUID": "#bebada", "AL4LI9+ALLI2": "#665191", "AL4LI9+BCC_A2": "#bc80bd",
             "BCC_A2+LIQUID": "#ccebc5", "AL2LI3+FCC_A1": "#e41a1c", "BCC_A2+FCC_A1": "#377eb8"}
    spare = [c for c in PALETTE if c not in fixed.values()]
    colors = [fixed.get(l) or spare.pop(0) for l in labels]
    cmap = ListedColormap(colors)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), sharey=True)
    draw_map(axes[0], xs1, Ts1, rows1, code, cmap, 0.01, 10.0)
    axes[0].set(title=f"SGTE assessment {args.ref} (ORCHID-Diagrams, pycalphad 0.11.2)", xlabel="x_Li", ylabel="T (K)", xlim=(0, 1), ylim=tuple(args.T))
    draw_map(axes[1], xs2, Ts2, rows2, code, cmap, 0.01, 10.0)
    if not args.no_data:
        data_points(axes[1])
    axes[1].set(title=f"ESPEI fit {os.path.basename(args.tdb)} (ORCHID data only)", xlabel="x_Li", xlim=(0, 1), ylim=tuple(args.T))
    handles = [Patch(facecolor=cmap.colors[code[l]], edgecolor="none", label=l) for l in labels if l]
    if not args.no_data:
        handles += [plt.Line2D([], [], marker="o", color="k", mfc="none", ls="", label="ZPF data: invariant tables (1926-1981)"),
                    plt.Line2D([], [], marker="x", color="k", ls="", label="ZPF data: handbook phase-field points"),
                    plt.Line2D([], [], marker=".", color="k", ls="", label="ZPF data: derived liquid points")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8, frameon=False, title="stable phase set (same colours in both panels)")
    fig.suptitle("Al-Li: evaluated CALPHAD assessment (left) vs ESPEI fit of the ORCHID data (right)", fontsize=11)
    fig.tight_layout(rect=(0, 0.2, 1, 0.96))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=120)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
