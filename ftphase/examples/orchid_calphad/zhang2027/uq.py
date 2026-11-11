"""Reproduce Zhang et al. 2027 Fig. 4a: uncertainty quantification of the Ru-Si (eSEN) phase diagram.  The TDB's compound
parameters get an independent dH - T dS per mole of atoms (times the formula-unit site count), the HCP interaction L0 likewise,
with dH ~ N(0, 1.41 kJ/mol) and dS ~ N(0, 1.73 J/mol/K) (the paper's MLIP-level uncertainty); the liquid (borrowed from CPDDB)
is left as is.  N samples -> equilibrium on a (x, T) grid -> probability that each phase is stable anywhere, probability maps,
and the Fig. 4a-style overlay of all sampled phase compositions.
    python uq.py <tdb> [--n 1000] [--workers 8] [--T 500 2500 25] [--dx 0.01] [--sigma-H 1414] [--sigma-S 1.73] [--out out/uq_<name>]
"""
import argparse, json, os, re, sys, time
from collections import Counter
from multiprocessing import Pool
import numpy as np

TDB_TEXT = None; GRID = None; PERTURB = None


def site_counts(text):
    out = {}
    for m in re.finditer(r"^\s*PHASE\s+(\w+)\s+%\s+(\d+)\s+([\d.\s]+)!", text, re.M):
        out[m.group(1).upper()] = sum(float(v) for v in m.group(3).split())
    return out


def perturbable(text):
    """(line index, phase, multiplier) for every compound G parameter and the HCP L0."""
    lines = text.split("\n"); sc = site_counts(text); items = []
    for i, l in enumerate(lines):
        m = re.match(r"\s*PARAMETER\s+([GL])\((\w+),([^;]+);(\d)\)", l)
        if not m:
            continue
        ph = m.group(2).upper(); sub = m.group(3)
        if ph in ("LIQUID",):
            continue
        if ph == "HCP":
            if "," in sub and m.group(4) == "0":
                items.append((i, ph, 1.0))
            continue
        if "," not in sub and ph in sc:          # stoichiometric compound end member (one constituent per sublattice)
            items.append((i, ph, sc[ph]))
    return items


def sample_tdb(text, items, dH, dS):
    lines = text.split("\n")
    for (i, ph, mult), h, s in zip(items, dH, dS):
        lines[i] = re.sub(r";(\s*\d+(?:\.\d+)?\s+N\s*!)", f"{mult * h:+.6E}{-mult * s:+.6E}*T;\\1", lines[i], count=1)
    return "\n".join(lines)


def run_one(args):
    k, dH, dS = args
    from pycalphad import Database, equilibrium, variables as v
    try:
        db = Database.from_string(sample_tdb(TDB_TEXT, PERTURB, dH, dS), fmt="tdb") if k >= 0 else Database.from_string(TDB_TEXT, fmt="tdb")
        els = [e for e in db.elements if e != "/-"]; xel, dx, tlo, thi, dt = GRID
        eq = equilibrium(db, els, list(db.phases.keys()), {v.X(xel): (0, 1, dx), v.T: (tlo, thi, dt), v.P: 101325, v.N: 1})
        P = eq.Phase.values[0, 0]; X = eq.X.values[0, 0, :, :, :, els.index(xel)]; T = eq.coords["T"].values
        sets = [[frozenset(p for p in P[i, j] if p) for j in range(P.shape[1])] for i in range(P.shape[0])]
        pts = [(float(T[i]), float(X[i, j, m]), str(P[i, j, m])) for i in range(P.shape[0]) for j in range(P.shape[1]) for m in range(P.shape[2]) if P[i, j, m]]
        return k, sets, pts
    except Exception as e:
        return k, None, str(e)[:200]


