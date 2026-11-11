"""Route 1: CALPHAD phase diagrams from ORCHID-Diagrams (SGTE binary collection, Hallstedt 2025) next to the MLIP runs.

ORCHID-Diagrams (10.5281/zenodo.23735859) holds, for every TDB of the SGTE binary collection, the phase boundaries that
pycalphad 0.11.2 computed (``regions``: pairs of boundary curves of each two-phase field, ``invariants``: three-phase
tie-lines).  The TDB files themselves are not redistributed (they are the CC BY 4.0 supplement of Hallstedt, Calphad 89
(2025) 102833), so this script draws the diagrams from the stored boundaries.

    ./env/ftphase/bin/python -I ftphase/examples/orchid_calphad/sgte_diagrams.py [--data DIR] [--out DIR]

Outputs (``out/``):
  sgte_<sys>.png        every assessment of the system in ORCHID-Diagrams, two-phase fields coloured, invariants as bars
  overlay_<sys>.png     the project's MLIP/EAM T-x diagrams (07_two_phase_regions.tsv) with the reference assessment's
                        boundaries (black) and invariants (dashed) on top
  sgte_invariants.tsv   invariants of all assessments (T, phases, compositions)
  REPORT.md             assessment list, reference invariants and the MLIP invariants in the same window
"""

import argparse
import glob
import json
import os
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EX = os.path.join(PROJECT, "ftphase", "examples")
AT = os.path.join(EX, "aiida_txdiagram", "out")
DATA = os.path.join(PROJECT, "data", "orchid-v2026.10", "phase-diagrams", "orchid-phase-diagrams-v2026.10", "phase-diagrams", "sgte")

# x of our runs = x of the second element; ORCHID x_component is the same (LI, NI, CU).
SYSTEMS = OrderedDict(
    alli=dict(
        prefix="AlLi", xlabel="x_Li", ref="AlLi-20Lon", title="Al-Li",
        panel_T=(300, 1100), overlay_T=(300, 1110), overlay_x=(0, 1.0),
        runs=[("ACE (aiida, x<=0.5)", os.path.join(AT, "alli_ace_m6")), ("ACE full range (example 6)", os.path.join(EX, "alli_ace_txdiagram", "out_full")),
              ("GRACE-FS-OAM", os.path.join(AT, "alli_grace_fs")), ("GRACE-1L-OMAT", os.path.join(AT, "alli_grace_1l")),
              ("GRACE-2L-OMAT", os.path.join(AT, "alli_grace_2l")), ("SevenNet-0", os.path.join(AT, "alli_sevenn_0")),
              ("SevenNet-MF-ompa", os.path.join(AT, "alli_sevenn_mf_ompa")), ("MACE-MPA-0", os.path.join(AT, "alli_mace_mpa_0")),
              ("MatterSim-v1-1M", os.path.join(AT, "alli_mattersim_1m")), ("MatterSim-v1-5M", os.path.join(AT, "alli_mattersim_5m")),
              ("NequIP-OAM-M", os.path.join(AT, "alli_nequip_oam_m")), ("NequIP-OAM-S", os.path.join(AT, "alli_nequip_oam_s")),
              ("DPA4-Plus-OMat24", os.path.join(AT, "alli_dpa4_plus_omat24"))],
    ),
    nial=dict(
        prefix="AlNi", xlabel="x_Ni", ref="AlNi-01Dup-4sl", title="Ni-Al (x = x_Ni)",
        panel_T=(600, 2000), overlay_T=(900, 2010), overlay_x=(0, 1.0),
        runs=[("EAM Mishin 2009 (stage 5, solid TI)", os.path.join(EX, "nial_eam", "out_mygardenx1_stage5")),
              ("GRACE-FS-OAM (QHA solids)", os.path.join(AT, "nial_grace_fs")), ("GRACE-FS-OAM (+TI ends)", os.path.join(AT, "nial_grace_fs_ti")),
              ("GRACE-1L-OMAT (QHA solids)", os.path.join(AT, "nial_grace_1l")), ("GRACE-1L-OMAT (+TI ends)", os.path.join(AT, "nial_grace_1l_ti")),
              ("SevenNet-0 (QHA solids)", os.path.join(AT, "nial_sevenn_0")), ("SevenNet-0 (+TI ends)", os.path.join(AT, "nial_sevenn_0_ti"))],
    ),
    ptrh=dict(   # 2026-11-10: ORCHID-Diagrams has 3 SGTE fcc+liquid assessments and no literature values for Pt-Rh (npj_ptrh/COMPARISON.md)
        prefix="PtRh", xlabel="x_Rh", ref="PtRh-98Jac", title="Pt-Rh (x = x_Rh)",
        panel_T=(1700, 2400), overlay_T=(1700, 2410), overlay_x=(0, 1.0),
        runs=[("GRACE-2L-OMAT (QHA solids, liquid 1910-2400 K)", os.path.join(AT, "ptrh_grace_2l")), ("NequIP-OAM-M", os.path.join(AT, "ptrh_nequip_oam_m")),
              ("MACE-MPA-0", os.path.join(AT, "ptrh_mace_mpa_0")), ("SevenNet-MF-ompa", os.path.join(AT, "ptrh_sevenn_mf_ompa")),
              ("GRACE-2L-OMAT (+2048-atom TI ends)", os.path.join(AT, "ptrh_grace_2l_ti")), ("NequIP-OAM-M (+TI ends)", os.path.join(AT, "ptrh_nequip_oam_m_ti")),
              ("MACE-MPA-0 (+TI ends)", os.path.join(AT, "ptrh_mace_mpa_0_ti"))],
    ),
    agcu=dict(
        prefix="AgCu", xlabel="x_Cu", ref="AgCu-04Wit-LB", title="Ag-Cu",
        panel_T=(600, 1500), overlay_T=(1000, 1410), overlay_x=(0, 1.0),
        runs=[("EAM WMH 2006 (2048-atom solid TI)", os.path.join(AT, "agcu_eam_2048")), ("EAM WMH 2006 (256-atom TI)", os.path.join(AT, "agcu_eam")),
              ("GRACE-FS-OAM (QHA)", os.path.join(AT, "agcu_grace_fs")), ("GRACE-FS-OAM (+TI ends)", os.path.join(AT, "agcu_grace_fs_ti")),
              ("GRACE-1L-OMAT (QHA)", os.path.join(AT, "agcu_grace_1l")), ("GRACE-1L-OMAT (+TI ends)", os.path.join(AT, "agcu_grace_1l_ti")),
              ("SevenNet-0 (QHA)", os.path.join(AT, "agcu_sevenn_0")), ("SevenNet-0 (+TI ends)", os.path.join(AT, "agcu_sevenn_0_ti"))],
    ),
)

