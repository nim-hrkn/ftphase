"""Binding energy of the B2 NiAl triple defect (2 Va_Ni + Ni_Al) when its three point defects sit next to each other (2026-11-17).
The Wagner-Schottky treatment and out_defects_mlip/TABLE.md use isolated point defects; here the three are put into one 4x4x4 cell
(128 sites): Ni_Al on an Al site and the two Ni vacancies on two of its 8 nearest Ni sites, at mutual distance a (cube edge,
<100>), a*sqrt2 (<110>) or a*sqrt3 (<111>, opposite corners), plus one cell with the three defects far apart (check of additivity).
    E_bind = [2 raw(Va_Ni) + raw(Ni_Al)] - [E(cell with the complex) - E(perfect)]      (> 0: bound)
raw(...) are read from out_defects_mlip/<mlip>.json (same cell, lattice parameter and fmax).
    python nial_triple_bound.py --mlip <name> [--device cpu|cuda] [--cmdargs "..."]   -> out_defects_mlip/<mlip>_bound.json
"""
import argparse, json, os, time
import numpy as np
from nial_defects_mlip import HERE, calculator, relax


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mlip", required=True); ap.add_argument("--device", default="cpu"); ap.add_argument("--cmdargs", default=""); a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "mlip_calcs.json")))[a.mlip]; iso = json.load(open(os.path.join(HERE, "out_defects_mlip", f"{a.mlip}.json")))
    calc = calculator(a.mlip, spec, a.device, a.cmdargs.split() if a.cmdargs else None); fmax = iso["fmax"]; a0 = iso["a0_B2_A"]; rep = round((iso["n_sites"] / 2) ** (1 / 3))
    from ase.spacegroup import crystal
    t0 = time.time(); b2 = crystal(["Al", "Ni"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=221, cellpar=[a0, a0, a0, 90, 90, 90])
    sc = b2.repeat((rep, rep, rep)); sc, e_perf, _ = relax(sc, calc, fmax=fmax); sym = np.array(sc.get_chemical_symbols())
    i_al = int(np.where(sym == "Al")[0][0]); d = sc.get_distances(i_al, range(len(sc)), mic=True); nn = [int(i) for i in np.where((sym == "Ni") & (d < 0.9 * a0))[0]]; assert len(nn) == 8
    cfg = {}
    for name, dist in (("<100> (a)", a0), ("<110> (a sqrt2)", a0 * 2 ** 0.5), ("<111> (a sqrt3)", a0 * 3 ** 0.5)):
        j = next(j for j in nn[1:] if abs(sc.get_distance(nn[0], j, mic=True) - dist) < 0.05); cfg[name] = (nn[0], j)
    ni = np.where(sym == "Ni")[0]; f1 = int(ni[np.argmax(d[ni])]); d1 = sc.get_distances(f1, range(len(sc)), mic=True); f2 = int(ni[np.argmax(np.minimum(d[ni], d1[ni]))]); cfg["far apart"] = (f1, f2)
    e_iso = 2 * iso["raw_eV"]["Va_Ni"] + iso["raw_eV"]["Ni_Al"]; res = {}
    for name, (i, j) in cfg.items():
        c = sc.copy(); c[i_al].symbol = "Ni"; dij = float(sc.get_distance(i, j, mic=True)); dia = (float(d[i]), float(d[j]))
        del c[[i, j]]; _, e, ns = relax(c, calc, fmax=fmax); raw = float(e - e_perf)
        res[name] = {"d_VaVa_A": round(dij, 3), "d_Va_antisite_A": [round(x, 3) for x in dia], "raw_eV": raw, "E_bind_eV": e_iso - raw, "triple_defect_eV": raw + 2 * iso["E_B2_per_atom"], "bfgs_steps": int(ns)}
        print(f"{a.mlip} {name}: E_bind {e_iso - raw:+.3f} eV, triple defect {res[name]['triple_defect_eV']:.3f} eV (isolated {iso['triple_defect_eV']:.3f}; {ns} steps, {time.time() - t0:.0f} s)", flush=True)
    json.dump({"mlip": a.mlip, "n_sites": len(sc), "a0_B2_A": a0, "fmax": fmax, "isolated_triple_defect_eV": iso["triple_defect_eV"], "configs": res, "seconds": time.time() - t0},
              open(os.path.join(HERE, "out_defects_mlip", f"{a.mlip}_bound.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
