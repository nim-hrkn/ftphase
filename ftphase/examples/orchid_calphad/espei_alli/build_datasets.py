"""Assemble the ESPEI datasets for the Al-Li route-2 fit from the ORCHID release (no other data).

Sources (all CC BY 4.0, data/orchid-v2026.10/):
  espei/invariants/AL-LI          4 experimental invariant-reaction ZPF datasets (eutectic 863-875 K, B32 congruent 970 K)
  espei/assessed/AL-LI            9 handbook phase-field points (Okamoto / McAlister 1982), tag assessed_phase_diagram
  espei/derived/invariant-brackets 4 derived phase sets just above/below the printed eutectics (tag derived_bracket)
  espei/derived/liquid-stability   liquid single phase at 1020 K
  espei/dft/literature/AL-LI       HM_FORM of AL2LI3 and AL4LI9 (one copy; the release repeats them per TDB)
  literature/systems/AL-LI.json    HM_FORM of AlLi (B32): experimental -20.7 kJ/mol-atom (Long 2020 compilation) -> endmember
                                   datasets AL:LI and LI:AL of ALLI_B32 written here
  SGTE unary (Dinsdale 1991, as in ESPEI refdata)  lattice stabilities of the ALLI_B32 end members AL:AL (= bcc Al,
                                   +10083 - 4.813 T J/mol-atom) and LI:LI (= bcc Li, 0): written as HM_FORM / SM_FORM datasets

Phase names: the ORCHID files use the names of AlLi-20Lon.tdb (BCC_4SL for the B32 phase); here the B32 phase is
ALLI_B32 modelled as (AL,LI)0.5(AL,LI)0.5, so BCC_4SL is renamed.  Values are per mole of atoms, as in the ORCHID files.

    ./env/pycalphad/bin/python -I build_datasets.py [--data DIR] [--out datasets]
"""

import argparse
import glob
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(PROJECT, "data", "orchid-v2026.10")
ESPEI = os.path.join(DATA, "espei", "orchid-espei-v2026.10", "espei")
LIT = os.path.join(DATA, "literature", "orchid-literature-v2026.10", "literature", "systems", "AL-LI.json")

RENAME = {"BCC_4SL": "ALLI_B32"}


def rename_phases(d):
    d["phases"] = [RENAME.get(p, p) for p in d["phases"]]
    for cond in d["values"]:
        for entry in cond:
            entry[0] = RENAME.get(entry[0], entry[0])
    return d


