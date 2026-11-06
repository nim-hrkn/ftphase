"""Pt-Rh order-disorder temperatures with a cluster expansion + canonical Monte Carlo (icet / mchammer) on a universal MLIP.

    ./env/ftphase/bin/python ce_mc.py --mlip mace-mpa-0 [--device cpu] [--sizes 8] [--T-max 500 --T-min 40 --dT 20]
        icet / mchammer live in env/ftphase; the MLIP energies are computed by a subprocess in the MLIP's env
        (env/mace for MACE, env/torch for SevenNet / MatterSim: `python -m ftphase.aiida.runners relax input.json`, CPU)

Steps
  1. enumerate every fcc ordering with 1..sizes atoms per cell (icet), relax positions + cell with the MLIP, energies per atom
     (the PtRh '40' and the D0_22 structures are 8-atom cells, so they are in the training set)
  2. fit a CE (pairs to 7.0 A, triplets to 5.0 A, ARDR with 10-fold CV); report the CE ground-state line and the energy of
     the ordered structures relative to the random state (ECI-based, no configuration noise)
  3. canonical MC on an 8x8x8 conventional cell (2048 sites) at x_Rh = 0.25, 0.5, 0.75: cooling from T_max to T_min, the
     structure carried from one T to the next; heat capacity C_v = Var(E)/(k_B T^2) per atom and the energy drop locate
     the order-disorder transition (including short-range order, unlike the CEF / Bragg-Williams route of the WorkChain)
Output: out_ce_<mlip>/ (training.tsv, ce_info.json, ground_states.tsv, mc.tsv, REPORT.md, cv.png)."""

import argparse
import importlib.util
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ftphase", "src"))
KB = 8.617333262e-5


def log(m):
    print(time.strftime("%H:%M:%S"), m, flush=True)


