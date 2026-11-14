"""Prior (Fig. 4a) and posterior (Fig. 4b) phase-diagram ensembles of the Ru-Si Bayesian update (see build_inputs.py).

Prior: N draws of theta ~ N(0, sigma).  Posterior: N draws from the ESPEI trace after burn-in.  Each theta -> TDB -> pycalphad
equilibrium on an (x, T) grid.  Output out/<set>.npz (phase-boundary points), out/summary.json (P(phase stable anywhere),
parameter means/widths, boundary statistics) and out/fig4.png (prior | posterior, the diagram of the posterior-mean parameters
in yellow, the three tie-lines of the data as circles).
    env/pycalphad/bin/python posterior.py [--n 1000] [--workers 16] [--burn 0.5]
"""
import argparse, json, os, re, time
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
TEXT = None; SYMS = None; GRID = ("SI", 0.01, 500.0, 2500.0, 25.0)


def tdb_with(theta):
    t = TEXT
    for s, val in zip(SYMS, theta):
        t = re.sub(rf"FUNCTION {s} 1 0\.0;", f"FUNCTION {s} 1 {val:.8E};", t)
    return t


def run_one(args):
    k, theta = args
    from pycalphad import Database, equilibrium, variables as v
    try:
        db = Database.from_string(tdb_with(theta), fmt="tdb"); els = ["RU", "SI"]; xel, dx, tlo, thi, dt = GRID
        eq = equilibrium(db, els, list(db.phases.keys()), {v.X(xel): (0, 1, dx), v.T: (tlo, thi, dt), v.P: 101325, v.N: 1})
        P = eq.Phase.values[0, 0]; X = eq.X.values[0, 0, :, :, :, els.index(xel)]; T = eq.coords["T"].values
        sets = [[frozenset(str(p) for p in P[i, j] if p) for j in range(P.shape[1])] for i in range(P.shape[0])]
        pts = [(float(T[i]), float(X[i, j, m]), str(P[i, j, m])) for i in range(P.shape[0]) for j in range(P.shape[1]) for m in range(P.shape[2]) if P[i, j, m]]
        return k, sets, pts
    except Exception as e:
        return k, None, str(e)[:200]


def boundary(pts):
    """Phase-boundary points only: drop single-phase solution points, which sit on the composition grid."""
    return [q for q in pts if q[2] not in ("LIQUID", "HCP") or abs(q[1] / GRID[1] - round(q[1] / GRID[1])) > 1e-6]


