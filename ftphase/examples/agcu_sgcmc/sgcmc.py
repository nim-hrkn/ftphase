"""Route B for Ag-Cu: semi-grand-canonical MC (LAMMPS fix atom/swap + MD) with the Williams-Mishin-Hamilton
2006 EAM, no free-energy fit.  Produces the fcc solubility limits (miscibility gap) directly and, by
integrating dG/dx = dmu along each branch, the free-energy curves of the two fcc branches.

    python sgcmc.py prepare [--smoke]      write LAMMPS inputs: one run per (T, direction); each run sweeps
                                           dmu = mu_Cu - mu_Ag in steps, equilibrates, averages x_Cu and E
    python sgcmc.py analyse                read runs/*/sweep.dat -> out/sgc_branches.tsv, out/gap_vs_T.tsv,
                                           out/REPORT.md, out/sgc_gap.png, and compare with the RK-based gap of
                                           the AiiDA run (out/rk_gap.tsv if present)

Directions: 'up' starts from pure Ag (x_Cu = 0) at the lowest dmu and raises dmu (Ag-rich branch, alpha);
'down' starts from pure Cu at the highest dmu and lowers it (Cu-rich branch, beta).  The jump of x in each
direction is the end of the metastable branch; the equilibrium solvus comes from the common tangent of the
two integrated branches (G_alpha(x) = G_Ag + int dmu dx, G_beta(x) = G_Cu - int dmu dx from the Cu end),
anchored on G_Ag, G_Cu of the same potential (any common constant cancels in the tangent construction).
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "potentials/agcu/CuAg.eam.alloy")
RUNS = os.path.join(HERE, "runs")
OUT = os.path.join(HERE, "out")

T_LIST = [800.0, 900.0, 1000.0]
DMU = np.round(np.arange(-1.00, -0.299, 0.02), 3)         # eV, mu_Cu - mu_Ag (the 900 K smoke test put the jumps between -0.9 and -0.5)
N_REP = 8                                                 # 8x8x8 conventional cells = 2048 atoms
STEPS_EQ, STEPS_AV = 20000, 20000                         # 1 fs steps: 20 ps + 20 ps per dmu
SWAP_EVERY, SWAP_N = 10, 20                              # 2 swap attempts per MD step (each attempt is a full energy evaluation)


def lammps_input(T, direction, dmus, n_rep, steps_eq, steps_av, seed):
    start_type = 1 if direction == "up" else 2            # 1 = Ag, 2 = Cu
    a0 = 4.09 if start_type == 1 else 3.615
    order = list(dmus) if direction == "up" else list(dmus)[::-1]
    L = [f"# SGC MC Ag-Cu, T={T} K, direction {direction}", "units metal", "atom_style atomic", "boundary p p p",
         f"lattice fcc {a0}", f"region box block 0 {n_rep} 0 {n_rep} 0 {n_rep}", "create_box 2 box", f"create_atoms {start_type} box",
         "mass 1 107.8682", "mass 2 63.546", "pair_style eam/alloy", f"pair_coeff * * {POT} Ag Cu",
         "variable is2 atom type==2", "compute n2 all reduce sum v_is2", "variable xcu equal c_n2/atoms", "variable epa equal pe/atoms", "variable vpa equal vol/atoms",
         "timestep 0.001", f"velocity all create {T} {seed} loop geom",
         f"fix nptf all npt temp {T} {T} 0.1 iso 0.0 0.0 1.0", "thermo 5000", "thermo_style custom step temp pe press vol v_xcu",
         "print \"# dmu_eV  x_cu  pe_per_atom_eV  vol_per_atom_A3  x_std\" file sweep.dat screen no"]
    for i, dmu in enumerate(order):
        L += [f"# ---- dmu = {dmu}", "unfix sw" if i > 0 else "",
              f"fix sw all atom/swap {SWAP_EVERY} {SWAP_N} {seed + i} {T} ke no semi-grand yes types 1 2 mu 0.0 {dmu}",
              f"run {steps_eq}",
              "unfix avg" if i > 0 else "",
              f"fix avg all ave/time 100 {steps_av // 100} {steps_av} v_xcu v_epa v_vpa ave one",
              f"run {steps_av}",
              "variable xm equal f_avg[1]", "variable em equal f_avg[2]", "variable vm equal f_avg[3]",
              f"print \"{dmu} ${{xm}} ${{em}} ${{vm}} 0\" append sweep.dat screen no"]
    return "\n".join(x for x in L if x is not None) + "\n"


def prepare(smoke=False):
    dmus, n_rep, se, sa, Ts = DMU, N_REP, STEPS_EQ, STEPS_AV, T_LIST
    if smoke:
        dmus, n_rep, se, sa, Ts = np.array([-0.9, -0.7, -0.5]), 4, 500, 500, [900.0]
    os.makedirs(RUNS, exist_ok=True)
    jobs = []
    for T in Ts:
        for d in ("up", "down"):
            tag = f"T{T:.0f}_{d}"
            dd = os.path.join(RUNS, tag)
            os.makedirs(dd, exist_ok=True)
            with open(os.path.join(dd, "in.sgc"), "w") as f:
                f.write(lammps_input(T, d, dmus, n_rep, se, sa, seed=4711 + int(T) + (0 if d == "up" else 1)))
            jobs.append(tag)
    with open(os.path.join(RUNS, "jobs.json"), "w") as f:
        json.dump({"jobs": jobs, "dmu": [float(v) for v in dmus], "n_rep": n_rep, "n_atoms": 4 * n_rep ** 3, "steps_eq": se, "steps_av": sa, "T": Ts}, f, indent=1)
    print(f"prepared {len(jobs)} runs in {RUNS}: {jobs}; {len(dmus)} dmu points, {4 * n_rep**3} atoms")


def _branches():
    data = {}
    for d in sorted(glob.glob(os.path.join(RUNS, "T*_*"))):
        tag = os.path.basename(d)
        p = os.path.join(d, "sweep.dat")
        if not os.path.exists(p):
            continue
        a = np.loadtxt(p, ndmin=2)
        if a.size == 0:
            continue
        a = np.unique(a, axis=0)                          # duplicate lines appear when mpirun starts serial copies
        T = float(tag[1:].split("_")[0]); direction = tag.split("_")[1]
        data.setdefault(T, {})[direction] = a[np.argsort(a[:, 0])]
    return data


def analyse():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    from ftphase.equilibrium import PhaseCurve, equilibrium_at_T

    os.makedirs(OUT, exist_ok=True)
    data = _branches()
    rows, gaps = [], []
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for T, br in sorted(data.items()):
        for direction, a in br.items():
            for dmu, x, e, v, _ in a:
                rows.append({"T": T, "direction": direction, "dmu_eV": dmu, "x_Cu": x, "E_per_atom_eV": e, "V_per_atom_A3": v})
        if "up" not in br or "down" not in br:
            continue
        up, down = br["up"], br["down"]
        # metastable-branch ends (jumps): largest x step
        def jump(a):
            dx = np.diff(a[:, 1]); i = int(np.argmax(np.abs(dx))); return a[i, 0], a[i + 1, 0], a[i, 1], a[i + 1, 1]
        ju, jd = jump(up), jump(down)
        # the alpha (Ag-rich) branch = 'up' points before its jump; the beta (Cu-rich) branch = 'down' points above its jump
        alpha = up[up[:, 0] <= ju[0] + 1e-9]
        beta = down[down[:, 0] >= jd[1] - 1e-9]
        # integrate dG/dx = dmu along each branch -> G(x) relative to the pure end of that branch (x strictly increasing;
        # points with the same composition, e.g. the pure end at very negative dmu, are merged)
        def integrate(a):
            x = a[:, 1]; dmu = a[:, 0]
            order = np.argsort(x); x = x[order]; dmu = dmu[order]
            xu, idx = np.unique(np.round(x, 6), return_inverse=True)
            du = np.array([dmu[idx == k].mean() for k in range(len(xu))])
            g = np.concatenate([[0.0], np.cumsum(0.5 * (du[1:] + du[:-1]) * np.diff(xu))])
            return xu, g
        xa, ga = integrate(alpha)
        xb, gb = integrate(beta)
        if len(xa) < 3 or len(xb) < 3:
            continue
        # branch alpha: G_alpha(x) = G_Ag + ga(x); branch beta: G_beta(x) = G_Cu + (gb(x) - gb(1)) ; G_Cu - G_Ag from the SGC runs:
        # at coexistence dmu* both grand potentials are equal; estimate dmu* as the midpoint of the hysteresis loop and
        # fix G_Cu - G_Ag = int over the full (combined) isotherm of dmu dx using the midpoint construction
        dmu_star = 0.5 * (ju[0] + jd[1])
        # Maxwell-like estimate: G_Cu - G_Ag = integral of dmu over x from 0 to 1 along the combined isotherm with the jump at dmu_star
        xa_lim = np.interp(dmu_star, up[:, 0], up[:, 1]); xb_lim = np.interp(dmu_star, down[:, 0], down[:, 1])
        g_alpha_at = np.interp(xa_lim, xa, ga); g_beta_rel_at = np.interp(xb_lim, xb, gb) - gb[-1]
        dG_CuAg = g_alpha_at + dmu_star * (xb_lim - xa_lim) - g_beta_rel_at     # G(pure Cu) - G(pure Ag) from the Maxwell midpoint
        G_alpha = ga; G_beta = (gb - gb[-1]) + dG_CuAg
        # common tangent between the two branches via the lower hull of both curves
        pa = PhaseCurve.from_points("fcc_alpha", xa, G_alpha, fit="spline", limited=True)
        pb = PhaseCurve.from_points("fcc_beta", xb, G_beta, fit="spline", limited=True)
        eq = equilibrium_at_T([pa, pb], T, min_width=0.005)
        seg = [c for c in eq.coexistence if c.phase_a != c.phase_b]
        if seg:
            r = seg[0]
            gaps.append({"T": T, "x_alpha_tangent": float(r.x_a), "x_beta_tangent": float(r.x_b), "dmu_star_eV": dmu_star,
                         "x_alpha_jump": float(ju[2]), "x_beta_jump": float(jd[3]), "dmu_jump_up": float(ju[0]), "dmu_jump_down": float(jd[1]), "dG_Cu_minus_Ag_eV": float(dG_CuAg)})
        axes[0].plot(up[:, 0], up[:, 1], "o-", ms=3, label=f"{T:.0f} K up"); axes[0].plot(down[:, 0], down[:, 1], "s--", ms=3, label=f"{T:.0f} K down")
        axes[1].plot(xa, G_alpha, "-", label=f"{T:.0f} K alpha"); axes[1].plot(xb, G_beta, "--", label=f"{T:.0f} K beta")
    axes[0].set_xlabel("dmu = mu_Cu - mu_Ag (eV)"); axes[0].set_ylabel("x_Cu"); axes[0].legend(fontsize=7)
    axes[1].set_xlabel("x_Cu"); axes[1].set_ylabel("G - G_Ag (eV/atom), integrated dmu dx"); axes[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "sgc_gap.png"), dpi=150)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "sgc_branches.tsv"), sep="\t", index=False)
    pd.DataFrame(gaps).to_csv(os.path.join(OUT, "gap_vs_T.tsv"), sep="\t", index=False)
    L = ["# Ag-Cu fcc miscibility gap from semi-grand-canonical MC (EAM, fix atom/swap + NPT MD), no free-energy fit", "",
         f"runs: {sorted(data)} K, up/down sweeps of dmu; points per sweep {len(rows)//max(1,2*len(data))}", "",
         "| T (K) | x_alpha (tangent) | x_beta (tangent) | x_alpha (jump, up) | x_beta (jump, down) | dmu* (eV) | hysteresis dmu (eV) |", "|---|---|---|---|---|---|---|"]
    for g in gaps:
        L.append(f"| {g['T']:.0f} | {g['x_alpha_tangent']:.3f} | {g['x_beta_tangent']:.3f} | {g['x_alpha_jump']:.3f} | {g['x_beta_jump']:.3f} | {g['dmu_star_eV']:+.3f} | {g['dmu_jump_up'] - g['dmu_jump_down']:+.3f} |")
    rk = os.path.join(OUT, "rk_gap.tsv")
    if os.path.exists(rk):
        r = pd.read_csv(rk, sep="\t")
        L += ["", "## Comparison with the ideal + Redlich-Kister fit of the random-cell free energies (AiiDA run, example 9)", "",
              "| T (K) | SGC x_alpha | RK x_alpha | SGC x_beta | RK x_beta |", "|---|---|---|---|---|"]
        for g in gaps:
            rr = r[np.isclose(r["T"], g["T"])]
            if len(rr):
                L.append(f"| {g['T']:.0f} | {g['x_alpha_tangent']:.3f} | {float(rr['x_alpha'].iloc[0]):.3f} | {g['x_beta_tangent']:.3f} | {float(rr['x_beta'].iloc[0]):.3f} |")
    with open(os.path.join(OUT, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


def rkgap(regions_tsv):
    """fcc+fcc segments of a 07_two_phase_regions.tsv (ideal + Redlich-Kister route) at the SGC temperatures -> out/rk_gap.tsv."""
    import pandas as pd

    os.makedirs(OUT, exist_ok=True)
    reg = pd.read_csv(regions_tsv, sep="\t", comment="#")
    rows = []
    for T in T_LIST:
        r = reg[np.isclose(reg["T"], T) & (reg.phase_a == "fcc") & (reg.phase_b == "fcc")]
        if len(r):
            r = r.sort_values("x_a")
            rows.append({"T": T, "x_alpha": float(r["x_a"].iloc[0]), "x_beta": float(r["x_b"].iloc[-1]), "n_segments": int(len(r))})
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "rk_gap.tsv"), sep="\t", index=False)
    print(pd.DataFrame(rows).to_string(index=False) if rows else "no fcc+fcc segments at the SGC temperatures")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prepare", "analyse", "rkgap"]); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--regions", default=os.path.join(HERE, "..", "aiida_txdiagram", "out", "agcu_eam", "07_two_phase_regions.tsv"))
    a = ap.parse_args()
    {"prepare": lambda: prepare(a.smoke), "analyse": analyse, "rkgap": lambda: rkgap(a.regions)}[a.cmd]()
