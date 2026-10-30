"""Torch LJ unified model that gets the pair forces from torch.autograd (like the MACE / MatterSim / NequIP wrappers do) instead of
the analytic derivative: isolates torch autograd inside LAMMPS's embedded interpreter on the CPU Kokkos build.

    cd env/lammps-cpu-mliap/test && PYTHONPATH=$PWD env/torch/bin/python -c "import mliap_torch_lj_autograd as m; m.write(EPS, SIGMA)"
"""
import pickle

import numpy as np
import torch
from lammps.mliap.mliap_unified_abc import MLIAPUnified


class MLIAPUnifiedTorchLJAutograd(MLIAPUnified):
    def __init__(self, element_types, epsilon=1.0, sigma=1.0, rcutfac=1.25, multithread=None):
        super().__init__()
        self.ndescriptors = 1
        self.nparams = 3
        self.element_types = element_types
        self.rcutfac = rcutfac
        self.epsilon = epsilon
        self.sigma = sigma
        self.multithread = multithread   # None = leave torch's default, False = torch.autograd.set_multithreading_enabled(False)

    def compute_gradients(self, data):
        pass

    def compute_descriptors(self, data):
        pass

    def compute_forces(self, data):
        if self.multithread is not None:
            torch.autograd.set_multithreading_enabled(bool(self.multithread))
        rij = torch.as_tensor(np.array(data.rij), dtype=torch.float64).requires_grad_(True)
        r2inv = 1.0 / (rij * rij).sum(dim=1)
        r6inv = r2inv * r2inv * r2inv
        lj1 = 4.0 * self.epsilon * self.sigma**12
        lj2 = 4.0 * self.epsilon * self.sigma**6
        eij = r6inv * (lj1 * r6inv - lj2)
        (dE_drij,) = torch.autograd.grad(eij.sum(), rij)
        # LAMMPS ML-IAP convention (lammps.mliap.mliap_unified_lj, verified against it): fij = +1/2 dE/drij per pair
        fij = 0.5 * dE_drij
        data.update_pair_energy(eij.detach().numpy())
        data.update_pair_forces(fij.detach().contiguous().numpy())


def write(epsilon=1.0, sigma=1.0, rcutfac=1.25):
    for mt, name in ((None, "mliap_unified_torch_lj_autograd.pkl"), (False, "mliap_unified_torch_lj_autograd_nomt.pkl")):
        with open(name, "wb") as f:
            pickle.dump(MLIAPUnifiedTorchLJAutograd(["Ar"], epsilon=epsilon, sigma=sigma, rcutfac=rcutfac, multithread=mt), f)
        print("wrote", name)