def ensemble(name, thetas, workers):
    import pickle
    t0 = time.time(); res = []; cache = os.path.join(OUT, f"{name}_raw.pkl")
    if os.path.exists(cache):
        res = pickle.load(open(cache, "rb"))
    else:
        with Pool(workers) as pool:
            for k, sets, pts in pool.imap_unordered(run_one, list(enumerate(thetas)), chunksize=2):
                if sets is not None:
                    res.append((k, sets, pts))
                if len(res) % 100 == 0:
                    print(name, len(res), f"{time.time() - t0:.0f} s", flush=True)
        res.sort(key=lambda r: r[0]); pickle.dump(res, open(cache, "wb"))
    phases = sorted({p for _, sets, _ in res for row in sets for s in row for p in s}); n = len(res)
    Tg = GRID[2] + GRID[4] * np.arange(len(res[0][1])); xg = GRID[1] * np.arange(len(res[0][1][0]))   # pycalphad's (lo, hi, step) grids exclude hi
    stats = {"n": n, "P_stable_anywhere": {p: float(np.mean([any(p in s for row in sets for s in row) for _, sets, _ in res])) for p in phases}}
    # P(phase present) at the three data temperatures, at the middle of each tie-line
    for T, x, ph in ((1250.0, 0.22, ("HCP", "RU4SI3")), (1550.0, 0.38, ("RU2SI", "RU4SI3")), (1900.0, 0.44, ("LIQUID", "RUSI"))):
        i = int(np.argmin(abs(Tg - T))); j = int(np.argmin(abs(xg - x)))
        stats[f"P_region_{int(T)}K_x{x}"] = {"+".join(ph): float(np.mean([sets[i][j] == frozenset(ph) for _, sets, _ in res]))}
    # Ru-rich side: HCP solvus (largest x of single-phase HCP) at 1250 and 1550 K; highest T with RU2SI; lowest T with liquid at x <= 0.33
    def solvus(sets, T):
        i = int(np.argmin(abs(Tg - T))); xs = [xg[j] for j in range(len(xg)) if sets[i][j] == frozenset(["HCP"])]
        return max(xs) if xs else 0.0
    for T in (1250.0, 1550.0):
        v_ = np.array([solvus(sets, T) for _, sets, _ in res]); stats[f"hcp_solvus_{int(T)}K"] = [float(v_.mean()), float(v_.std())]
    def trange(sets, p, jmax=None):
        rows = [i for i, row in enumerate(sets) if any(p in s for s in (row if jmax is None else row[:jmax]))]
        return (Tg[min(rows)], Tg[max(rows)]) if rows else (np.nan, np.nan)
    for p in ("RU2SI", "SI3RU5", "RU4SI3"):
        r = np.array([trange(sets, p) for _, sets, _ in res]); ok = ~np.isnan(r[:, 0])
        stats[f"{p}_T_range_when_present"] = {"fraction": float(ok.mean()), "T_low_mean_std": [float(r[ok, 0].mean()), float(r[ok, 0].std())] if ok.any() else None,
                                              "T_high_mean_std": [float(r[ok, 1].mean()), float(r[ok, 1].std())] if ok.any() else None}
    j33 = int(np.argmin(abs(xg - 0.33)))
    eut = np.array([trange(sets, "LIQUID", j33 + 1)[0] for _, sets, _ in res]); stats["lowest_T_liquid_x<=0.33"] = [float(np.nanmean(eut)), float(np.nanstd(eut))]
    np.savez_compressed(os.path.join(OUT, f"{name}.npz"), pts=np.array([(q[0], q[1]) for _, _, pts in res for q in boundary(pts)], dtype=np.float32), thetas=np.asarray(thetas))
    print(name, json.dumps(stats, indent=0), flush=True)
    return stats, res


def main():
    global TEXT, SYMS
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--workers", type=int, default=16); ap.add_argument("--burn", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=1); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); TEXT = open(os.path.join(HERE, "rusi-start.tdb")).read(); pr = json.load(open(os.path.join(HERE, "prior.json")))
    SYMS = pr["symbols"]; sig = np.array(pr["sigma"]); rng = np.random.default_rng(a.seed)
    tr = np.load(os.path.join(HERE, "trace.npy")); ln = np.load(os.path.join(HERE, "lnprob.npy"))
    nit = int((np.abs(tr).sum(axis=(0, 2)) > 0).sum()); tr = tr[:, :nit]; ln = ln[:, :nit]; b = int(a.burn * nit)
    flat = tr[:, b:].reshape(-1, tr.shape[2]); post = flat[rng.choice(len(flat), a.n, replace=False)]; prior = rng.normal(0, 1, (a.n, len(SYMS))) * sig
    summary = {"iterations": nit, "walkers": tr.shape[0], "burn_in": b, "lnprob_mean_first_last": [float(ln[:, 0].mean()), float(ln[:, -1].mean())],
               "parameters": [{"phase": p["phase"], "dH_post_mean_std_J": [float(flat[:, 2 * i].mean()), float(flat[:, 2 * i].std())],
                               "dS_post_mean_std_J_K": [float(flat[:, 2 * i + 1].mean()), float(flat[:, 2 * i + 1].std())]} for i, p in enumerate(pr["params"])],
               "prior_sigma": [1410.0, 1.73]}
    sets = {}
    for name, th in (("prior", prior), ("posterior", post)):
        summary[name], _ = ensemble(name, th, a.workers)
    for name, th in (("point_mlip", np.zeros(len(SYMS))), ("point_posterior_mean", flat.mean(axis=0))):
        k, s_, pts = run_one((0, th)); sets[name] = np.array([(q[0], q[1]) for q in boundary(pts)], dtype=np.float32)
        summary[name + "_phases"] = sorted({p for row in s_ for s in row for p in s})
    np.savez_compressed(os.path.join(OUT, "points.npz"), **sets)
    json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    import subprocess, sys
    subprocess.run([sys.executable, os.path.join(HERE, "plot.py")], check=False)


if __name__ == "__main__":
    main()