def load_mlips():
    spec = importlib.util.spec_from_file_location("run_aiida", os.path.join(ROOT, "ftphase", "examples", "aiida_txdiagram", "run_aiida.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MLIPS


def mlip_energies(mlip, device, structures, out, fmax=2e-3):
    """Relax every structure (positions + cell) with the MLIP in its own env and return energies per atom (eV)."""
    import subprocess

    from ase.io import write

    ml = load_mlips()[mlip]
    inp = {"pair_style": ml.get("qha_pair_style", ml["pair_style"]), "pair_coeff": ml["pair_coeff"].replace("Al Li", "Pt Rh"), "atom_types": {"Pt": 1, "Rh": 2},
           "potential": ml.get("potential_qha") or ml["potential"], "structures": os.path.join(out, "training_in.extxyz"), "relax": {"fmax": fmax, "cell": True},
           "output": os.path.join(out, "relax_output.json"), "output_structures": os.path.join(out, "training_relaxed.extxyz")}
    for k in ("qha_calculator", "qha_dtype", "qha_modal"):
        if k in ml:
            inp[k[4:]] = ml[k]
    if device:
        inp["device"] = device
    write(inp["structures"], structures)
    json.dump(inp, open(os.path.join(out, "relax_input.json"), "w"), indent=1)
    py = os.path.join(ROOT, "env", "mace" if ml.get("qha_calculator") == "mace" else "torch", "bin", "python")
    subprocess.run([py, "-m", "ftphase.aiida.runners", "relax", os.path.join(out, "relax_input.json")], check=True, cwd=out,
                   env={**os.environ, "PYTHONPATH": os.path.join(ROOT, "ftphase", "src")})
    rows = json.load(open(inp["output"]))
    return np.array([r["e"] for r in rows]), rows


def canonical_scan(ce, supercell, x, temperatures, n_eq, n_av, seed=0):
    from mchammer.calculators import ClusterExpansionCalculator  # type: ignore
    from mchammer.ensembles import CanonicalEnsemble  # type: ignore

    s = supercell.copy()
    n = len(s)
    n_rh = int(round(x * n))
    rng = np.random.default_rng(seed)
    syms = np.array(["Pt"] * n)
    syms[rng.choice(n, n_rh, replace=False)] = "Rh"
    s.set_chemical_symbols(list(syms))
    calc = ClusterExpansionCalculator(s, ce)
    rows = []
    for k, T in enumerate(temperatures):
        mc = CanonicalEnsemble(s, calculator=calc, temperature=float(T), random_seed=seed + 1000 * k, ensemble_data_write_interval=n)
        mc.run((n_eq + n_av) * n)
        data = mc.data_container.data
        data = data[data["mctrial"] > n_eq * n]
        E = data["potential"].to_numpy()
        e_mean = float(E.mean()) / n
        cv = float(E.var(ddof=0)) / (KB * T * T) / n          # eV/K per atom
        rows.append({"x": x, "T": float(T), "E_per_atom": e_mean, "Cv_per_atom_kB": cv / KB, "n_samples": int(len(E))})
        s = mc.structure
        log(f"x={x:.2f} T={T:5.0f} K  E={e_mean:.5f} eV/atom  Cv={cv / KB:.3f} k_B")
    return rows, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mlip", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--sizes", type=int, default=8)
    ap.add_argument("--cutoffs", type=float, nargs="+", default=[7.0, 5.0])
    ap.add_argument("--T-max", type=float, default=500.0)
    ap.add_argument("--T-min", type=float, default=40.0)
    ap.add_argument("--dT", type=float, default=20.0)
    ap.add_argument("--n-eq", type=int, default=40)
    ap.add_argument("--n-av", type=int, default=80)
    ap.add_argument("--cell", type=int, default=8)
    ap.add_argument("--xs", type=float, nargs="+", default=[0.25, 0.5, 0.75])
    a = ap.parse_args()
    import pandas as pd
    from ase.build import bulk

    from ftphase.ce import enumerate_training_structures, fit_cluster_expansion

    out = os.path.join(HERE, f"out_ce_{a.mlip}")
    os.makedirs(out, exist_ok=True)
    prim = bulk("Pt", "fcc", a=3.87)   # between Pt 3.924 and Rh 3.803; the lattice is only the CE reference, every cell is relaxed
    syms = [["Pt", "Rh"]]
    t0 = time.time()
    structures = enumerate_training_structures(prim, syms, range(1, a.sizes + 1))
    log(f"{len(structures)} enumerated fcc orderings (1-{a.sizes} atoms)")
    energies, relax_rows = mlip_energies(a.mlip, a.device, structures, out)
    log(f"relaxed in {time.time() - t0:.0f} s ({sum(1 for r in relax_rows if not r['converged'])} not converged, {sum(1 for r in relax_rows if r['transformed'])} changed symmetry)")
    xs = np.array([np.mean(np.array(s.get_chemical_symbols()) == "Rh") for s in structures])
    e_pt = energies[[i for i, s in enumerate(structures) if set(s.get_chemical_symbols()) == {"Pt"}][0]]
    e_rh = energies[[i for i, s in enumerate(structures) if set(s.get_chemical_symbols()) == {"Rh"}][0]]
    eform = energies - (1 - xs) * e_pt - xs * e_rh
    pd.DataFrame({"index": range(len(structures)), "n_atoms": [len(s) for s in structures], "x_Rh": xs, "E_per_atom": energies, "E_form": eform}).to_csv(os.path.join(out, "training.tsv"), sep="\t", index=False)
    ce, info = fit_cluster_expansion(prim, syms, a.cutoffs, structures, energies)
    info["mlip"] = a.mlip
    log(f"CE: rmse train {info['rmse_train'] * 1000:.2f}, CV {info['rmse_validation'] * 1000:.2f} meV/atom, {info['n_nonzero_parameters']} / {info['n_parameters']} ECIs")
    json.dump(info, open(os.path.join(out, "ce_info.json"), "w"), indent=1)
    ce.write(os.path.join(out, "ce.icet"))
    # ground-state line of the training set and the CE energy of the random state (mean-field: ECI x pair-product cluster vectors)
    from icet.tools import ConvexHull  # type: ignore

    hull = ConvexHull(xs, eform)
    gs = pd.DataFrame({"x_Rh": hull.concentrations, "E_form_hull": hull.energies})
    gs.to_csv(os.path.join(out, "ground_states.tsv"), sep="\t", index=False)
    # random-state energy from the CE: average over random configurations of the big cell
    sc = prim.repeat((a.cell, a.cell, a.cell))
    from mchammer.calculators import ClusterExpansionCalculator  # type: ignore

    rand = {}
    rng = np.random.default_rng(1)
    for x in a.xs:
        vals = []
        for _ in range(4):
            s = sc.copy(); n = len(s); syms_ = np.array(["Pt"] * n); syms_[rng.choice(n, int(round(x * n)), replace=False)] = "Rh"; s.set_chemical_symbols(list(syms_))
            vals.append(ClusterExpansionCalculator(s, ce).calculate_total(occupations=s.get_atomic_numbers()) / n)
        rand[x] = float(np.mean(vals)) - (1 - x) * e_pt - x * e_rh
    ordered = {}
    for name, x in (("PtRh-40", 0.5), ("PtRh3-D0_22", 0.75), ("Pt3Rh-D0_22", 0.25)):
        cand = [(i, eform[i]) for i in range(len(structures)) if abs(xs[i] - x) < 1e-6 and len(structures[i]) == 8]
        ordered[name] = float(min(e for _, e in cand)) if cand else float("nan")
    # MC
    temps = np.arange(a.T_max, a.T_min - 1e-6, -a.dT)
    rows = []
    for x in a.xs:
        r, _ = canonical_scan(ce, sc, x, temps, a.n_eq, a.n_av, seed=int(x * 100))
        rows += r
    mc = pd.DataFrame(rows)
    mc.to_csv(os.path.join(out, "mc.tsv"), sep="\t", index=False)
    tc = {}
    for x in a.xs:
        g = mc[np.isclose(mc.x, x)]
        tc[x] = float(g.loc[g.Cv_per_atom_kB.idxmax(), "T"])
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for x in a.xs:
        g = mc[np.isclose(mc.x, x)]
        axes[0].plot(g["T"], g["Cv_per_atom_kB"], "o-", ms=3, label=f"x_Rh = {x:.2f}")
        axes[1].plot(g["T"], (g["E_per_atom"] - (1 - x) * e_pt - x * e_rh) * 1000, "o-", ms=3, label=f"x_Rh = {x:.2f}")
    axes[0].set(xlabel="T (K)", ylabel="C_v (k_B / atom)", title=f"{a.mlip}: CE + canonical MC, {a.cell}^3 fcc cell")
    axes[1].set(xlabel="T (K)", ylabel="E_form (meV/atom)")
    axes[0].legend(); fig.tight_layout(); fig.savefig(os.path.join(out, "cv.png"), dpi=120)
    L = [f"# Pt-Rh CE + canonical MC with {a.mlip} ({time.strftime('%F')})", "",
         f"Training: {info['n_structures']} fcc orderings (1-{a.sizes} atoms), relaxed (positions + cell, fmax 2e-3). CE cutoffs {a.cutoffs} A, ARDR, "
         f"rmse train {info['rmse_train'] * 1000:.2f} / CV {info['rmse_validation'] * 1000:.2f} meV/atom, {info['n_nonzero_parameters']} nonzero of {info['n_parameters']} ECIs.", "",
         "## 0 K: ordered structures vs the random state (CE)", "", "| structure | x_Rh | E_form (MLIP, relaxed) meV/atom | E_form random (CE) | ordering energy |", "|---|---|---|---|---|"]
    for name, x in (("Pt3Rh-D0_22", 0.25), ("PtRh-40", 0.5), ("PtRh3-D0_22", 0.75)):
        L.append(f"| {name} | {x} | {ordered[name] * 1000:.1f} | {rand[x] * 1000:.1f} | {(ordered[name] - rand[x]) * 1000:.1f} |")
    L += ["", "Ground-state line of the training set (x, E_form meV/atom): " + ", ".join(f"({x:.3f}, {e * 1000:.1f})" for x, e in zip(hull.concentrations, hull.energies)), "",
          "## Order-disorder temperatures (C_v peak of the cooling scan)", "", "| x_Rh | T_c (K) | C_v max (k_B) |", "|---|---|---|"]
    for x in a.xs:
        g = mc[np.isclose(mc.x, x)]
        L.append(f"| {x:.2f} | {tc[x]:.0f} | {g.Cv_per_atom_kB.max():.2f} |")
    L += ["", f"MC: {a.cell}^3 conventional cell ({len(sc)} sites), {a.n_eq} + {a.n_av} sweeps per T, cooling {a.T_max:.0f} -> {a.T_min:.0f} K in {a.dT:.0f} K steps; "
          "the structure is carried between temperatures (hysteresis possible for first-order transitions). Lattice CE: no vibrations, no relaxation energy beyond the training cells.",
          "", "Reference (Saengdeejing et al. 2026, Table 7): fcc <-> PtRh 258 K (PFP) / 210 K (DFT); fcc <-> PtRh3 235 / 156 K; fcc <-> Pt3Rh 146 K (PFP only); Pohl & Albe MC: PtRh 238 K."]
    open(os.path.join(out, "REPORT.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
