import sys, numpy as np
from lammps.mliap.mliap_unified_abc import MLIAPUnified
class DbgInts(MLIAPUnified):
    def __init__(self):
        super().__init__(); self.ndescriptors = 1; self.nparams = 1; self.element_types = ["Al", "Li"]; self.rcutfac = 2.5
    def compute_gradients(self, data): pass
    def compute_descriptors(self, data): pass
    def compute_forces(self, data):
        e, pi, pj, r = data.elems, data.pair_i, data.pair_j, data.rij
        print("DBG nlocal", data.nlocal, "ntotal", data.ntotal, "npairs", data.npairs, "nlistatoms", data.nlistatoms, file=sys.stderr)
        for n, a in (("elems", e), ("pair_i", pi), ("pair_j", pj), ("rij", r)):
            a = np.asarray(a); print("DBG", n, a.dtype, a.shape, "min", a.min(), "max", a.max(), "first", a.ravel()[:6].tolist(), file=sys.stderr)
        d = np.sqrt((np.asarray(r)**2).sum(1)); print("DBG |rij| min %.3f max %.3f" % (d.min(), d.max()), "bad pair_i(>=nlocal)", int((np.asarray(pi) >= data.nlocal).sum()), "bad pair_j(>=ntotal)", int((np.asarray(pj) >= data.ntotal).sum()), file=sys.stderr)
        data.update_pair_energy(np.zeros(len(d))); data.update_pair_forces(np.zeros((len(d), 3)))
