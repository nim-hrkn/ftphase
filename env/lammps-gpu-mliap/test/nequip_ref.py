"""Reference energy / pressure of test/conf.data (108-atom Al-Li) with the NequIP ASE calculator from an AOTInductor-compiled
model (nequip-compile --mode aotinductor --target ase, done on the same GPU inside bench_nequip.sbatch).  Writes nequip_ref.txt.

    env/torch/bin/python nequip_ref.py <model.nequip.pt2> <label> [device]
"""
import os
import sys

from ase import units
from ase.io import read
from nequip.ase import NequIPCalculator

HERE = os.path.dirname(os.path.abspath(__file__))
path, label = sys.argv[1], sys.argv[2]
device = sys.argv[3] if len(sys.argv) > 3 else "cuda"
atoms = read(os.path.join(HERE, "conf.data"), format="lammps-data", style="atomic", Z_of_type={1: 13, 2: 3})
atoms.calc = NequIPCalculator.from_compiled_model(path, device=device, chemical_species_to_atom_type_map={"Al": "Al", "Li": "Li"})
e = atoms.get_potential_energy()
s = atoms.get_stress(voigt=True)
line = f"{label}: natoms {len(atoms)} pe {e:.5f} eV  press {-s[:3].mean()/units.bar:.3f} bar  pxx {-s[0]/units.bar:.3f} pxy {-s[5]/units.bar:.3f}"
print(line)
with open(os.path.join(HERE, "nequip_ref.txt"), "a") as f:
    f.write(line + "\n")
