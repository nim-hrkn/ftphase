"""Integration example 2: a real MLIP (Al-Li ACE, pyiron potentials-workshop-2022,
AlLi-6gen-18May.yace; Menon et al. 2024) through stages 01, 02A, 03A, 04B.

* 01: relax fcc Al, bcc Li, B32 AlLi (NaTl type), L1_2 Al3Li with the ACE
      potential (LAMMPS pair_style pace via ASE LAMMPSlib); 0 K convex hull;
      compare with the known ground states (fcc Al, bcc Li, B32 AlLi; Al3Li is
      metastable, Menon et al. 2024); EOS of fcc Al (bulk modulus check).
* 02A: a random fcc Al0.9Li0.1 cell (32 atoms, seed 0) and an icet SQS of the
      same composition (enumeration, 8-16 atoms) -> cluster-vector deviation.
* 03A: phonopy volume scan + QHA (9 volumes, -3 % .. +5 % in length, 2x2x2 supercell of the cubic
      fcc cell = 32 atoms, 8x8x8 mesh) for fcc Al and B32 AlLi -> G(T) at 0 GPa,
      V(T), B(T).
* 04B: quantum-minus-classical harmonic correction dF(T) of fcc Al.

Run on CPU (the GPU is unavailable on this host).  Results in out_alli_ace/.
"""

import json
import os
import time

import numpy as np
import pandas as pd
from ase import Atoms
from ase.build import bulk
from ase.calculators.lammpslib import LAMMPSlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples", "workshop2022-phase-diagram", "resources", "lammps", "potentials", "ace", "AlLi-6gen-18May.yace")
OUT = os.path.join(HERE, "out_alli_ace")
os.makedirs(OUT, exist_ok=True)

from ftphase.validate import relax, hull_0K, compare_ground_states, eos_scan
from ftphase.structures import composition_series, sqs_icet
from ftphase.qha import phonopy_volume_scan
from ftphase.quantum import quantum_minus_classical
from ftphase.records import FreeEnergyTable


def ace():
    return LAMMPSlib(lmpcmds=["pair_style pace", f"pair_coeff * * {POT} Al Li"], atom_types={"Al": 1, "Li": 2}, keep_alive=True, log_file=None)