PALETTE = ["#5b9bd5", "#70ad47", "#f4a259", "#a05195", "#d45087", "#888888", "#2f4b7c", "#ffa600", "#665191", "#003f5c",
           "#8dd3c7", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5"]


def norm(name):
    """Strip pycalphad composition-set suffixes (FCC_A1#2 -> FCC_A1)."""
    return name.split("#")[0]


def load_sgte(prefix, data=DATA):
    out = []
    for f in sorted(glob.glob(os.path.join(data, prefix + "-*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d["name"] = os.path.basename(f)[:-5]
        out.append(d)
    return out


def draw_sgte(ax, d, T_window, colors, seen):
    for region in d.get("regions") or []:
        if len(region) != 2:
            continue
        a, b = region
        pair = "+".join(sorted([norm(a["phase"]), norm(b["phase"])]))
        c = colors.setdefault(pair, PALETTE[len(colors) % len(PALETTE)])
        n = min(len(a["T"]), len(b["T"]))
        h = ax.fill_betweenx(a["T"][:n], a["x"][:n], b["x"][:n], color=c, lw=0, alpha=0.9)
        seen.setdefault(pair, h)
    for inv in d.get("invariants") or []:
        xs = [p["x"] for p in inv["points"]]
        ax.plot([min(xs), max(xs)], [inv["T"]] * 2, color="k", lw=1.0)
    ax.set_ylim(*T_window)
    ax.set_xlim(0, 1)


def draw_run(ax, run_dir, colors, seen, T_window):
    f = os.path.join(run_dir, "07_two_phase_regions.tsv")
    if not os.path.exists(f):
        ax.text(0.5, 0.5, "no 07 output", ha="center", transform=ax.transAxes)
        return None
    r = pd.read_csv(f, sep="\t"); T_liq = float(r["T"].min())
    low = os.path.join(run_dir, "lowT", "07_two_phase_regions.tsv")   # solids-only re-assembly below the liquid window (assemble_solids_lowT.py, 2026-11-10)
    if os.path.exists(low):
        lr = pd.read_csv(low, sep="\t")
        r = pd.concat([lr[lr["T"] < r["T"].min() - 1e-6], r], ignore_index=True)
    lis = os.path.join(run_dir.rstrip("/") + "_liside_solid", "07_two_phase_regions.tsv")   # Li-side solids (bcc Li series, Al2Li3, Al4Li9) from the --li-side --solid-only WorkChain (2026-11-11)
    if os.path.exists(lis):
        ls = pd.read_csv(lis, sep="\t")
        ls = ls[(ls["T"] < T_liq - 1e-6) & (ls[["x_a", "x_b"]].min(axis=1) >= 0.45)]
        r = pd.concat([ls, r], ignore_index=True)
    r = r[r.phase_a != r.phase_b]
    steps = r["T"].diff().abs()
    dT = float(steps[steps > 0].min()) if (steps > 0).any() else 10.0
    for _, row in r.iterrows():
        pair = "+".join(sorted([row.phase_a, row.phase_b]))
        c = colors.setdefault(pair, PALETTE[len(colors) % len(PALETTE)])
        h = ax.fill_between([min(row.x_a, row.x_b), max(row.x_a, row.x_b)], row["T"] - dT / 2, row["T"] + dT / 2, color=c, lw=0)
        seen.setdefault(pair, h)
    ax.set_ylim(*T_window)
    return r


def draw_ref_boundaries(ax, d):
    for region in d.get("regions") or []:
        for side in region:
            ax.plot(side["x"], side["T"], color="k", lw=0.9)
    for inv in d.get("invariants") or []:
        xs = [p["x"] for p in inv["points"]]
        ax.plot([min(xs), max(xs)], [inv["T"]] * 2, color="k", lw=0.9, ls="--")


def invariants_rows(d, system):
    rows = []
    for inv in d.get("invariants") or []:
        pts = sorted(inv["points"], key=lambda p: p["x"])
        rows.append(dict(system=system, assessment=d["name"], T_K=round(inv["T"], 1),
                         phases="+".join(norm(p["phase"]) for p in pts), x=", ".join(f"{p['x']:.3f}" for p in pts),
                         source=(d.get("original_source") or {}).get("citation", "")))
    return rows


def run_invariants(run_dir):
    f = os.path.join(run_dir, "07_invariants.tsv")
    if not os.path.exists(f):
        return None
    return pd.read_csv(f, sep="\t")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--systems", nargs="*", default=list(SYSTEMS))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    inv_rows = []
    report = ["# 経路 1: ORCHID-Diagrams（SGTE binary collection, Hallstedt 2025）の CALPHAD 相図と MLIP の比較", "",
              f"データ: `{args.data}` (ORCHID-Diagrams 10.5281/zenodo.23735859, pycalphad 0.11.2 で計算された境界; TDB 本体は非同梱)。",
              "各系の全評価を `sgte_<sys>.png` に、参照評価の境界を MLIP の T-x 図に重ねたものを `overlay_<sys>.png` に描いた。", ""]
    for sys_key in args.systems:
        S = SYSTEMS[sys_key]
        diagrams = load_sgte(S["prefix"], args.data)
        ok = [d for d in diagrams if d.get("status") == "ok"]
        report += [f"## {S['title']}", "", f"ORCHID-Diagrams の評価 {len(diagrams)} 件（計算成功 {len(ok)}）。参照評価: `{S['ref']}`。", "",
                   "| assessment | status | phases | n_inv | source |", "|---|---|---|---|---|"]
        for d in diagrams:
            report.append(f"| {d['name']} | {d.get('status')} | {', '.join(d.get('phases') or [])} | {len(d.get('invariants') or [])} | "
                          f"{(d.get('original_source') or {}).get('citation', (d.get('error') or '')[:80])} |")
        report.append("")
        # --- figure 1: all assessments
        ncol = 4
        nrow = (len(ok) + ncol) // ncol
        fig, axes = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 3.4 * nrow), squeeze=False)
        colors, seen = {}, {}
        for ax, d in zip(axes.flat, ok):
            draw_sgte(ax, d, S["panel_T"], colors, seen)
            ax.set(title=d["name"] + (" (ref)" if d["name"] == S["ref"] else ""), xlabel=S["xlabel"], ylabel="T (K)")
        tail = list(axes.flat)[len(ok):]
        for ax in tail:
            ax.axis("off")
        if tail:
            tail[0].legend(seen.values(), seen.keys(), loc="upper left", fontsize=7, ncol=2)
            tail[0].text(0.02, 0.02, f"{S['title']}: SGTE binary collection assessments\n(pycalphad boundaries stored in ORCHID-Diagrams)\nblack bars: invariants",
                         fontsize=8, transform=tail[0].transAxes)
        fig.tight_layout()
        p1 = os.path.join(args.out, f"sgte_{sys_key}.png")
        fig.savefig(p1, dpi=110)
        plt.close(fig)
        # --- figure 2: overlay
        ref = next((d for d in ok if d["name"] == S["ref"]), None)
        runs = S["runs"]
        n = len(runs) + 1
        ncol = 4
        nrow = (n + ncol - 1) // ncol
        fig, axes = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 3.4 * nrow), squeeze=False)
        colors, seen = {}, {}
        ax0 = axes.flat[0]
        if ref is not None:
            draw_sgte(ax0, ref, S["overlay_T"], colors, seen)
        ax0.set(title=f"CALPHAD {S['ref']}", xlabel=S["xlabel"], ylabel="T (K)", xlim=S["overlay_x"])
        for ax, (label, run_dir) in zip(list(axes.flat)[1:], runs):
            draw_run(ax, run_dir, colors, seen, S["overlay_T"])
            if ref is not None:
                draw_ref_boundaries(ax, ref)
            ax.set(title=label, xlabel=S["xlabel"], ylabel="T (K)", xlim=S["overlay_x"])
        for ax in list(axes.flat)[n:]:
            ax.axis("off")
        fig.legend(seen.values(), seen.keys(), loc="lower right", fontsize=7, ncol=3, title="two-phase fields (CALPHAD names / run names)")
        fig.suptitle(f"{S['title']}: MLIP/EAM T-x diagrams with the CALPHAD boundaries of {S['ref']} (black; dashed = invariants)", fontsize=11)
        fig.tight_layout(rect=(0, 0.04, 1, 0.97))
        p2 = os.path.join(args.out, f"overlay_{sys_key}.png")
        fig.savefig(p2, dpi=110)
        plt.close(fig)
        report += [f"図: `{os.path.basename(p1)}`, `{os.path.basename(p2)}`", ""]
        # --- invariants
        for d in ok:
            inv_rows += invariants_rows(d, sys_key)
        if ref is not None:
            lo, hi = S["overlay_T"]
            report += [f"### 参照評価 `{S['ref']}` の不変反応（{lo}-{hi} K）", "", "| T (K) | phases (x ascending) | x |", "|---|---|---|"]
            seen_inv = set()
            for row in invariants_rows(ref, sys_key):
                key = (row["T_K"], row["phases"])
                if key in seen_inv or not (lo <= row["T_K"] <= hi):
                    continue
                seen_inv.add(key)
                report.append(f"| {row['T_K']} | {row['phases']} | {row['x']} |")
            report.append("")
            # spread over assessments: same-T invariants of the other assessments listed by phases
            report += ["評価間のばらつき（全評価の不変反応、同じ温度窓）:", "", "| assessment | T (K) | phases |", "|---|---|---|"]
            for d in ok:
                done = set()
                for row in invariants_rows(d, sys_key):
                    key = (row["T_K"], row["phases"])
                    if key in done or not (lo <= row["T_K"] <= hi):
                        continue
                    done.add(key)
                    report.append(f"| {d['name']} | {row['T_K']} | {row['phases']} |")
            report.append("")
        report += ["### MLIP/EAM run の不変反応（07_invariants.tsv、同相区間の出入りを除く）", "", "| run | T bracket (K) | changed pairs |", "|---|---|---|"]
        for label, run_dir in runs:
            inv = run_invariants(run_dir)
            if inv is None:
                report.append(f"| {label} | - | no 07_invariants.tsv |")
                continue
            for _, row in inv.iterrows():
                txt = str(row.get("pairs_changed", row.get("pairs", "")))
                if "liquid+liquid" in txt or "fcc+fcc" in txt or "fccAg+fccAg" in txt or "fccCu+fccCu" in txt:
                    pass
                report.append(f"| {label} | {row.get('T_low', '')}-{row.get('T_high', '')} | {txt[:160]} |")
        report.append("")
    pd.DataFrame(inv_rows).to_csv(os.path.join(args.out, "sgte_invariants.tsv"), sep="\t", index=False)
    with open(os.path.join(args.out, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(report))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
