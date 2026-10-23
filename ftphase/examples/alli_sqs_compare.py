"""Stage 02A test: sqsgenerator vs icet SQS vs random cells for fcc Al-Li (ACE potential).

For x_Li = 1/16, 1/8, 1/4 and 32 / 64-atom fcc cells, build the solid-solution cell with
  (a) random substitution (ftphase.structures.composition_series, seed 0),
  (b) icet SQS in the fixed supercell (sqs_icet(method='supercells'), cutoffs 7.0/5.0 A),
  (c) sqsgenerator 0.5.6 (sqs_sqsgenerator, Warren-Cowley objective, 5 shells),
and compare: icet cluster-vector deviation (pairs + triplets), the first-shell Warren-Cowley
parameter of the Al-Li pair, the relaxed 0 K energy (ACE, hydrostatic cell relaxation) and, for
x = 1/8, the quasi-harmonic G at 800 K (phonopy, 5 volumes, mesh 60 A).  Timings are recorded.

Output: out_alli_ace/sqs_compare.json and sqs_compare.md.  Run as a Slurm CPU job (about 10-15 min).
"""

import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
OUT = os.path.join(HERE, "out_alli_ace")
CUTOFFS = [7.0, 5.0]


def ace():
    from ase.calculators.lammpslib import LAMMPSlib

    return LAMMPSlib(lmpcmds=["pair_style pace", f"pair_coeff * * {POT} Al Li"], atom_types={"Al": 1, "Li": 2}, keep_alive=True, log_file=None)


def warren_cowley_first_shell(atoms, a_elem="Al", b_elem="Li", rcut=3.2):
    """alpha_AB of the first shell: 1 - P(B | neighbour of A) / x_B."""
    from ase.neighborlist import neighbor_list

    i, j = neighbor_list("ij", atoms, rcut)
    syms = np.asarray(atoms.get_chemical_symbols())
    x_b = float(np.mean(syms == b_elem))
    mask = syms[i] == a_elem
    p_b = float(np.mean(syms[j[mask]] == b_elem)) if mask.any() else np.nan
    return 1.0 - p_b / x_b


def main():
    from ase.build import bulk
    from icet import ClusterSpace
    from icet.tools.structure_generation import _get_sqs_cluster_vector

    from ftphase.qha import phonopy_volume_scan
    from ftphase.structures import composition_series, sqs_icet, sqs_sqsgenerator
    from ftphase.validate import relax

    os.makedirs(OUT, exist_ok=True)
    calc = ace()
    prim = bulk("Al", "fcc", a=4.05)
    cs = ClusterSpace(prim, cutoffs=CUTOFFS, chemical_symbols=[["Al", "Li"]])

    def icet_dev(at, x):
        cv = cs.get_cluster_vector(at)
        tgt = _get_sqs_cluster_vector(cs, {"Al": 1 - x, "Li": x})
        return float(np.sum(np.abs(np.asarray(cv) - np.asarray(tgt))))

    rows = []
    T_qha = np.arange(0.0, 1001.0, 50.0)
    for rep, n in (((2, 2, 2), 32), ((4, 2, 2), 64)):
        base = bulk("Al", "fcc", a=4.05, cubic=True).repeat(rep)
        for x in (1 / 16, 1 / 8, 1 / 4):
            n_li = int(round(x * n))
            cells = {}
            t0 = time.time()
            m = list(composition_series(base, "Li", [x], seed=0, n_configs=1))[0]
            cells["random"] = (m.atoms.copy(), time.time() - t0)
            t0 = time.time()
            at, meta = sqs_icet(prim, [["Al", "Li"]], CUTOFFS, {"Al": 1 - x, "Li": x}, n, method="supercells", supercells=[base.copy()], n_steps=20000, seed=0)
            cells["icet"] = (at, time.time() - t0)
            t0 = time.time()
            at, meta_sg = sqs_sqsgenerator(base, {"Al": n - n_li, "Li": n_li}, iterations=500000)
            cells["sqsgenerator"] = (at, time.time() - t0)
            for gen, (at, dt) in cells.items():
                at = at.copy(); at.calc = None
                r = relax(at, calc, fmax=1e-3, cell=True, hydrostatic=True)
                row = {"n": n, "x": n_li / n, "generator": gen, "seconds_generate": dt, "icet_cluster_vector_deviation": icet_dev(at, n_li / n),
                       "alpha_AlLi_shell1": warren_cowley_first_shell(at), "E0_eV_per_atom": r.energy_per_atom, "V0_A3_per_atom": r.volume_per_atom}
                if gen == "sqsgenerator":
                    row["sqsgenerator_objective"] = meta_sg["objective"]
                if abs(n_li / n - 0.125) < 1e-9:
                    t1 = time.time()
                    a0 = r.atoms.copy(); a0.calc = None
                    sc = np.diag([2, 2, 2]) if n == 32 else np.diag([1, 2, 2])      # 256-atom phonon supercell in both cases
                    res, _ = phonopy_volume_scan(a0, calc, sc, T_qha, scales=(0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04), mesh=60.0, imaginary="drop", eos="vinet")
                    G, V = res.per_atom()
                    row["G800_eV_per_atom"] = float(np.interp(800.0, T_qha, G))
                    row["seconds_qha"] = time.time() - t1
                rows.append(row)
                print(json.dumps(row), flush=True)
    with open(os.path.join(OUT, "sqs_compare.json"), "w") as f:
        json.dump(rows, f, indent=1)
    # markdown: differences relative to the icet cell at the same (n, x)
    L = ["# 02A: sqsgenerator vs icet SQS vs random cells, fcc Al-Li, ACE (0 K relaxed energies; QHA G at 800 K for x = 1/8)", "",
         "| N | x_Li | generator | icet cluster-vector deviation | alpha_AlLi (shell 1) | E0 - E0(icet) (meV/atom) | G800 - G800(icet) (meV/atom) | generate (s) |", "|---|---|---|---|---|---|---|---|"]
    for n in (32, 64):
        for x in sorted({r["x"] for r in rows}):
            ref = next(r for r in rows if r["n"] == n and r["x"] == x and r["generator"] == "icet")
            for r in [r for r in rows if r["n"] == n and r["x"] == x]:
                dG = f"{(r['G800_eV_per_atom'] - ref['G800_eV_per_atom']) * 1000:+.2f}" if "G800_eV_per_atom" in r else "-"
                L.append(f"| {n} | {x:.4f} | {r['generator']} | {r['icet_cluster_vector_deviation']:.3f} | {r['alpha_AlLi_shell1']:+.3f} | {(r['E0_eV_per_atom'] - ref['E0_eV_per_atom']) * 1000:+.2f} | {dG} | {r['seconds_generate']:.2f} |")
    with open(os.path.join(OUT, "sqs_compare.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
