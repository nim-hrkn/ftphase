"""Collect out_defects_mlip/*.json (nial_defects_mlip.py) and the EAM numbers into one table vs DFT literature values.
    python defects_table.py  -> out_defects_mlip/TABLE.md (printed too)
DFT references (eV): Korzhavyi et al. PRB 61, 6003 (2000) / Fu & Painter / Mishin, Mehl, Papaconstantopoulos PRB 65, 224114 (2002)
collected: Va_Ni formation (effective, vs pure elements) ~0.9-1.1 (raw vacancy ~1.0-1.3 at the stoichiometric mu), triple defect 1.0-1.3
(Mishin 2002 quotes EAM 2.9 vs DFT 1.0-1.3 is not in that paper; the DFT range is the one used in vacancy_analysis.md)."""
import glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
eam = os.path.join(HERE, "out_mygardenx1_stage5", "vacancy_analysis.md")
for f in sorted(glob.glob(os.path.join(HERE, "out_defects_mlip", "*.json"))):
    d = json.load(open(f)); r = d["raw_eV"]; fp = d["formation_vs_pure_elements_eV"]
    rows.append((d["mlip"], d["a0_B2_A"], d["E_form_B2_eV_per_atom"], r["Va_Ni"], r["Va_Al"], r["Ni_Al"], r["Al_Ni"], fp["Va_Ni"], fp["Va_Al"], fp["Ni_Al"], fp["Al_Ni"], d["triple_defect_eV"], d["schottky_pair_eV"], d["antisite_pair_eV"]))
L = ["# B2 NiAl point defects: MLIPs vs EAM vs DFT (eV; 4x4x4 = 128 sites, positions relaxed at the MLIP lattice parameter)", "",
     "raw = E(defect cell) - E(perfect cell); formation vs pure elements adds/removes the atom at its pure-fcc energy; triple defect = 2 Va_Ni + Ni_Al + 2 E_B2 (composition conserving, per formula unit removed); Schottky = Va_Ni + Va_Al + 2 E_B2.", "",
     "| MLIP | a0 (A) | E_f B2 (eV/atom) | raw Va_Ni | raw Va_Al | raw Ni_Al | raw Al_Ni | Va_Ni form. | Va_Al form. | Ni_Al form. | Al_Ni form. | triple defect | Schottky pair | antisite pair |", "|---|" + "---|" * 13]
for r in rows:
    L.append("| " + " | ".join([r[0], f"{r[1]:.3f}", f"{r[2]:+.3f}"] + [f"{v:+.2f}" for v in r[3:]]) + " |")
L += ["| EAM Mishin 2009 (vacancy_analysis.md) | 2.832 | — | — | — | — | — | 1.76 (Va_Ni, formation-like) | — | — | — | 2.82 | — | — |",
      "| DFT (literature, vacancy_analysis.md) | 2.89 | -0.70 (expt -0.61) | — | — | — | — | 0.9-1.3 | — | — | — | 1.0-1.3 | — | — |", "",
      "Reading: the Al-rich width of B2 is carried by Ni vacancies (triple defect 2 Va_Ni + Ni_Al per missing formula unit); an MLIP whose triple-defect energy is near the DFT 1.0-1.3 eV can give the experimental x_Ni ~ 0.45 at 1600 K, the EAM's 2.8 eV cannot (vacancy_analysis.md)."]
os.makedirs(os.path.join(HERE, "out_defects_mlip"), exist_ok=True); open(os.path.join(HERE, "out_defects_mlip", "TABLE.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))
