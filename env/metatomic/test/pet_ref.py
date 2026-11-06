"""Reference energies of a LAMMPS data file with the upet ASE calculator (same exported .pt), for the LAMMPS check.
usage: python pet_ref.py model.pt data.file   (types 1=Al, 2=Li)"""
import sys
from ase.io import read
from metatomic.torch.ase_calculator import MetatomicCalculator
model, data = sys.argv[1], sys.argv[2]
atoms = read(data, format="lammps-data", style="atomic", Z_of_type={1: 13, 2: 3})
atoms.calc = MetatomicCalculator(model, device="cuda")
e = atoms.get_potential_energy(); s = atoms.get_stress(voigt=True)
print(f"natoms {len(atoms)} E {e:.6f} eV  E/atom {e/len(atoms):.6f}  press(bar) {-s[:3].mean()*1.602176634e6:.2f}")