def main():
    global TDB_TEXT, GRID, PERTURB
    ap = argparse.ArgumentParser(); ap.add_argument("tdb"); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--T", nargs=3, type=float, default=[500, 2500, 25]); ap.add_argument("--dx", type=float, default=0.01); ap.add_argument("--x", default=None)
    ap.add_argument("--sigma-H", type=float, default=1414.0); ap.add_argument("--sigma-S", type=float, default=1.73); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    TDB_TEXT = open(a.tdb).read(); PERTURB = perturbable(TDB_TEXT)
    xel = a.x or sorted(e for e in re.findall(r"^ELEMENT\s+(\w+)", TDB_TEXT, re.M) if e not in ("VA", "/-"))[-1]
    GRID = (xel, a.dx, a.T[0], a.T[1], a.T[2])
    name = os.path.basename(os.path.dirname(os.path.abspath(a.tdb))) + "_" + os.path.basename(a.tdb)[:-4]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", f"uq_{name}"); os.makedirs(out, exist_ok=True)
    print("perturbed parameters:", [(ph, m) for _, ph, m in PERTURB], "| x =", xel, "| grid", GRID, flush=True)
    rng = np.random.default_rng(a.seed); n_par = len(PERTURB)
    jobs = [(-1, np.zeros(n_par), np.zeros(n_par))] + [(k, rng.normal(0, a.sigma_H, n_par), rng.normal(0, a.sigma_S, n_par)) for k in range(a.n)]
    t0 = time.time(); results = []; fails = 0
    with Pool(a.workers) as pool:
        for k, sets, pts in pool.imap_unordered(run_one, jobs, chunksize=2):
            if sets is None:
                fails += 1; print("sample", k, "failed:", pts, flush=True); continue
            results.append((k, sets, pts))
            if len(results) % 50 == 0:
                print(f"{len(results)} samples done ({time.time() - t0:.0f} s)", flush=True)
    results.sort(key=lambda r: r[0]); base = next(r for r in results if r[0] == -1); samples = [r for r in results if r[0] >= 0]
    phases = sorted({p for _, sets, _ in results for row in sets for s in row for p in s})
    nT = len(base[1]); nx = len(base[1][0])
    stable_any = {p: np.mean([any(p in s for row in sets for s in row) for _, sets, _ in samples]) for p in phases}
    pmap = {p: np.zeros((nT, nx)) for p in phases}
    for _, sets, _ in samples:
        for i, row in enumerate(sets):
            for j, s in enumerate(row):
                for p in s:
                    pmap[p][i, j] += 1.0 / len(samples)
    # how often the sampled phase set equals the unperturbed one (a 'self-consistency' accuracy)
    acc = [np.mean([s == b for row, brow in zip(sets, base[1]) for s, b in zip(row, brow)]) for _, sets, _ in samples]
    summary = {"tdb": os.path.abspath(a.tdb), "n_samples": len(samples), "n_failed": fails, "sigma_H_J": a.sigma_H, "sigma_S_J_K": a.sigma_S, "grid": GRID,
               "perturbed": [(ph, m) for _, ph, m in PERTURB], "P_stable_anywhere": stable_any,
               "P_stable_anywhere_unperturbed": {p: bool(any(p in s for row in base[1] for s in row)) for p in phases},
               "accuracy_vs_unperturbed_mean": float(np.mean(acc)), "accuracy_vs_unperturbed_p05_p95": [float(np.percentile(acc, 5)), float(np.percentile(acc, 95))], "seconds": time.time() - t0}
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1, default=str)
    np.savez_compressed(os.path.join(out, "pmaps.npz"), T=np.arange(GRID[2], GRID[3] + 1e-6, GRID[4]), x=np.arange(0, 1 + 1e-9, GRID[1]), **{p: pmap[p] for p in phases})
    np.savez_compressed(os.path.join(out, "points.npz"), samples=np.array([(q[0], q[1]) for _, _, pts in samples for q in pts], dtype=np.float32),
                        base=np.array([(q[0], q[1]) for q in base[2]], dtype=np.float32), base_phase=np.array([q[2] for q in base[2]]))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("perturbed", "grid")}, indent=0, default=str))
    # figure: Fig. 4a style
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    xs = np.array([q[1] for _, _, pts in samples for q in pts]); Ts = np.array([q[0] for _, _, pts in samples for q in pts])
    ax.scatter(xs, Ts, s=0.4, c="#1f4e8c", alpha=min(1.0, 25.0 / max(1, len(samples))), linewidths=0, rasterized=True)
    bx = np.array([q[1] for q in base[2]]); bT = np.array([q[0] for q in base[2]])
    ax.scatter(bx, bT, s=0.8, c="#e8c100", linewidths=0, label="unperturbed TDB", rasterized=True)
    k = 0
    for p, pr in sorted(stable_any.items(), key=lambda kv: -kv[1]):
        if p in ("LIQUID", "HCP") or pr < 0.02:
            continue
        m = pmap[p]; cols = np.where(m.max(axis=0) > 0.05)[0]; rows = np.where(m.max(axis=1) > 0.05)[0]
        xp = float(np.average(cols * GRID[1], weights=m.max(axis=0)[cols])); Tp = GRID[2] + rows.max() * GRID[4]
        ax.annotate(f"{p} {pr:.2f}", (xp, Tp), xytext=(xp, GRID[3] - (0.05 + 0.055 * (k % 6)) * (GRID[3] - GRID[2])), fontsize=7, ha="center", color="k",
                    arrowprops=dict(arrowstyle="-", lw=0.5, color="0.4")); k += 1
    ax.set(xlim=(0, 1), ylim=(GRID[2], GRID[3]), xlabel=f"x_{xel.capitalize()}", ylabel="T (K)",
           title=f"{name}: {len(samples)} samples, dH~N(0,{a.sigma_H / 1000:.2f} kJ/mol), dS~N(0,{a.sigma_S} J/mol/K)\nlabels: P(phase stable anywhere)", )
    ax.title.set_fontsize(9); ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout(); fig.savefig(os.path.join(out, "uq_overlay.png"), dpi=150); print("->", out)


if __name__ == "__main__":
    main()
