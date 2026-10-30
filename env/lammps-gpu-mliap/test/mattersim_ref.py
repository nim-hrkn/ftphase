"""Reference energy / pressure of test/conf.data (108-atom Al-Li) with the MatterSim ASE calculator (CPU, float32),
for comparison with pair_style mliap unified in LAMMPS.  Writes mattersim_ref.txt.

    env/torch/bin/python mattersim_ref.py
"""
import os

from ase.io import read
from ase import units
from mattersim.forcefield import MatterSimCalculator

HERE = os.path.dirname(os.path.abspath(__file__))
atoms = read(os.path.join(HERE, "conf.data"), format="lammps-data", style="atomic", Z_of_type={1: 13, 2: 3})
lines = []
for v in ("mattersim-v1.0.0-5M", "mattersim-v1.0.0-1M"):
    atoms.calc = MatterSimCalculator(load_path=v, device="cpu")
    e = atoms.get_potential_energy()
    s = atoms.get_stress(voigt=True)                     # eV/A^3, ASE sign (positive = tensile)
    p_bar = -s[:3].mean() / units.bar                    # LAMMPS press = -trace(stress)/3
    lines.append(f"{v}: natoms {len(atoms)} pe {e:.5f} eV  press {p_bar:.3f} bar  pxx {-s[0]/units.bar:.3f} pxy {-s[5]/units.bar:.3f}")
    print(lines[-1])
open(os.path.join(HERE, "mattersim_ref.txt"), "w").write("\n".join(lines) + "\n")