def copy_zpf(src_glob, dst_dir, tag_note):
    n = 0
    for f in sorted(glob.glob(src_glob)):
        d = json.load(open(f, encoding="utf-8"))
        d = rename_phases(d)
        d["comment"] = (d.get("comment", "") + f" | route-2 copy: {tag_note}; BCC_4SL renamed ALLI_B32").strip(" |")
        json.dump(d, open(os.path.join(dst_dir, os.path.basename(f)), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        n += 1
    return n


def b32_hm_form(lit_path):
    """Experimental HM_FORM of AlLi (B32) from the ORCHID literature values (accepted, experimental)."""
    recs = json.load(open(lit_path, encoding="utf-8"))["records"]
    vals = []
    for r in recs:
        if r.get("property") != "HM_FORM" or r.get("evidence_class") != "experimental":
            continue
        if not r.get("flags", {}).get("extraction_accepted", True):
            continue
        labels = [p.get("label", "") for p in (r.get("phases") or [])]
        if any("B32" in lab for lab in labels):
            vals.append((float(r["value"]), r.get("unit"), r["id"], r.get("paper_id")))
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--out", default=os.path.join(HERE, "datasets"))
    args = ap.parse_args()
    espei = os.path.join(args.data, "espei", "orchid-espei-v2026.10", "espei")
    lit = os.path.join(args.data, "literature", "orchid-literature-v2026.10", "literature", "systems", "AL-LI.json")
    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    for sub in ["zpf_experimental", "zpf_assessed", "zpf_derived", "thermo_dft", "thermo_b32", "thermo_lattice"]:
        os.makedirs(os.path.join(args.out, sub))
    log = []
    log.append(("zpf_experimental", copy_zpf(os.path.join(espei, "invariants", "AL-LI", "*.json"), os.path.join(args.out, "zpf_experimental"), "ORCHID espei/invariants")))
    log.append(("zpf_assessed", copy_zpf(os.path.join(espei, "assessed", "AL-LI", "*.json"), os.path.join(args.out, "zpf_assessed"), "ORCHID espei/assessed")))
    log.append(("zpf_derived", copy_zpf(os.path.join(espei, "derived", "invariant-brackets", "AL-LI", "*.json"), os.path.join(args.out, "zpf_derived"), "ORCHID espei/derived/invariant-brackets")
                + copy_zpf(os.path.join(espei, "derived", "liquid-stability", "AL-LI", "*.json"), os.path.join(args.out, "zpf_derived"), "ORCHID espei/derived/liquid-stability")))
    # DFT formation enthalpies: one copy (the AlLi-20Lon-named files), per mole of atoms as released
    n = 0
    for f in sorted(glob.glob(os.path.join(espei, "dft", "literature", "AL-LI", "AlLi-20Lon.*.json"))):
        shutil.copy(f, os.path.join(args.out, "thermo_dft", os.path.basename(f)))
        n += 1
    log.append(("thermo_dft", n))
    # B32 end members from the experimental HM_FORM of AlLi (B32)
    vals = b32_hm_form(lit)
    if not vals:
        raise SystemExit("no experimental HM_FORM for AlLi (B32) in the literature values")
    h = sum(v[0] for v in vals) / len(vals) * 1000.0  # kJ/mol-atom -> J/mol-atom
    ids = [v[2] for v in vals]
    for name, conf in [("AL_LI", ["AL", "LI"]), ("LI_AL", ["LI", "AL"])]:
        d = {"components": ["AL", "LI", "VA"], "phases": ["ALLI_B32"], "output": "HM_FORM",
             "conditions": {"P": 101325.0, "T": 298.15},
             "solver": {"mode": "manual", "sublattice_site_ratios": [0.5, 0.5], "sublattice_configurations": [conf]},
             "values": [[[h]]], "weight": 1.0,
             "reference": "ORCHID literature values v2026.10, experimental HM_FORM of AlLi (B32), ids " + ", ".join(ids),
             "comment": f"route-2: B32 end member {conf[0]}:{conf[1]} set to the experimental formation enthalpy of AlLi (B32) "
                        f"({h / 1000:.1f} kJ/mol-atom, mean of {len(vals)} accepted experimental records); LI:AL by symmetry"}
        json.dump(d, open(os.path.join(args.out, "thermo_b32", f"ALLI_B32.{name}.HM_FORM.json"), "w"), indent=1)
    # lattice stabilities of the pure end members of ALLI_B32 (bcc Al and bcc Li relative to GHSER), SGTE unary
    for name, conf, hval, sval in [("AL_AL", ["AL", "AL"], 10083.0, 4.813), ("LI_LI", ["LI", "LI"], 0.0, 0.0)]:
        for out, val in [("HM_FORM", hval), ("SM_FORM", sval)]:
            d = {"components": [conf[0]], "phases": ["ALLI_B32"], "output": out,
                 "conditions": {"P": 101325.0, "T": 298.15},
                 "solver": {"mode": "manual", "sublattice_site_ratios": [0.5, 0.5], "sublattice_configurations": [conf]},
                 "values": [[[val]]], "weight": 1.0,
                 "reference": "SGTE unary (Dinsdale 1991) lattice stability GBCCAL - GHSERAL = 10083 - 4.813 T (H = 10083, S = +4.813); bcc Li = GHSERLI",
                 "comment": "route-2: pure end member of ALLI_B32 placed at the bcc lattice stability (per mole of atoms)"}
            json.dump(d, open(os.path.join(args.out, "thermo_lattice", f"ALLI_B32.{name}.{out}.json"), "w"), indent=1)
    log.append(("thermo_b32", 2))
    log.append(("thermo_lattice", 4))
    with open(os.path.join(args.out, "MANIFEST.md"), "w", encoding="utf-8") as fh:
        fh.write("# route-2 datasets (built by build_datasets.py from ORCHID v2026.10)\n\n")
        for k, v in log:
            fh.write(f"- {k}: {v} files\n")
        fh.write(f"\nB32 experimental HM_FORM records used: {vals}\n")
    print(log)


if __name__ == "__main__":
    main()
