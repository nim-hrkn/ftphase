"""Minimal ML-IAP unified model that evaluates LJ with *torch* on whatever arrays the coupling hands over (numpy on the CPU, cupy
on the GPU).  Purpose: test torch inside LAMMPS's embedded interpreter on the CPU Kokkos build independently of any MLIP package.

    env/torch/bin/python -c "import mliap_torch_lj as m; m.write()"   # (from this folder) writes mliap_unified_torch_lj_Ar.pkl
    PYTHONPATH=<this folder> lmp_cpumliap -k on t 1 -sf kk -pk kokkos newton on neigh half -in in.torch_lj.Ar   (1 or 4 ranks)
Reference: the numpy LJ example (examples/mliap/in.mliap.unified.lj.Ar) gives pe = -6.7733681 per atom at step 0.
"""
import pickle

import numpy as np
import torch
from lammps.mliap.mliap_unified_abc import MLIAPUnified


class MLIAPUnifiedTorchLJ(MLIAPUnified):
    def __init__(self, element_types, epsilon=1.0, sigma=1.0, rcutfac=1.25, copy_inputs=True):
        super().__init__()
        self.ndescriptors = 1
        self.nparams = 3
        self.element_types = element_types
        self.rcutfac = rcutfac
        self.epsilon = epsilon
        self.sigma = sigma
        self.copy_inputs = copy_inputs

    def compute_gradients(self, data):
        pass

    def compute_descriptors(self, data):
        pass

    def compute_forces(self, data):
        rij = torch.as_tensor(np.array(data.rij) if self.copy_inputs else data.rij, dtype=torch.float64)
        r2inv = 1.0 / (rij * rij).sum(dim=1)
        r6inv = r2inv * r2inv * r2inv
        lj1 = 4.0 * self.epsilon * self.sigma**12
        lj2 = 4.0 * self.epsilon * self.sigma**6
        eij = r6inv * (lj1 * r6inv - lj2)
        fij = r6inv * (3.0 * lj2 - 6.0 * lj1 * r6inv) * r2inv   # LAMMPS ML-IAP convention (lammps.mliap.mliap_unified_lj): fij = +1/2 dE/drij
        fij = fij.unsqueeze(1) * rij
        data.update_pair_energy(eij.numpy())
        data.update_pair_forces(fij.numpy())


def write():
    for copy, name in ((True, "mliap_unified_torch_lj_Ar.pkl"), (False, "mliap_unified_torch_lj_Ar_nocopy.pkl")):
        m = MLIAPUnifiedTorchLJ(["Ar"], epsilon=1.0, sigma=1.0, rcutfac=1.25, copy_inputs=copy)   # reduced units like lammps.mliap.mliap_unified_lj.MLIAPUnifiedLJ(["Ar"])
        with open(name, "wb") as f:
            pickle.dump(m, f)
        print("wrote", name)
