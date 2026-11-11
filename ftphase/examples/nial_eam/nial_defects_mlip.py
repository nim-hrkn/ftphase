"""B2 NiAl point-defect energies with an MLIP (step 1 of the triple-defect check, 2026-11-11): the EAM analysis of
vacancy_analysis.py (a) repeated with the MLIPs of the Ni-Al WorkChains.  4x4x4 B2 (128 sites) relaxed at the MLIP's own lattice
parameter; one defect per cell (Va_Ni, Va_Al, Ni_Al, Al_Ni), positions relaxed at fixed cell; raw energies, formation energies vs the
pure elements, the composition-conserving triple defect 2 Va_Ni + Ni_Al and the Schottky / antisite pairs.
    python nial_defects_mlip.py --mlip grace-fs|grace-1l|sevenn-0|sevenn-mf-ompa|mace-mpa-0|mattersim-5m [--device cpu|cuda] [--fmax 5e-3]
Calculator settings come from mlip_calcs.json (dumped from run_aiida.MLIPS); torch MLIPs need their own env (env/torch, env/mace),
LAMMPS ones env/ftphase (grace/1l needs the Kokkos GPU build: --cmdargs "-k on g 1 -sf kk -pk kokkos newton on neigh half").
Output: out_defects_mlip/<mlip>.json
"""
import argparse, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def calculator(mlip, spec, device, cmdargs):
    kind = spec.get("qha_calculator") or "lammps"
    if kind == "lammps":
        from ase.calculators.lammpslib import LAMMPSlib
        pot = spec["potential"]; pc = spec["pair_coeff"].format(potential=pot).replace("Al Li", "Al Ni")
        return LAMMPSlib(lmpcmds=[f"pair_style {spec['pair_style']}", f"pair_coeff {pc}"], atom_types={"Al": 1, "Ni": 2}, keep_alive=True, log_file=None,
                         lammps_header=["units metal", "atom_style atomic", "atom_modify map array sort 0 0"], **({"extra_cmd_args": cmdargs} if cmdargs else {}))
    pot = spec["potential_qha"]
    if kind == "sevenn":
        from sevenn.calculator import SevenNetCalculator
        return SevenNetCalculator(model=pot, device=device, modal="mpa" if "ompa" in pot.lower() or "mf" in os.path.basename(pot).lower() else None)
    if kind == "mace":
        from mace.calculators import MACECalculator
        return MACECalculator(model_paths=pot, device=device, default_dtype="float64")
    if kind == "mattersim":
        from mattersim.forcefield import MatterSimCalculator
        return MatterSimCalculator(load_path=pot, device=device)
    if kind == "deepmd":
        from deepmd.calculator import DP
        return DP(model=pot)
    raise SystemExit(kind)


def relax(atoms, calc, cell=False, fmax=5e-3, steps=1500):
    from ase.filters import FrechetCellFilter
    from ase.optimize import BFGS
    a = atoms.copy(); a.calc = calc
    opt = BFGS(FrechetCellFilter(a) if cell else a, logfile=None); opt.run(fmax=fmax, steps=steps)
    return a, float(a.get_potential_energy()), opt.nsteps


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mlip", required=True); ap.add_argument("--device", default="cpu"); ap.add_argument("--fmax", type=float, default=5e-3)
    ap.add_argument("--cmdargs", default=""); ap.add_argument("--rep", type=int, default=4); a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "mlip_calcs.json")))[a.mlip]
    calc = calculator(a.mlip, spec, a.device, a.cmdargs.split() if a.cmdargs else None)
    from ase.build import bulk
    from ase.spacegroup import crystal
    t0 = time.time()
    b2 = crystal(["Al", "Ni"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=221, cellpar=[2.88, 2.88, 2.88, 90, 90, 90])
    b2, _, _ = relax(b2, calc, cell=True, fmax=1e-3); a0 = float(b2.cell.lengths()[0])
    sc = b2.repeat((a.rep, a.rep, a.rep)); sc, e_perf, _ = relax(sc, calc, fmax=a.fmax); n = len(sc)
    al, _, _ = relax(bulk("Al", "fcc", a=4.05, cubic=True), calc, cell=True, fmax=1e-3); ni, _, _ = relax(bulk("Ni", "fcc", a=3.52, cubic=True), calc, cell=True, fmax=1e-3)
    e_al = float(al.get_potential_energy()) / len(al); e_ni = float(ni.get_potential_energy()) / len(ni); e_b2 = float(e_perf) / n   # torch calculators return numpy float32
    syms = sc.get_chemical_symbols(); i_al = syms.index("Al"); i_ni = syms.index("Ni")
    cells = {}
    v = sc.copy(); del v[i_ni]; cells["Va_Ni"] = v
    v = sc.copy(); del v[i_al]; cells["Va_Al"] = v
    v = sc.copy(); v[i_al].symbol = "Ni"; cells["Ni_Al"] = v
    v = sc.copy(); v[i_ni].symbol = "Al"; cells["Al_Ni"] = v
    raw, steps = {}, {}
    for k, c in cells.items():
        _, e, ns = relax(c, calc, fmax=a.fmax); raw[k] = float(e - e_perf); steps[k] = int(ns)
        print(f"{a.mlip} {k}: raw {raw[k]:+.3f} eV ({ns} steps, {time.time() - t0:.0f} s)", flush=True)
    out = {"mlip": a.mlip, "model": spec.get("model"), "device": a.device, "fmax": a.fmax, "n_sites": n, "a0_B2_A": a0, "E_B2_per_atom": e_b2, "E_fccAl_per_atom": e_al, "E_fccNi_per_atom": e_ni,
           "E_form_B2_eV_per_atom": e_b2 - 0.5 * (e_al + e_ni), "raw_eV": raw, "bfgs_steps": steps,
           "formation_vs_pure_elements_eV": {"Va_Ni": raw["Va_Ni"] + e_ni, "Va_Al": raw["Va_Al"] + e_al, "Ni_Al": raw["Ni_Al"] - e_ni + e_al, "Al_Ni": raw["Al_Ni"] - e_al + e_ni},
           "formation_vs_compound_eV": {"Va_Ni": raw["Va_Ni"] + e_b2, "Va_Al": raw["Va_Al"] + e_b2},
           "triple_defect_eV": 2 * raw["Va_Ni"] + raw["Ni_Al"] + 2 * e_b2, "schottky_pair_eV": raw["Va_Ni"] + raw["Va_Al"] + 2 * e_b2, "antisite_pair_eV": raw["Ni_Al"] + raw["Al_Ni"],
           "seconds": time.time() - t0}
    os.makedirs(os.path.join(HERE, "out_defects_mlip"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "out_defects_mlip", f"{a.mlip}.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("raw_eV", "bfgs_steps")}, indent=0))


if __name__ == "__main__":
    main()
