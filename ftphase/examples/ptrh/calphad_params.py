"""Step A of the Saengdeejing-type CALPHAD route for Pt-Rh with an MLIP (2026-11-11): fit the TDB parameters from one AiiDA run.

Follows Saengdeejing et al., npj Comput. Mater. 12, 362 (2026), Table 6 / eqs. 11-15: pure elements = SGTE unaries; fcc
solid solution = ideal mixing + Redlich-Kister excess L_k = a_k + b_k T fitted to the mixing free energy of the random
(SQS-like) cells; ordered phases = two-sublattice CEF whose mixed end-members are Neumann-Kopp sums of the pure-element
GHSER plus dG_f = dH_f - T dS_f, dH_f from the 0 K static formation energy and dS_f from the slope of the harmonic
vibrational formation free energy; liquid = ideal solution of the SGTE liquids (the paper had no liquid data).
Here every MLIP input comes from the QHA nodes of the AiiDA run (32-atom random fcc cells x_Rh 0..1, 2 configurations per
composition, and the stoichiometric ordered cells): E0 = relaxed static energy, F_vib = quantum harmonic phonopy free energy
at the 0 K volume (volume index 2 of the QHA scan, i.e. the harmonic level the paper used), so all phases share one
calculator setting.  The fit windows: a_k from E0 (0 K), b_k and dS_f from F_vib over T_fit.

    env/ftphase/bin/python ftphase/examples/ptrh/calphad_params.py aiida_txdiagram/out/ptrh_mace_mpa_0 [--T 300 1000] [--rk 2]
    -> ptrh/out/calphad_<mlip>/params.json  (then calphad_tdb.py, env/pycalphad, builds the TDB and the diagram)
"""
import argparse, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EV = 96485.33212  # J/mol per eV/atom
KB = 8.617333262e-5


