"""Ni-Al / Ag-Cu panels from 100 K: the stage-2 assemblies (solid TI + calphy liquid; EAM references) plus the solids-only
low-T re-assemblies below their grids (assemble_solids_lowT.py -> <run>/lowT; QHA cells only, classical level).
    python panels_nial_agcu_full.py  -> out/mlip_compare_nial_agcu/panels_ti_full_lowT.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
ROWS = [("Ni-Al", "x_Ni", (100, 2000), [("EAM Mishin 2009 (solid TI; low T not sampled)", os.path.join(HERE, "..", "nial_eam", "out_mygardenx1_stage5")),
                                        ("GRACE-FS-OAM (solid TI)", os.path.join(OUT, "nial_grace_fs_ti")), ("GRACE-1L-OMAT fp32 (solid TI)", os.path.join(OUT, "nial_grace_1l_ti")),
                                        ("SevenNet-0 (solid TI)", os.path.join(OUT, "nial_sevenn_0_ti"))]),
        ("Ag-Cu", "x_Cu", (100, 1400), [("EAM WMH 2006 (2048-atom solid TI)", os.path.join(OUT, "agcu_eam_2048")),
                                        ("GRACE-FS-OAM (solid TI)", os.path.join(OUT, "agcu_grace_fs_ti")), ("GRACE-1L-OMAT fp32 (solid TI)", os.path.join(OUT, "agcu_grace_1l_ti")),
                                        ("SevenNet-0 (solid TI)", os.path.join(OUT, "agcu_sevenn_0_ti"))])]
PAL = ["#5b9bd5", "#f4a259", "#70ad47", "#a05195", "#d45087", "#8dd3c7", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#bc80bd", "#ccebc5", "#ffa600", "#665191"]


def load(run):
    f = os.path.join(run, "07_two_phase_regions.tsv"); low = os.path.join(run, "lowT", "07_two_phase_regions.tsv")
    r = pd.read_csv(f, sep="\t") if os.path.exists(f) else pd.DataFrame(columns=["T", "phase_a", "x_a", "phase_b", "x_b"])
    if os.path.exists(low):
        lr = pd.read_csv(low, sep="\t"); r = pd.concat([lr[lr["T"] < (r["T"].min() if len(r) else 1e9) - 1e-6], r], ignore_index=True)
    keep_same = "agcu" in os.path.basename(os.path.normpath(run)).lower()   # Ag-Cu: fcc+fcc IS the miscibility gap; elsewhere same-phase rows are fit noise
    return r if keep_same else r[r.phase_a != r.phase_b]


def main():
    colors, seen = {}, {}
    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    for (sysname, xl, Tw, runs), axrow in zip(ROWS, axes):
        for ax, (label, run) in zip(axrow, runs):
            r = load(run)
            for row in r.itertuples():
                pair = "+".join(sorted([row.phase_a, row.phase_b])); c = colors.setdefault(pair, PAL[len(colors) % len(PAL)])
                h = ax.fill_between([min(row.x_a, row.x_b), max(row.x_a, row.x_b)], row.T - 5, row.T + 5, color=c, lw=0); seen.setdefault(pair, h)
            lowmax = None
            low = os.path.join(run, "lowT", "07_two_phase_regions.tsv")
            if os.path.exists(low):
                lowmax = pd.read_csv(low, sep="\t")["T"].max(); ax.axhline(lowmax + 5, color="k", lw=0.6, ls=":")
            ax.set(xlim=(0, 1), ylim=Tw, xlabel=xl, ylabel="T (K)", title=f"{sysname}: {label}", )
            ax.title.set_fontsize(9)
    fig.legend(seen.values(), seen.keys(), loc="lower center", ncol=8, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.005))
    fig.suptitle("Ni-Al (top) and Ag-Cu (bottom) from 100 K: stage-2 assembly (solid TI + calphy liquid) above the dotted line, solids-only re-assembly of the QHA cells below it "
                 "(classical level, same fits and sublattice models; EAM Ni-Al has no low-T solid data)", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96)); p = os.path.join(OUT, "mlip_compare_nial_agcu", "panels_ti_full_lowT.png"); fig.savefig(p, dpi=120); print("wrote", p)


if __name__ == "__main__":
    main()
