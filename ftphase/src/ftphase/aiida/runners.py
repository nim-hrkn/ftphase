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


def volume_scan_data(atoms, calc, supercell_matrix, T, scales, mesh, imaginary, fmax):
    """Energies and phonon free energies on the volume scan (the per-volume part of
    :func:`ftphase.qha.phonopy_volume_scan`, computed once so the QHA fit can be retried)."""
    from ase.optimize import BFGS
    from ftphase.qha import phonopy_free_energy

    vols, e0s, Fs, freqs = [], [], [], []
    for s in scales:
        a = atoms.copy()
        a.set_cell(atoms.get_cell() * s, scale_atoms=True)
        a.calc = calc
        if len(a) > 1:
            BFGS(a, logfile=None).run(fmax=fmax, steps=500)
        vols.append(a.get_volume())
        e0s.append(a.get_potential_energy())
        F, hw, w = phonopy_free_energy(a, calc, supercell_matrix, T, mesh=mesh, imaginary=imaginary, return_frequencies=True)
        Fs.append(F)
        freqs.append((hw, w))
    return {"volumes": np.array(vols), "e0": np.array(e0s), "f_vib": np.array(Fs).T, "frequencies": freqs}


def qha_main(argv=None):
    from ase.io import read
    from ftphase.qha import qha_gibbs
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
    scales = tuple(p.get("scales", (0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05)))
    sc = np.diag(p["supercell"]) if np.ndim(p["supercell"]) == 1 else np.asarray(p["supercell"])
    data = volume_scan_data(atoms, calc, sc, T, scales, mesh, p.get("imaginary", "drop"), float(p.get("relax", {}).get("fmax", 1e-3)))
    # QHA has no minimum far above the melting point: shorten the temperature range instead of failing
    T_full = T
    while True:
        try:
            res = qha_gibbs(data["volumes"], data["e0"], T, data["f_vib"][: len(T)], pressure_gpa=float(p.get("pressure_GPa", 0.0)), eos=p.get("eos", "vinet"), n_atoms=len(atoms))
            break
        except ValueError as exc:
            if len(T) <= 4:
                raise
            T = T[:-1]
            out.setdefault("qha_T_shortened", []).append(f"{float(T_full[len(T)]):.0f} K dropped: {exc}")
    res.metadata.update({"scales": list(scales), "supercell_matrix": np.asarray(sc).tolist(), "mesh": (list(mesh) if np.ndim(mesh) else float(mesh)), "T_max_effective": float(T.max())})
    G, V = res.per_atom()
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
