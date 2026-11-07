"""Reference energy of a LAMMPS data file with the deepmd ASE calculator. usage: python test_ref.py model.pth data.file"""
import sys
from ase.io import read
from deepmd.calculator import DP
model, data = sys.argv[1], sys.argv[2]
atoms = read(data, format="lammps-data", style="atomic", Z_of_type={1: 13, 2: 3})
atoms.calc = DP(model=model)
e = atoms.get_potential_energy(); s = atoms.get_stress(voigt=True)
print(f"natoms {len(atoms)} E {e:.6f} eV  E/atom {e/len(atoms):.6f}  press(bar) {-s[:3].mean()*1.602176634e6:.2f}")
