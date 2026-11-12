"""Splice the extended-B2 solid-TI rows (run <base>_b2ext_solid, assembled by mlip_solids_ti.py assemble -> <base>_b2ext_solid_ti) into the
stage-2 table of the base MLIP run (<base>_ti) and re-assemble with the Wagner-Schottky model (reassemble_ws.py).
    python merge_b2ext.py nial_grace_1l   -> aiida_txdiagram/out/nial_grace_1l_b2ext_merged/{05_free_energies.tsv, ws/}
"""
import os, shutil, subprocess, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "aiida_txdiagram", "out"); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
base = sys.argv[1]
a = pd.read_csv(os.path.join(OUT, base + "_ti", "05_free_energies.tsv"), sep="\t"); b = pd.read_csv(os.path.join(OUT, base + "_b2ext_solid_ti", "05_free_energies.tsv"), sep="\t")
ti_b2 = b[(b.phase == "B2") & b.method.str.contains("calphy", case=False)]
print("base table rows", len(a), "| extended B2 TI rows", len(ti_b2), "x:", sorted(ti_b2.x.round(4).unique()))
m = pd.concat([a, ti_b2], ignore_index=True)
dst = os.path.join(OUT, base + "_b2ext_merged")
l12 = os.path.join(OUT, base + "_l12ext_solid_ti", "05_free_energies.tsv")
if os.path.exists(l12) and "--no-l12" not in sys.argv:   # 2026-11-12: extended L1_2 anti-site cells (Ni->Al 2-4, Al->Ni 2-3; 2048-atom TI)
    c = pd.read_csv(l12, sep="\t"); ti_l12 = c[(c.phase == "L12") & c.method.str.contains("calphy", case=False)]
    print("extended L12 TI rows", len(ti_l12), "x:", sorted(ti_l12.x.round(4).unique()))
    m = pd.concat([m, ti_l12], ignore_index=True); dst = os.path.join(OUT, base + "_b2l12ext_merged")
os.makedirs(dst, exist_ok=True)
m.to_csv(os.path.join(dst, "05_free_energies.tsv"), sep="\t", index=False)
for f in ("05_free_energies.tsv.meta.json",):
    if os.path.exists(os.path.join(OUT, base + "_ti", f)):
        shutil.copy(os.path.join(OUT, base + "_ti", f), dst)
py = os.path.join(ROOT, "env", "ftphase", "bin", "python")
subprocess.run([py, os.path.join(HERE, "reassemble_ws.py"), "--in", dst, "--l12-sites", "32", "--title", f"{base} Ni-Al: solids TI + extended B2 defect cells (vacancies 4-7, anti-sites 8-10), Wagner-Schottky"], check=True)
