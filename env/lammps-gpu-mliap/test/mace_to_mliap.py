# same as mace_create_lammps_model --format mliap, but without the forced e3nn->cueq conversion
import sys, torch
from mace.calculators.lammps_mliap_mace import LAMMPS_MLIAP_MACE
from mace.cli.create_lammps_model import select_head
model = torch.load(sys.argv[1], map_location="cpu", weights_only=False)
model = (model.float() if len(sys.argv) > 2 and sys.argv[2] == "float32" else model.double()).to("cpu")
model.lammps_mliap = True
head = select_head(model)
torch.save(LAMMPS_MLIAP_MACE(model, head=head) if head is not None else LAMMPS_MLIAP_MACE(model), sys.argv[1] + ("-mliap_lammps-f32.pt" if len(sys.argv) > 2 and sys.argv[2] == "float32" else "-mliap_lammps.pt"))
print("wrote", sys.argv[1] + ("-mliap_lammps-f32.pt" if len(sys.argv) > 2 and sys.argv[2] == "float32" else "-mliap_lammps.pt"))
