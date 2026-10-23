"""Integration example 1: Al-Li EAM free energies (pyiron potentials-workshop-2022
tutorial_2, recomputed on 2026-10-21, see pyiron-examples/workshop2022-phase-diagram/)
through ftphase stages 04A -> 05 -> 06 -> 07.

Two configurational treatments are compared:
  (a) 'tutorial': ideal mixing on all sites for fcc and B32 (what the tutorial and
      Menon et al. 2024 do; workflow section 4 warns against it for B32);
  (b) 'sublattice': ideal mixing for fcc, two-sublattice anti-site model for B32
      (Al on the Li sublattice only, a_s = 1/2), eq. (E10).
The liquid comes from calphy's UFM reference and already contains the mixing
statistics of the liquid: no term is added.

Outputs in examples/out_alli_eam/: free-energy tables, two-phase regions, T-x
plots, invariant brackets, error sensitivity, calphy-PhaseDiagram cross-check.
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TSV = os.path.join(ROOT, "pyiron-examples", "workshop2022-phase-diagram", "analysis", "free_energies.tsv")
OUT = os.path.join(HERE, "out_alli_eam")
os.makedirs(OUT, exist_ok=True)

from ftphase.records import FreeEnergyTable
from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table, to_calphy_phase_diagram, fit_residuals
from ftphase.configurational import b32_antisite_site_fractions
from ftphase.diagram import scan, invariants, sensitivity, plot_tx, write_records

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_table():
    raw = pd.read_csv(TSV, sep="\t")
    rows = []
    for r in raw.itertuples():
        for T, col in ((800.0, "F_800K_eV_per_atom"), (900.0, "F_900K"), (1000.0, "F_1000K")):
            ph = {"fcc": "fcc", "lqd": "liquid", "alli": "B32", "liquid": "liquid", "b32": "B32"}.get(r.phase, r.phase)
            rows.append({
                "phase": ph, "kind": "solution", "x": float(r.x_actual), "T": T, "P_GPa": 0.0,
                "G": float(getattr(r, col)), "G_err": 0.002,  # calphy ts reports error=0 for 1 iteration; 2 meV is a conservative estimate from fe/ts differences in calphy-examples
                "V": np.nan, "model": "AlLi.eam.fs (atomicrex, workshop 2022)",
                "reference_state": "absolute EAM energy (calphy)",
                "method": "calphy ts 800-1000 K, Einstein (solid) / UFM (liquid), 5000+5000 steps, classical",
                "config_entropy": "liquid-ti" if ph == "liquid" else "none", "quantum": "classical",
                "n_atoms": 256 if ph != "B32" else 432, "source": "pyiron-examples/workshop2022-phase-diagram",
            })
    return FreeEnergyTable.from_rows(rows, {"origin": TSV})


def run(label, table, b32_model, fit="poly"):
    if b32_model == "ideal":
        t = add_configurational_term(table, "fcc", "ideal")
        t = add_configurational_term(t, "B32", "ideal")
    else:
        t = add_configurational_term(table, "fcc", "ideal")
        t = add_configurational_term(t, "B32", "sublattice", site_model=b32_antisite_site_fractions)
    probs = t.check()
    assert not probs, probs
    t.to_tsv(os.path.join(OUT, f"table_{label}.tsv"))
    Ts = np.arange(800.0, 1000.01, 2.0)
    ti = interpolate_T(t, Ts)
    # B32 data exist only for x <= 0.5: treat as limited-range phase (no extrapolation)
    df = ti.df.copy(); df.loc[df.phase == "B32", "kind"] = "limited"
    ti = FreeEnergyTable.from_dataframe(df, ti.meta)
    builder = builder_from_table(ti, fit=fit, poly_order=3)  # 'poly' = cubic as in the tutorial; 'spline' = exact interpolation
    resid = fit_residuals(builder, 800.0)
    print(f"[{label}] fit residuals at 800 K:\n", resid.round(5).to_string(index=False))
    resid.to_csv(os.path.join(OUT, f"fit_residuals_{label}.tsv"), sep="\t", index=False)
    reg = scan(builder, Ts)
    inv = invariants(reg)
    write_records(os.path.join(OUT, f"two_phase_{label}.tsv"), reg, {"label": label, "fit": "poly3", "b32_config": b32_model, "T_step": 2.0})
    inv.to_csv(os.path.join(OUT, f"invariants_{label}.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Li", dT=2.0)
    ax.set_xlim(0, 0.55); ax.set_title(f"Al-Li EAM (workshop), B32 config = {b32_model}")
    ax.figure.savefig(os.path.join(OUT, f"phase_diagram_{label}.png"), dpi=150, bbox_inches="tight"); plt.close(ax.figure)
    # error sensitivity: 2 meV/atom offsets per phase, 20 samples
    sens = sensitivity(builder, Ts[::5], {"fcc": 0.002, "B32": 0.002, "liquid": 0.002}, n_samples=20, rng=0)
    sens.table.to_csv(os.path.join(OUT, f"sensitivity_{label}.tsv"), sep="\t", index=False)
    return t, reg, inv, sens


def eutectic_from(inv, reg):
    """Lowest T at which the liquid takes part in a coexistence."""
    liq = reg[(reg.phase_a == "liquid") | (reg.phase_b == "liquid")]
    if liq.empty:
        return None
    Tm = liq["T"].min()
    r = liq[liq["T"] == Tm]
    return Tm, r[["phase_a", "x_a", "phase_b", "x_b"]].to_dict("records")


def main():
    table = load_table()
    print("rows:", len(table), "phases:", table.phases())
    summary = []
    for label, model, fit in (("tutorial_poly3", "ideal", "poly"), ("tutorial_spline", "ideal", "spline"), ("sublattice_poly3", "sublattice", "poly"), ("sublattice_spline", "sublattice", "spline")):
        t, reg, inv, sens = run(label, table, model, fit)
        eu = eutectic_from(inv, reg)
        fb = reg[(reg["T"] == 800.0) & (reg.phase_a == "fcc") & (reg.phase_b == "B32")]
        summary.append({"label": label, "b32_config": model, "fit": fit, "T_liquid_first_K": eu[0] if eu else None, "segments_at_that_T": eu[1] if eu else None,
                        "fcc_B32_800K": fb[["x_a", "x_b"]].to_numpy().round(4).tolist(), "invariants": inv.to_dict("records")})
        print(f"\n== {label}: fcc+B32 at 800 K:", fb[["x_a", "x_b"]].round(4).to_dict("records"))
        print("invariants:\n", inv.to_string(index=False))
        st = sens.table
        print("sensitivity (std of boundaries, 2 meV/atom) at 800/900/1000 K:\n", st[st["T"].isin([800.0, 900.0, 1000.0])][["T", "pair", "x_a_mean", "x_a_std", "x_b_mean", "x_b_std", "n_found"]].round(4).to_string(index=False))
    # calphy PhaseDiagram cross-check (same data, calphy's own polynomial fit at each T)
    try:
        from ftphase.assemble import to_calphy_phase_diagram
        t = add_configurational_term(table, "fcc", "ideal"); t = add_configurational_term(t, "B32", "ideal")
        pdg = to_calphy_phase_diagram(t, reference_element="Li", composition_intervals={"B32": (0.0, 0.5)})
        pdg.calculate(T_range=(800, 1000), T_step=10, fit_order=3, ideal_configurational_entropy=False, calphad_surface=False)
        fig, ax = pdg.plot()
        fig.savefig(os.path.join(OUT, "calphy_phase_diagram_crosscheck.png"), dpi=150, bbox_inches="tight")
        print("\ncalphy PhaseDiagram cross-check written")
    except Exception as e:  # pragma: no cover
        print("calphy cross-check failed:", repr(e))
    pd.DataFrame(summary).to_json(os.path.join(OUT, "summary.json"), orient="records", indent=1)
    print("\nsummary:", summary)


if __name__ == "__main__":
    main()
