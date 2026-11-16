"""Solids-only assembly of example 6 (ACE Al-Li, full range) below its liquid window, 300 K upward.

    ./env/ftphase/bin/python ftphase/examples/alli_ace_txdiagram/assemble_lowT_full.py [--T 300 640] [--step 10]

The main assembly (pipeline_full.py assemble) keeps only temperatures where the liquid covers 0 <= x_Li <= 1 (650 K and above), although
the QHA solids of the same table (out_full/05_free_energies.tsv, classical level, configurational terms already added) go down to 0 K.
This drops the liquid rows and scans the solid phases alone with the same fits (fcc, bcc: cubic excess over ideal mixing; B32: spline;
Al3Li, Al2Li3, Al4Li9: point phases).  Output out_full/lowT/07_two_phase_regions.tsv (+ invariants, figure), which
orchid_calphad/sgte_diagrams.py merges below the liquid window.  Caveat: without a liquid the Li side above the Li melting point
(453 K in the assessment) is a metastable-solids picture."""
import argparse, os
import numpy as np


def main():
    import matplotlib; matplotlib.use("Agg")
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import interpolate_T, builder_from_table
    from ftphase.diagram import scan, invariants, plot_tx, write_records
    ap = argparse.ArgumentParser(); ap.add_argument("--T", nargs=2, type=float, default=[300.0, 640.0]); ap.add_argument("--step", type=float, default=10.0); a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__)); src = os.path.join(here, "out_full"); out = os.path.join(src, "lowT"); os.makedirs(out, exist_ok=True)
    tab = FreeEnergyTable.from_tsv(os.path.join(src, "05_free_energies.tsv")); df = tab.df[tab.df.phase != "liquid"]
    Ts = np.arange(a.T[0], a.T[1] + 1e-6, a.step); ti = interpolate_T(FreeEnergyTable.from_dataframe(df, tab.meta), Ts)
    FITS = {"fcc": "poly", "bcc": "poly", "B32": "spline"}; HULL = {"min_width": 0.005, "gap_tol": 2.5}
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3)
    reg = scan(builder, Ts, **HULL); inv = invariants(reg)
    write_records(os.path.join(out, "07_two_phase_regions.tsv"), reg, {"example": "alli_ace_txdiagram_full, solids only below the liquid window", "fit": str(FITS), "hull": str(HULL),
                                                                       "T_step": a.step, "level": "classical (QHA lowered by F_q-F_cl)", "solids": "QHA, 64-atom SQS (fcc, bcc), B32 16-atom, point phases"})
    inv.to_csv(os.path.join(out, "07_invariants.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Li", dT=a.step); ax.set_xlim(0, 1); ax.set_title("ACE Al-Li example 6, solids only (no liquid computed below 650 K)", fontsize=9)
    ax.figure.savefig(os.path.join(out, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
    for T in (300.0, 400.0, 500.0, 600.0, 640.0):
        r = reg[np.isclose(reg["T"], T)]; print(int(T), "; ".join(f'{p.phase_a}({p.x_a:.3f})+{p.phase_b}({p.x_b:.3f})' for p in r.itertuples()))
    print(inv.to_string(index=False)[:1500])


if __name__ == "__main__":
    main()
