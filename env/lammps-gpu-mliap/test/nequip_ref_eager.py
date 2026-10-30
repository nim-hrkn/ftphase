"""Reference energy / pressure of test/conf.data (108-atom Al-Li) from the NequIP package model evaluated eagerly on the CPU
(no AOTInductor compile: the GPU compile needs cuda.h on CPATH, the CPU compile hits an inductor codegen error with g++ 13).
Uses nequip's own data pipeline (from_ase -> type mapper -> neighbour list) and the packaged GraphModel.  Appends to nequip_ref.txt.

    env/torch/bin/python nequip_ref_eager.py potentials/nequip/NequIP-OAM-L-0.1.nequip.zip "label"
"""
import os
import sys

import torch
from ase import units
from ase.io import read
from nequip.data import AtomicDataDict as K
from nequip.data.ase import from_ase
from nequip.data.transforms import ChemicalSpeciesToAtomTypeMapper, NeighborListTransform
from nequip.model.saved_models.load_utils import load_saved_model
from nequip.nn import graph_model

HERE = os.path.dirname(os.path.abspath(__file__))
path, label = sys.argv[1], sys.argv[2]
torch.set_default_dtype(torch.float64)
model = load_saved_model(path, compile_mode="eager").eval()
r_max = float(model.metadata[graph_model.R_MAX_KEY])
atoms = read(os.path.join(HERE, "conf.data"), format="lammps-data", style="atomic", Z_of_type={1: 13, 2: 3})
data = from_ase(atoms)
data = ChemicalSpeciesToAtomTypeMapper(model_type_names=model.type_names, chemical_species_to_atom_type_map={"Al": "Al", "Li": "Li"})(data)
data = NeighborListTransform(r_max=r_max, type_names=model.type_names)(data)
data = K.with_batch_(data)
out = model(data)
e = float(out[K.TOTAL_ENERGY_KEY].sum())
stress = out[K.STRESS_KEY].detach().reshape(3, 3).numpy() if K.STRESS_KEY in out else None   # eV/A^3, ASE sign
line = f"{label}: natoms {len(atoms)} r_max {r_max} dtype {model.metadata.get(graph_model.MODEL_DTYPE_KEY)} pe {e:.5f} eV"
if stress is not None:
    line += f"  press {-stress.trace()/3/units.bar:.3f} bar  pxx {-stress[0,0]/units.bar:.3f} pxy {-stress[0,1]/units.bar:.3f}"
print(line)
with open(os.path.join(HERE, "nequip_ref.txt"), "a") as f:
    f.write(line + "\n")
