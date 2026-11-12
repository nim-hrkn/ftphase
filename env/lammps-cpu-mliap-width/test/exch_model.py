"""Minimal MLIAPUnified model that only exercises forward_exchange / reverse_exchange with a chosen width.
EXCH_VECLEN = width used at run time (default 4); EXCH_DECLARE = comm_width declared by the model (unset = not declared).
python exch_model.py  writes exch.pkl (declaration is read from the environment when the pickle is LOADED, in __setstate__)."""
import os, sys, numpy as np, torch
from lammps.mliap.mliap_unified_abc import MLIAPUnified


class Exch(MLIAPUnified):
    def __init__(self):
        super().__init__(); self.ndescriptors = 1; self.nparams = 1; self.element_types = ["Al", "Li"]; self.rcutfac = 2.5

    def __setstate__(self, st):
        self.__dict__.update(st)
        d = os.environ.get("EXCH_DECLARE")
        if d:
            self.comm_width = int(d)

    def compute_gradients(self, data): pass
    def compute_descriptors(self, data): pass

    def compute_forces(self, data):
        nl, nt, k = data.nlocal, data.ntotal, int(os.environ.get("EXCH_VECLEN", "4"))
        full = torch.zeros((nt, k), dtype=torch.float64); full[:nl, 0] = torch.arange(nl, dtype=torch.float64); full[:nl, 1:] = 7.0
        out = torch.full((nt, k), -1.0, dtype=torch.float64)
        data.forward_exchange(full, out, k)
        g = out[nl:]
        back = torch.zeros((nt, k), dtype=torch.float64); gin = torch.ones((nt, k), dtype=torch.float64)
        data.reverse_exchange(gin, back, k)
        ok = bool(torch.equal(out[:nl], full[:nl])) and bool((g[:, -1] == 7).all()) and int((g[:, 0] == -1).sum()) == 0 and bool((back[nl:] == 0).all())
        print(f"EXCH k={k} nlocal={nl} nghost={nt - nl} forward_ok={ok} ghost_col0_max={float(g[:, 0].max()) if nt > nl else -1:.0f} reverse_sum={float(back[:nl].sum()):.0f} expect={float(nt * k):.0f}", file=sys.stderr, flush=True)
        n = data.npairs; data.update_pair_energy(np.zeros(n)); data.update_pair_forces(np.zeros((n, 3)))


if __name__ == "__main__":
    Exch().pickle("exch.pkl"); print("wrote exch.pkl")