def load_cells(run):
    """E0 (eV/atom) and harmonic F_vib(T) (eV/atom, quantum, at the 0 K volume) of every QHA node of the run's WorkChain."""
    from aiida import load_profile, orm
    load_profile("ftphase")
    rec = json.load(open(os.path.abspath(run) + ".pk.json"))
    wc = orm.load_node(rec["pk"])
    prep = [l.node for l in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all() if l.node.process_label == "prepare_cells" and l.node.is_finished_ok][0]
    sol_p = prep.outputs.solid_params.get_dict()
    cells = []
    for l in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all():
        n = l.node
        if n.process_label != "QhaCalculation" or not n.is_finished_ok:
            continue
        key = n.label.split()[1]; meta = sol_p[key]; arr = n.outputs.arrays; res = n.outputs.results.get_dict()
        T = arr.get_array("T"); fv = arr.get_array("f_vib"); i0 = res.get("frequency_volume_index", 2)
        fvib = fv[:, i0] if fv.shape[0] == len(T) else fv[i0]          # stored per QHA input cell (n_atoms), layout (T, volumes)
        cells.append({"key": key, "phase": meta["phase"], "x": float(meta["x"]), "config": meta["config"], "E0": float(res["E0_eV_per_atom"]),
                      "T": np.asarray(T, float), "F": np.asarray(fvib, float) / res["n_atoms"]})
    return wc.inputs.spec.get_dict(), cells


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--T", nargs=2, type=float, default=[300.0, 1000.0]); ap.add_argument("--rk", type=int, default=2)
    ap.add_argument("--tag", default=None); a = ap.parse_args()
    spec, cells = load_cells(a.run)
    tag = a.tag or os.path.basename(os.path.normpath(a.run)).replace("ptrh_", "")
    out = os.path.join(HERE, "out", f"calphad_{tag}"); os.makedirs(out, exist_ok=True)
    T = cells[0]["T"]; win = (T >= a.T[0] - 1e-6) & (T <= a.T[1] + 1e-6)
    def avg(ph, x):
        g = [c for c in cells if c["phase"] == ph and abs(c["x"] - x) < 1e-6]
        return (np.mean([c["E0"] for c in g]), np.mean([c["F"] for c in g], axis=0), len(g)) if g else (np.nan, None, 0)
    e_pt, f_pt, _ = avg("fcc", 0.0); e_rh, f_rh, _ = avg("fcc", 1.0)
    # --- fcc: dH_mix(x) from E0, dF_vib_mix(x, T) from the harmonic free energies; RK L_k = a_k + b_k T
    xs = sorted(set(c["x"] for c in cells if c["phase"] == "fcc" and 0 < c["x"] < 1))
    dH, dF = [], []
    for x in xs:
        e, f, n = avg("fcc", x); dH.append(e - (1 - x) * e_pt - x * e_rh); dF.append(f - (1 - x) * f_pt - x * f_rh)
    xx = np.array(xs); dH = np.array(dH); dF = np.array(dF)
    A = np.array([[x * (1 - x) * (1 - 2 * x) ** k for k in range(a.rk + 1)] for x in xx])  # (x_Pt - x_Rh)^k = (1-2x)^k
    aH, *_ = np.linalg.lstsq(A, dH, rcond=None); rmsH = float(np.sqrt(np.mean((A @ aH - dH) ** 2)))
    # per-T excess vibrational free energy -> L_k(T), then slope b_k over the window
    Lk_T = np.array([np.linalg.lstsq(A, dF[:, i], rcond=None)[0] for i in range(len(T))])
    bk = [float(np.polyfit(T[win], Lk_T[win, k], 1)[0]) for k in range(a.rk + 1)]
    ck = [float(np.polyfit(T[win], Lk_T[win, k], 1)[1]) for k in range(a.rk + 1)]   # intercept of the vibrational part (ZPE etc.), reported, not used
    rk = [{"k": k, "a_J": float(aH[k] * EV), "b_J_per_K": float(bk[k] * EV), "vib_intercept_J": float(ck[k] * EV)} for k in range(a.rk + 1)]
    # --- ordered phases: dH_f from E0 of the stoichiometric cell, dS_f from the slope of dF_vib,f over the window
    comp = {}
    for ph, x in (("Pt3Rh", 0.25), ("PtRh", 0.5), ("PtRh3", 0.75)):
        e, f, n = avg(ph, x)
        if n == 0:
            continue
        dHf = e - (1 - x) * e_pt - x * e_rh; dFf = f - (1 - x) * f_pt - x * f_rh
        b, c = np.polyfit(T[win], dFf[win], 1)
        comp[ph] = {"x_Rh": x, "dH_f_eV": float(dHf), "a_J": float(dHf * EV), "b_J_per_K": float(b * EV), "dS_f_kB": float(-b / KB), "vib_intercept_meV": float(c * 1000),
                    "dF_vib_f_meV_at": {str(int(t)): float(dFf[i] * 1000) for i, t in enumerate(T) if int(t) in (0, 300, 600, 1000)},
                    "random_fcc_dH_mix_meV": float(np.interp(x, xx, dH) * 1000)}
    res = {"run": os.path.abspath(a.run), "model": spec.get("model", ""), "T_fit": a.T, "rk_order": a.rk,
           "fcc": {"xs": xs, "dH_mix_meV": (dH * 1000).tolist(), "RK": rk, "rms_dH_meV": rmsH * 1000,
                   "dF_vib_mix_meV_300K": (dF[:, int(np.argmin(abs(T - 300)))] * 1000).tolist(), "dF_vib_mix_meV_1000K": (dF[:, int(np.argmin(abs(T - 1000)))] * 1000).tolist()},
           "ordered": comp, "E0_Pt_eV": e_pt, "E0_Rh_eV": e_rh,
           "notes": "L_k = a_k + b_k T in J/mol of atoms, Redlich-Kister in (x_Pt - x_Rh)^k; a_k from the 0 K static E0 of the 32-atom random cells (2 configurations averaged), "
                    "b_k from the slope of the excess quantum-harmonic F_vib over T_fit; ordered phases dG_f = a + b T relative to fcc Pt / fcc Rh of the same MLIP "
                    "(a = 0 K static formation energy, b = -dS_f from the harmonic F_vib slope); harmonic level = phonopy at the 0 K volume (QHA volume index 2)"}
    json.dump(res, open(os.path.join(out, "params.json"), "w"), indent=1)
    print("fcc dH_mix (meV):", [(x, round(h * 1000, 1)) for x, h in zip(xs, dH)], "rms", round(rmsH * 1000, 2))
    print("fcc RK:", [(r["k"], round(r["a_J"]), round(r["b_J_per_K"], 2)) for r in rk])
    print("fcc dF_vib_mix 300 K:", np.round(res["fcc"]["dF_vib_mix_meV_300K"], 1).tolist()); print("            1000 K:", np.round(res["fcc"]["dF_vib_mix_meV_1000K"], 1).tolist())
    for ph, c in comp.items():
        print(ph, "dH_f %.1f meV (random fcc %.1f), dS_f %.3f k_B, b %.2f J/mol/K, dF_vib_f:" % (c["dH_f_eV"] * 1000, c["random_fcc_dH_mix_meV"], c["dS_f_kB"], c["b_J_per_K"]), c["dF_vib_f_meV_at"])
    print("->", out)


if __name__ == "__main__":
    main()
