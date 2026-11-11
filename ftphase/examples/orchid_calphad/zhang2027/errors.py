"""Reproduce Zhang et al. 2027 Table 1 (RMSE of decomposition enthalpy / entropy vs DFT) and the parity data of Fig. S13 from the
deposit's JSON files, following notebook 05-enthalpy_entropy_error.ipynb (same temperature windows, same 'free_diff[-1]/T' entropy).
    python errors.py <deposit dir> [--methods ...] [--extra name=dir] [--out out/errors.tsv]
Extra MLIP folders (our own runs) must mirror the deposit layout <dir>/<system>/<file>.json.
"""
import argparse, glob, os, sys
import numpy as np, pandas as pd
from scipy import constants
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "benchmark"))
from benchmark.dft import DFTCompound
from pymatgen.analysis.phase_diagram import PDEntry, PhaseDiagram
from pymatgen.core import Composition

SYSTEMS = {"Al-Zn": 800, "Cu-Mg": 1000, "Cu-Pt": 1000, "Mo-Rh": 2000, "Ru-Si": 2000, "W-Re": 2000}
METHODS = ["DFT", "grace-2L-SMAX", "grace-2L-OAM-L", "SevenNet-omni", "Nequip-OAM-XL", "eSEN-uma-s-1p1", "grace-2L-MP", "ORB-v3", "Nequip-MP-L"]
EV = constants.electron_volt * constants.Avogadro


def load(folder, fn):
    for p in (os.path.join(folder, fn), os.path.join(folder, "unused", fn)):
        if os.path.exists(p):
            return DFTCompound.from_json(p)
    return None


def one_system(deposit, system, tmax, methods, extra):
    temp = np.linspace(10, tmax, 100)
    comps = {os.path.basename(f): DFTCompound.from_json(f) for f in glob.glob(os.path.join(deposit, "DFT", system, "*.json"))}
    comps = {k: c for k, c in comps.items() if c.ph_omega is not None}
    e2f = {PDEntry(Composition("".join(c.structure.symbols)).formula, c.energy_per_atom_eV * len(c.structure)): k for k, c in comps.items()}
    ph = PhaseDiagram(list(e2f)); f2e = {v: k for k, v in e2f.items()}
    ref_ele = {k.symbol: e2f[v] for k, v in ph.el_refs.items()}
    rows = []
    for m in methods:
        folder = os.path.join(extra[m] if m in extra else os.path.join(deposit, m), system)
        mc = {k: load(folder, k) for k in f2e}
        missing = [k for k, c in mc.items() if c is None or c.ph_omega is None]
        if missing:   # a structure the MLIP run lost (e.g. MACE Mo8Rh24, spglib failure): skip it and every decomposition that needs it
            print(f"{system} {m}: missing {missing} (skipped; structures depending on them are skipped too)", flush=True)
            mc = {k: c for k, c in mc.items() if c is not None and c.ph_omega is not None}
            if any(ref_ele[el] not in mc for el in ref_ele):
                continue
        for fn, c in mc.items():
            if len(c.get_composition_dict()) == 1:
                continue
            decomp0, _ = ph.get_decomp_and_phase_separation_energy(f2e[fn])
            if any(e2f[p_] not in mc for p_ in decomp0):
                continue
            def diff(parts):
                eref = sum(x * mc[k].energy_per_atom_eV for k, x in parts); fref = sum(x * mc[k].get_free_energy_per_atom(temp, include_internal_energy=False) for k, x in parts)
                dH = (c.energy_per_atom_eV - eref) * EV; dS = (c.get_free_energy_per_atom(temp, include_internal_energy=False) - fref)[-1] / temp[-1]
                return dH, dS
            Hf, Sf = diff([(ref_ele[el], x) for el, x in c.get_composition_dict().items()])
            decomp, _ = ph.get_decomp_and_phase_separation_energy(f2e[fn])
            Hd, Sd = diff([(e2f[p], x) for p, x in decomp.items()])
            rows.append(dict(system=system, structure=fn[:-5], method=m, H_form=Hf, S_form=-Sf, H_decomp=Hd, S_decomp=-Sd))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("deposit"); ap.add_argument("--methods", nargs="*", default=METHODS); ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--systems", nargs="*", default=list(SYSTEMS)); ap.add_argument("--out", default=os.path.join(HERE, "out", "errors.tsv")); a = ap.parse_args()
    extra = dict(e.split("=", 1) for e in a.extra); methods = list(a.methods) + [m for m in extra if m not in a.methods]
    df = pd.concat([one_system(a.deposit, s, SYSTEMS[s], methods, extra) for s in a.systems], ignore_index=True)
    df.to_csv(a.out, sep="\t", index=False)
    ref = df[df.method == "DFT"].set_index(["system", "structure"])
    print("\nRMSE vs DFT over all structures (notebook 05 definition: decomposition H in kJ/mol, S in J/mol/K; S here = -dF/dT at T_max)")
    summ = []
    for m in methods:
        if m == "DFT":
            continue
        d = df[df.method == m].set_index(["system", "structure"]); j = d.join(ref, rsuffix="_dft", how="inner")
        if len(j) == 0:
            continue
        rH = np.sqrt(np.mean((j.H_decomp - j.H_decomp_dft) ** 2)) / 1e3; rS = np.sqrt(np.mean((j.S_decomp - j.S_decomp_dft) ** 2))
        rHf = np.sqrt(np.mean((j.H_form - j.H_form_dft) ** 2)) / 1e3; rSf = np.sqrt(np.mean((j.S_form - j.S_form_dft) ** 2))
        summ.append((m, rH, rS, rHf, rSf, len(j))); print(f"{m:16s} dH_decomp {rH:.3f}  dS_decomp {rS:.3f}   (formation: {rHf:.3f} / {rSf:.3f}; n={len(j)})")
    pd.DataFrame(summ, columns=["method", "rmse_H_decomp_kJ", "rmse_S_decomp_J_K", "rmse_H_form_kJ", "rmse_S_form_J_K", "n"]).to_csv(a.out.replace(".tsv", "_summary.tsv"), sep="\t", index=False)


if __name__ == "__main__":
    main()
