"""Integration example 3: stages 03B -> 04B -> 05 -> 06 (degenerate, pure Al) with
the Al-Li ACE potential.

Inputs
* calphy reversible-scaling runs written by ftphase.calphy_io and submitted to
  Slurm from examples/calphy_ace/ (fcc Al 256 atoms, solid: Einstein crystal
  reference; liquid: UFM reference; 800-1000 K; classical);
* the QHA free energy of fcc Al from examples/alli_ace_validate_qha.py
  (phonopy, quantum) and its phonon frequencies at the equilibrium volume.

Three melting points of ACE-Al are compared:
  (a) calphy solid vs calphy liquid              -- both classical (consistent);
  (b) QHA solid vs calphy liquid                 -- quantum vs classical (inconsistent, workflow 04B);
  (c) QHA solid lowered by dF = F_q - F_cl (harmonic) vs calphy liquid -- made consistent.
Experiment: 933.5 K.  The ACE potential's own value is whatever (a) gives; (b)-(a)
is the size of the mistake one makes by mixing quantum solids with classical liquids.
"""

import glob
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(HERE, "calphy_ace")
QHA = os.path.join(HERE, "out_alli_ace")
OUT = os.path.join(HERE, "out_alli_ace")

from ftphase.calphy_io import read_calphy_results
from ftphase.records import FreeEnergyTable
from ftphase.quantum import quantum_minus_classical
from ftphase.assemble import interpolate_T


def crossing(T, dG):
    """First sign change of dG(T) = G_solid - G_liquid, linear interpolation."""
    s = np.sign(dG)
    idx = np.where(np.diff(s) != 0)[0]
    if idx.size == 0:
        return None
    i = idx[0]
    return float(T[i] - dG[i] * (T[i + 1] - T[i]) / (dG[i + 1] - dG[i]))


def main():
    cal = read_calphy_results(CAL, reference_element="Li", model="AlLi-6gen-18May.yace (ACE)", source_prefix="examples/calphy_ace/")
    cal.to_tsv(os.path.join(OUT, "calphy_ace_free_energies.tsv"))
    df = cal.df
    print(df.groupby(["phase", "x", "config_entropy"]).agg(T_min=("T", "min"), T_max=("T", "max"), n=("T", "size"), G_err_max=("G_err", "max")).to_string())
    sol = df[(df.phase.str.startswith("fcc")) & np.isclose(df.x, 0.0)].sort_values("T")
    liq = df[(df.phase.str.startswith("lqd")) & np.isclose(df.x, 0.0)].sort_values("T")
    if sol.empty or liq.empty:
        raise SystemExit("calphy results for pure Al not complete yet")
    T = np.arange(max(sol["T"].min(), liq["T"].min()), min(sol["T"].max(), liq["T"].max()) + 1e-9, 1.0)
    Gs = np.interp(T, sol["T"], sol["G"]); Gl = np.interp(T, liq["T"], liq["G"])
    res = {"Tm_calphy_classical_K": crossing(T, Gs - Gl)}
    # QHA solid (quantum) and harmonic correction
    qha = FreeEnergyTable.from_tsv(os.path.join(QHA, "qha_free_energies.tsv")).subset(phase="fcc-Al")
    fr = np.load(os.path.join(QHA, "frequencies_fcc-Al_scale1.npz"))
    Gq = np.interp(T, qha.df["T"], qha.df["G"])
    dF = quantum_minus_classical(fr["hw_eV"], T, weights=fr["weights"]) / int(fr["n_atoms"])
    res["Tm_QHA_quantum_vs_classical_liquid_K"] = crossing(T, Gq - Gl)
    res["Tm_QHA_lowered_to_classical_vs_liquid_K"] = crossing(T, (Gq - dF) - Gl)
    res["dF_quantum_minus_classical_meV_per_atom_at_900K"] = float(np.interp(900.0, T, dF) * 1000)
    # how far apart are the two solid routes (QHA vs calphy Einstein TI) at 900 K, after the correction?
    res["G_solid_QHA_classical_minus_calphy_meV_at_900K"] = float((np.interp(900.0, T, Gq - dF) - np.interp(900.0, T, Gs)) * 1000)
    res["G_err_calphy_solid_meV"] = float(sol["G_err"].max() * 1000)
    res["G_err_calphy_liquid_meV"] = float(liq["G_err"].max() * 1000)
    res["T_range_K"] = [float(T[0]), float(T[-1])]
    # x = 0.1 solid/liquid pair, if present: mixing free energies relative to pure Al, same classical level
    s1 = df[(df.phase.str.startswith("fcc")) & (df.x > 0.05)].sort_values("T")
    l1 = df[(df.phase.str.startswith("lqd")) & (df.x > 0.05)].sort_values("T")
    if not s1.empty and not l1.empty:
        res["x_0.1_solid_minus_liquid_meV_at_900K"] = float((np.interp(900.0, s1["T"], s1["G"]) - np.interp(900.0, l1["T"], l1["G"])) * 1000)
    with open(os.path.join(OUT, "melting_ace.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(T, (Gs - Gl) * 1000, label="calphy solid - liquid (classical)")
        ax.plot(T, (Gq - Gl) * 1000, label="QHA solid (quantum) - liquid")
        ax.plot(T, (Gq - dF - Gl) * 1000, label="QHA solid - dF (classical level) - liquid")
        ax.axhline(0, color="k", lw=0.5); ax.axvline(933.5, color="gray", ls="--", lw=0.8, label="expt. 933.5 K")
        ax.set_xlabel("T (K)"); ax.set_ylabel("G_solid - G_liquid (meV/atom)"); ax.legend(fontsize=8); ax.set_title("ACE Al melting: 03B/04B consistency")
        fig.savefig(os.path.join(OUT, "melting_ace.png"), dpi=150, bbox_inches="tight")
    except Exception as e:  # pragma: no cover
        print("plot failed", e)


if __name__ == "__main__":
    main()
