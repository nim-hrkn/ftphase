"""Export MatterSim checkpoints as LAMMPS ML-IAP unified models (official wrapper, mattersim >= 1.2.5).

    env/torch/bin/python mattersim_to_mliap.py [mattersim-v1.0.0-5M mattersim-v1.0.0-1M ...]

Writes potentials/mattersim/<version>_mliap.pt (torch.compile on the GPU at first use, the wrapper default) and
<version>_mliap_nocompile.pt (compile=False).  The checkpoints are downloaded by mattersim into
~/.local/mattersim/pretrained_models/ on first use.  Runs on the CPU (no GPU needed).
"""
import os
import sys

import torch

from mattersim.lammps.mliap_wrapper import MatterSimMLIAP

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "potentials", "mattersim")
os.makedirs(OUT, exist_ok=True)

versions = sys.argv[1:] or ["mattersim-v1.0.0-5M", "mattersim-v1.0.0-1M"]
for v in versions:
    for compile_flag, suffix in ((True, "_mliap.pt"), (False, "_mliap_nocompile.pt")):
        m = MatterSimMLIAP.from_checkpoint(v, device="cpu", compile=compile_flag)
        path = os.path.join(OUT, v + suffix)
        m.save(path)
        n = sum(p.numel() for p in m.m3gnet_lammps.parameters())
        print(f"{path}: cutoff {m.cutoff} A, threebody {m.threebody_cutoff} A, {n} parameters, compile={compile_flag}, "
              f"dtype {next(m.m3gnet_lammps.parameters()).dtype}, {os.path.getsize(path)/1e6:.1f} MB")
