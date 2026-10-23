"""Executables that the CalcJobs run on the compute node (inside env/ftphase).

``ftphase-qha-run input.json``: stage 03A for one cell.  Reads the cell (``structure.extxyz``),
the potential description and the QHA parameters, relaxes the cell (optional), runs
:func:`ftphase.qha.phonopy_volume_scan` and writes ``qha_results.json`` (scalars, metadata)
and ``qha_arrays.npz`` (G(T), V(T), frequencies at the 0 K volume for stage 04B).
"""

import json
import os
import sys
import time

import numpy as np


def lammps_calculator(pair_style: str, pair_coeff: str, atom_types: dict):
    from ase.calculators.lammpslib import LAMMPSlib

    return LAMMPSlib(lmpcmds=[f"pair_style {pair_style}", f"pair_coeff {pair_coeff}"], atom_types=dict(atom_types), keep_alive=True, log_file=None)


def qha_main(argv=None):
    from ase.io import read
    from ftphase.qha import phonopy_volume_scan
    from ftphase.validate import relax

    argv = sys.argv[1:] if argv is None else argv
    inp = json.load(open(argv[0] if argv else "input.json"))
    t0 = time.time()
    pot = os.path.abspath(inp["potential"])
    calc = lammps_calculator(inp["pair_style"], inp["pair_coeff"].format(potential=pot), inp["atom_types"])
    atoms = read(inp.get("structure", "structure.extxyz"))
    p = inp["parameters"]
    out = {"n_atoms": len(atoms), "started": time.strftime("%F %T")}
    if p.get("relax", {}).get("do", True):
        r = relax(atoms, calc, fmax=float(p["relax"].get("fmax", 1e-3)), cell=bool(p["relax"].get("cell", True)), hydrostatic=bool(p["relax"].get("hydrostatic", True)))
        atoms = r.atoms.copy()
        out.update({"E0_eV_per_atom": r.energy_per_atom, "V0_A3_per_atom": r.volume_per_atom, "spacegroup_before": r.spacegroup_before,
                    "spacegroup_after": r.spacegroup_after, "relax_converged": bool(r.converged), "transformed": bool(r.transformed)})
    atoms.calc = None
    T = np.asarray(p["temperatures"], dtype=float)
    mesh = p.get("mesh", 60.0)
    mesh = tuple(mesh) if isinstance(mesh, (list, tuple)) else float(mesh)
    res, data = phonopy_volume_scan(atoms, calc, np.diag(p["supercell"]) if np.ndim(p["supercell"]) == 1 else np.asarray(p["supercell"]), T,
                                    scales=tuple(p.get("scales", (0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05))), mesh=mesh,
                                    imaginary=p.get("imaginary", "drop"), eos=p.get("eos", "vinet"), pressure_gpa=float(p.get("pressure_GPa", 0.0)))
    G, V = res.per_atom()
    scales = list(p.get("scales", (0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05)))
    i0 = int(np.argmin(np.abs(np.asarray(scales) - 1.0)))
    hw, w = data["frequencies"][i0]
    np.savez("qha_arrays.npz", T=T, G=np.asarray(G, dtype=float), V=np.asarray(V, dtype=float), hw_eV=np.asarray(hw, dtype=float),
             weights=np.asarray(w, dtype=float), volumes=np.asarray(data["volumes"], dtype=float), e0=np.asarray(data["e0"], dtype=float),
             f_vib=np.asarray(data["f_vib"], dtype=float))
    out.update({"metadata": {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in res.metadata.items()}, "G300_eV_per_atom": float(np.interp(300.0, T, G)) if T.max() >= 300 else None,
                "V_Tmax_A3_per_atom": float(V[-1]), "n_imaginary_dropped": int(np.sum(np.asarray(hw) < 0)), "frequency_volume_index": i0,
                "seconds": time.time() - t0, "finished": time.strftime("%F %T"), "units": {"G": "eV/atom", "V": "A^3/atom", "T": "K", "hw_eV": "eV"}})
    with open("qha_results.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"ftphase-qha-run: {len(atoms)} atoms, {len(T)} temperatures, {time.time()-t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(qha_main())
