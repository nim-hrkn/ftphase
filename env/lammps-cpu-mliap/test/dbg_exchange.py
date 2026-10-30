import sys, numpy as np, torch
from lammps.mliap.mliap_unified_abc import MLIAPUnified
class DbgExchange(MLIAPUnified):
    def __init__(self):
        super().__init__(); self.ndescriptors = 1; self.nparams = 1; self.element_types = ["Al", "Li"]; self.rcutfac = 2.5
    def compute_gradients(self, data): pass
    def compute_descriptors(self, data): pass
    def compute_forces(self, data):
        nl, nt, k = data.nlocal, data.ntotal, int(__import__("os").environ.get("DBG_VECLEN", "4"))
        full = torch.zeros((nt, k), dtype=torch.float64); full[:nl, 0] = torch.arange(nl, dtype=torch.float64); full[:nl, 1:] = 7.0
        out = torch.full((nt, k), -1.0, dtype=torch.float64)
        try:
            data.forward_exchange(full, out, k)
            g = out[nl:]; print("DBG forward_exchange ok: local rows copied", bool(torch.equal(out[:nl], full[:nl])), "ghost col0 range", float(g[:,0].min()), float(g[:,0].max()), "ghost col1 all 7", bool((g[:,1]==7).all()), "ghost untouched(-1)", int((g[:,0]==-1).sum()), "of", nt-nl, file=sys.stderr)
            for dt in (torch.float64, torch.float32):   # copy_to must be ntotal-sized (the C++ copies all of copy_from first, then zeroes the ghost rows)
                back = torch.zeros((nt, k), dtype=dt); gin = torch.ones((nt, k), dtype=dt)
                data.reverse_exchange(gin, back, k); print("DBG reverse_exchange", str(dt), "local sums min/max", float(back[:nl,0].min()), float(back[:nl,0].max()), "(= 1 + ghost images per local atom) ghosts zeroed", bool((back[nl:]==0).all()), file=sys.stderr)
                f32in = torch.zeros((nt, k), dtype=dt); f32in[:nl, 0] = torch.arange(nl, dtype=dt); o = torch.full((nt, k), -1.0, dtype=dt); data.forward_exchange(f32in, o, k); print("DBG forward_exchange", str(dt), "ghost col0 range", float(o[nl:,0].min()), float(o[nl:,0].max()), file=sys.stderr)
        except Exception as e:
            print("DBG exchange EXC", repr(e)[:200], file=sys.stderr)
        n = data.npairs; data.update_pair_energy(np.zeros(n)); data.update_pair_forces(np.zeros((n, 3)))