def b32_alli(a=6.37):
    """NaTl (B32) AlLi: Fd-3m, Al at 8a (0,0,0), Li at 8b (1/2,1/2,1/2), conventional cubic 16 atoms."""
    from ase.spacegroup import crystal
    return crystal(["Al", "Li"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=227, cellpar=[a, a, a, 90, 90, 90])


def l12_al3li(a=4.0):
    return Atoms("LiAl3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[a, a, a], pbc=True)


def main():
    t0 = time.time()
    log = {}
    calc = ace()
    # ---------------- 01: candidates, relax, hull ----------------
    cands = {
        "fcc-Al": (bulk("Al", "fcc", a=4.05, cubic=True), 0.0),
        "bcc-Li": (bulk("Li", "bcc", a=3.49, cubic=True), 1.0),
        "fcc-Li": (bulk("Li", "fcc", a=4.40, cubic=True), 1.0),
        "B32-AlLi": (b32_alli(), 0.5),
        "L12-Al3Li": (l12_al3li(), 0.25),
    }
    rows = []
    relaxed = {}
    for name, (at, x) in cands.items():
        r = relax(at, calc, fmax=1e-3, cell=True)
        relaxed[name] = r
        rows.append({"name": name, "x": x, "e": r.energy_per_atom, "V": r.volume_per_atom, "sg_before": r.spacegroup_before, "sg_after": r.spacegroup_after, "converged": r.converged, "transformed": r.transformed})
        print(f"[01] {name:10s} E={r.energy_per_atom:.5f} eV/atom V={r.volume_per_atom:.3f} A3  {r.spacegroup_before} -> {r.spacegroup_after}")
    relax_df = pd.DataFrame(rows)
    hull = hull_0K(relax_df["name"], relax_df["x"], relax_df["e"])
    cmp = compare_ground_states(hull, ["fcc-Al", "bcc-Li", "B32-AlLi"])
    print(hull.round(5).to_string(index=False)); print(cmp.to_string(index=False))
    relax_df.to_csv(os.path.join(OUT, "relaxed.tsv"), sep="\t", index=False)
    hull.to_csv(os.path.join(OUT, "hull_0K.tsv"), sep="\t", index=False)
    cmp.to_csv(os.path.join(OUT, "ground_state_check.tsv"), sep="\t", index=False)
    try:
        from ftphase.validate import hull_0K_pymatgen
        eah = hull_0K_pymatgen(relax_df["name"], ("Al", "Li"), relax_df["x"], relax_df["e"])
        log["pymatgen_e_above_hull_max_abs_diff"] = float(np.max(np.abs(eah - hull.set_index("name").loc[relax_df["name"], "e_above_hull"].to_numpy())))
        print("[01] pymatgen cross-check max |diff| e_above_hull:", log["pymatgen_e_above_hull_max_abs_diff"])
    except Exception as e:
        log["pymatgen"] = repr(e)
    fit, V, E = eos_scan(relaxed["fcc-Al"].atoms, calc, scales=(0.94, 0.96, 0.98, 1.0, 1.02, 1.04, 1.06))
    log["fcc_Al_eos"] = {"V0_A3_per_atom": fit.V0, "B0_GPa": fit.B0_GPa, "B1": fit.B1, "rmse_eV": fit.rmse}
    print(f"[01] fcc Al Vinet: V0={fit.V0:.3f} A3/atom, B0={fit.B0_GPa:.1f} GPa (expt. ~76 GPa), B'={fit.B1:.2f}")

    # ---------------- 02A: random cell and SQS ----------------
    base = relaxed["fcc-Al"].atoms.repeat((2, 2, 2))
    base.calc = None
    series = composition_series(base, "Li", [0.125], seed=0, n_configs=2)
    e_rand = []
    for m in series:
        a = m.atoms.copy(); a.calc = calc
        e_rand.append(a.get_potential_energy() / len(a))
    log["random_Al0.875Li0.125_energies_unrelaxed"] = e_rand
    print("[02A] random 32-atom cells, x_Li=0.125, unrelaxed E (eV/atom):", np.round(e_rand, 5))
    try:
        prim = bulk("Al", "fcc", a=relaxed["fcc-Al"].atoms.cell.lengths()[0])
        sqs, meta = sqs_icet(prim, [["Al", "Li"]], cutoffs=[7.0, 5.0], target_concentrations={"Al": 0.875, "Li": 0.125}, max_size=16, method="enumeration")
        s = sqs.copy(); s.calc = calc
        log["sqs"] = {"n_atoms": len(sqs), "cluster_vector_deviation": meta["cluster_vector_deviation"], "E_unrelaxed_eV_per_atom": s.get_potential_energy() / len(s)}
        print("[02A] icet SQS:", log["sqs"])
        from ase.io import write
        write(os.path.join(OUT, "sqs_Al0.875Li0.125.vasp"), sqs, format="vasp", direct=True, sort=True)
    except Exception as e:
        log["sqs"] = repr(e); print("[02A] SQS failed:", repr(e))

    # ---------------- 03A: phonopy QHA ----------------
    Ts = np.arange(0.0, 1001.0, 50.0)
    qha_rows = []
    for name, sc, mesh in (("fcc-Al", np.diag([2, 2, 2]), (8, 8, 8)), ("B32-AlLi", np.diag([2, 2, 2]), (6, 6, 6))):
        at = relaxed[name].atoms.copy(); at.calc = None
        t1 = time.time()
        res, data = phonopy_volume_scan(at, calc, sc, Ts, scales=(0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05), mesh=mesh, imaginary="raise", eos="vinet")
        G, Vt = res.per_atom()
        print(f"[03A] {name}: QHA done in {time.time()-t1:.0f} s; G(300K)={G[6]:.5f} eV/atom, V(0K)={Vt[0]:.3f}, V(1000K)={Vt[-1]:.3f} A3/atom, B(300K)={res.bulk_modulus_gpa[6]:.1f} GPa")
        x = 0.0 if name == "fcc-Al" else 0.5
        for T, g, v in zip(Ts, G, Vt):
            qha_rows.append({"phase": name, "kind": "solution" if name == "fcc-Al" else "point", "x": x, "T": T, "P_GPa": 0.0, "G": g, "G_err": 0.0, "V": v,
                             "model": "AlLi-6gen-18May.yace (ACE)", "reference_state": "absolute ACE energy", "method": f"QHA vinet 7 volumes, phonopy sc={np.diag(sc).tolist()} mesh={list(mesh)}, quantum",
                             "config_entropy": "none", "quantum": "quantum", "n_atoms": len(at), "source": "examples/alli_ace_validate_qha.py"})
        # 04B: quantum - classical harmonic difference at the equilibrium volume (index of scale 1.0)
        hw, w = data["frequencies"][3]
        np.savez(os.path.join(OUT, f"frequencies_{name}_scale1.npz"), hw_eV=hw, weights=w, n_atoms=len(at), volumes=data["volumes"], e0=data["e0"], f_vib=data["f_vib"], T=Ts)
        dF = quantum_minus_classical(hw, Ts[1:], weights=w) / len(at)
        log[f"{name}_quantum_minus_classical_meV_per_atom"] = {int(T): float(d * 1000) for T, d in zip(Ts[1:], dF)}
        print(f"[04B] {name}: F_q - F_cl = {dF[5]*1000:.2f} meV/atom at 300 K, {dF[-1]*1000:.2f} meV/atom at 1000 K (ZPE-dominated at low T)")
        # thermal expansion sanity
        log[f"{name}_linear_expansion_300_900K_ppm_per_K"] = float(((Vt[18] / Vt[6]) ** (1 / 3) - 1) / 600 * 1e6)
    tab = FreeEnergyTable.from_rows(qha_rows, {"potential": POT})
    tab.to_tsv(os.path.join(OUT, "qha_free_energies.tsv"))
    log["elapsed_s"] = time.time() - t0
    with open(os.path.join(OUT, "log.json"), "w") as f:
        json.dump(log, f, indent=1, default=str)
    print("done in", round(log["elapsed_s"]), "s")


if __name__ == "__main__":
    main()
