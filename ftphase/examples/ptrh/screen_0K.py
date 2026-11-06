"""0 K screen of the Pt-Rh ordered structures with a universal MLIP (stage 01 outside AiiDA), for the comparison with
Table 2 / Fig. 3 of Saengdeejing et al., npj Comput. Mater. 12, 362 (2026) (PFP vs DFT).

    <env python> screen_0K.py --mlip mace-mpa-0 [--device cpu]      # env/mace for MACE, env/torch for SevenNet / MatterSim

Structures: fcc Pt, fcc Rh, PtRh '40' (I4_1/amd), PtRh L1_0 (P4/mmm), PtRh3 D0_22 (I4/mmm), PtRh3 L1_2 (Pm-3m),
Pt3Rh D0_22, Pt3Rh L1_2.  Each is relaxed (positions + cell, fmax 1e-3) with ftphase.validate.relax; the formation
energy is per atom relative to the relaxed fcc ends.  Output: out/screen_<mlip>.tsv"""

import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ftphase", "src"))


def load_mlips():
    spec = importlib.util.spec_from_file_location("run_aiida", os.path.join(ROOT, "ftphase", "examples", "aiida_txdiagram", "run_aiida.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MLIPS


def structures():
    from ase import Atoms
    from ase.build import bulk
    from pymatgen.core import Lattice, Structure
    from pymatgen.io.ase import AseAtomsAdaptor

    def tet(sg, a, c, species, coords):
        return AseAtomsAdaptor.get_atoms(Structure.from_spacegroup(sg, Lattice.tetragonal(a, c), species, coords))

    l10 = Atoms("PtRh", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0.5)], cell=[2.75, 2.75, 3.80], pbc=True)   # P4/mmm, c/a ~ 1.38 (fcc-based L1_0)
    l12_ptrh3 = Atoms("PtRh3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[3.87] * 3, pbc=True)
    l12_pt3rh = Atoms("RhPt3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[3.93] * 3, pbc=True)
    return [("fcc-Pt", 0.0, bulk("Pt", "fcc", a=3.924, cubic=True)), ("fcc-Rh", 1.0, bulk("Rh", "fcc", a=3.803, cubic=True)),
            ("PtRh-40 (I4_1/amd)", 0.5, tet("I4_1/amd", 3.899, 7.811, ["Pt", "Rh"], [[0, 0, 0], [0, 0, 0.5]])),
            ("PtRh-L1_0 (P4/mmm)", 0.5, l10),
            ("PtRh3-D0_22 (I4/mmm)", 0.75, tet("I4/mmm", 3.867, 7.738, ["Pt", "Rh", "Rh"], [[0, 0, 0], [0, 0, 0.5], [0, 0.5, 0.25]])),
            ("PtRh3-L1_2 (Pm-3m)", 0.75, l12_ptrh3),
            ("Pt3Rh-D0_22 (I4/mmm)", 0.25, tet("I4/mmm", 3.937, 7.861, ["Rh", "Pt", "Pt"], [[0, 0, 0], [0, 0, 0.5], [0, 0.5, 0.25]])),
            ("Pt3Rh-L1_2 (Pm-3m)", 0.25, l12_pt3rh)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mlip", required=True)
    ap.add_argument("--device", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    a = ap.parse_args()
    ml = load_mlips()[a.mlip]
    from ftphase.aiida.runners import make_calculator
    from ftphase.validate import relax

    inp = {"pair_style": ml.get("qha_pair_style", ml["pair_style"]), "pair_coeff": ml["pair_coeff"].replace("Al Li", "Pt Rh"), "atom_types": {"Pt": 1, "Rh": 2}}
    for k in ("qha_calculator", "qha_dtype", "qha_modal"):
        if k in ml:
            inp[k[4:]] = ml[k]
    if a.device:
        inp["device"] = a.device
    calc = make_calculator(inp, ml.get("potential_qha") or ml["potential"])
    rows = []
    # random 32-atom fcc cells at x = 0.25, 0.5, 0.75 (same generator and seed as the WorkChain's fcc series): the ordering
    # energy E(ordered) - E(random) at equal composition is what decides whether the ordered phases exist at T > 0
    from ase.build import bulk
    from ftphase.structures import composition_series
    base = bulk("Pt", "fcc", a=3.924, cubic=True).repeat((2, 2, 2))
    rnd = [(f"fcc-random-{m.x_actual:.2f}-seed{m.seed}", m.x_actual, m.atoms) for m in composition_series(base, "Rh", [0.25, 0.5, 0.75], seed=0, n_configs=2)]
    for name, x, at in structures() + rnd:
        at = at.copy()
        at.calc = calc
        r = relax(at, calc, fmax=1e-3, cell=True, hydrostatic=False)
        rows.append([name, x, r.energy_per_atom, r.volume_per_atom, r.spacegroup_after, bool(r.converged)])
    e_pt = [r[2] for r in rows if r[0] == "fcc-Pt"][0]
    e_rh = [r[2] for r in rows if r[0] == "fcc-Rh"][0]
    rand = {}
    for name, x, e, V, sg, conv in rows:
        if name.startswith("fcc-random"):
            rand.setdefault(round(x, 2), []).append(e)
    os.makedirs(a.out, exist_ok=True)
    fn = os.path.join(a.out, f"screen_{a.mlip}.tsv")
    with open(fn, "w") as fh:
        fh.write("structure\tx_Rh\tE_per_atom_eV\tE_form_eV_per_atom\tV_per_atom_A3\tspacegroup_after\tconverged\tE_minus_E_random_eV_per_atom\n")
        for name, x, e, V, sg, conv in rows:
            ef = e - (1 - x) * e_pt - x * e_rh
            dord = (e - sum(rand[round(x, 2)]) / len(rand[round(x, 2)])) if (round(x, 2) in rand and not name.startswith("fcc-random")) else float("nan")
            fh.write(f"{name}\t{x:.4f}\t{e:.6f}\t{ef:.5f}\t{V:.4f}\t{sg}\t{conv}\t{dord:.5f}\n")
            print(f"{name:26s} x={x:.2f} E_form={ef*1000:7.1f} meV/atom  E-E_random={dord*1000:7.1f}  V={V:.3f} {sg} {'' if conv else 'NOT CONVERGED'}")
    print("wrote", fn)


if __name__ == "__main__":
    main()
