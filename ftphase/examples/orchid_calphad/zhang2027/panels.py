"""Fig. 2-style grid of phase-set maps: rows = TDB sources (CPDDB assessment, DFT, deposit UMLIPs, this project's MLIPs), columns = the six
binary systems.  Each (x, T) cell is coloured by its equilibrium phase set (same colour for the same set across all panels of a system);
the cell is hatched-free white where the set matches the Modified_CPDDB reference is NOT marked - accuracy numbers are in the titles.
    python panels.py <deposit dir> [--rows DFT grace-2L-SMAX ...] [--extra name=dir ...] [--out out/panels.png]
Grids as in classify.py (notebook 06).  Phase sets are cached in out/cache_<row>_<system>.json.
"""
import argparse, json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from classify import GRIDS, phase_sets

ROWS = ["Modified_CPDDB", "DFT", "grace-2L-SMAX", "SevenNet-omni", "Nequip-OAM-XL", "eSEN-uma-s-1p1"]
PALETTE = ["#f2f2f2", "#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5", "#ffed6f",
           "#1f78b4", "#33a02c", "#e31a1c", "#ff7f00", "#6a3d9a", "#b15928", "#a6cee3", "#b2df8a", "#fb9a99", "#fdbf6f", "#cab2d6"]


def cached_sets(row, folder, system, cache):
    f = os.path.join(cache, f"{row}_{system}.json")
    if os.path.exists(f):
        return [frozenset(s) for s in json.load(open(f))]
    tdb = os.path.join(folder, f"{system}.tdb")
    if not os.path.exists(tdb):
        return None
    ps = phase_sets(tdb, system); json.dump([sorted(s) for s in ps], open(f, "w")); return ps


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("deposit"); ap.add_argument("--rows", nargs="*", default=ROWS); ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--systems", nargs="*", default=["Al-Zn", "Mo-Rh", "Cu-Pt", "W-Re", "Ru-Si", "Cu-Mg"]); ap.add_argument("--out", default=os.path.join(HERE, "out", "panels.png")); a = ap.parse_args()
    extra = dict(e.split("=", 1) for e in a.extra); rows = list(a.rows) + [m for m in extra if m not in a.rows]
    cache = os.path.join(HERE, "out", "cache"); os.makedirs(cache, exist_ok=True)
    fig, axes = plt.subplots(len(rows), len(a.systems), figsize=(2.6 * len(a.systems), 2.1 * len(rows)), squeeze=False)
    for j, system in enumerate(a.systems):
        xel, dx, tlo, thi, dt = GRIDS[system]; nT = int(np.ceil((thi - tlo) / dt - 1e-9))   # pycalphad arange: end point excluded
        ref = None; colors = {}
        for i, row in enumerate(rows):
            ax = axes[i, j]; folder = extra[row] if row in extra else os.path.join(a.deposit, row)
            ps = cached_sets(row, folder, system, cache)
            if ps is None:
                ax.text(0.5, 0.5, "no TDB", ha="center", transform=ax.transAxes); ax.set_xticks([]); ax.set_yticks([]); continue
            if row == "Modified_CPDDB":
                ref = ps
            nx = len(ps) // nT; arr = np.empty(len(ps), dtype=object); arr[:] = ps; arr = arr.reshape(nT, nx)
            img = np.zeros((nT, nx)); 
            for s in sorted({q for q in ps}, key=lambda q: (len(q), sorted(q))):
                colors.setdefault(s, len(colors))
            for r in range(nT):
                for c in range(nx):
                    img[r, c] = colors[arr[r, c]]
            cmap = matplotlib.colors.ListedColormap(PALETTE[:max(len(colors), 1)] + ["#999999"] * max(0, len(colors) - len(PALETTE)))
            ax.imshow(img, origin="lower", aspect="auto", extent=(0, 1, tlo, thi), cmap=cmap, vmin=-0.5, vmax=len(cmap.colors) - 0.5, interpolation="nearest")
            acc = np.mean([p == q for p, q in zip(ref, ps)]) if ref is not None and row != "Modified_CPDDB" else None
            ax.set_title(f"{row}" + (f"  acc {acc:.2f}" if acc is not None else "  (reference)"), fontsize=7.5)
            ax.tick_params(labelsize=6)
            if i == len(rows) - 1:
                ax.set_xlabel(f"x_{xel.capitalize()}", fontsize=7)
            if j == 0:
                ax.set_ylabel("T (K)", fontsize=7)
        axes[0, j].set_title(f"{system}\n" + axes[0, j].get_title(), fontsize=8)
    fig.suptitle("Zhang 2027 systems: phase-set maps per TDB (colour = equilibrium phase set, consistent within a column); acc = phase-label accuracy vs Modified_CPDDB on this grid", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(a.out, dpi=120); print("wrote", a.out)


if __name__ == "__main__":
    main()
