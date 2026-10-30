import sys, numpy as np, torch
from lammps.mliap.mliap_unified_abc import MLIAPUnified
def step(name, fn):
    try:
        r = fn(); print("DBG", name, "ok", r, file=sys.stderr); sys.stderr.flush()
    except Exception as e:
        print("DBG", name, "EXC", repr(e)[:150], file=sys.stderr); sys.stderr.flush()
class DbgFC(MLIAPUnified):
    def __init__(self):
        super().__init__(); self.ndescriptors = 1; self.nparams = 1; self.element_types = ["Al", "Li"]; self.rcutfac = 2.5
        torch.manual_seed(0); self.lin32 = torch.nn.Linear(64, 64); self.lin64 = torch.nn.Linear(64, 64).double()
    def compute_gradients(self, data): pass
    def compute_descriptors(self, data): pass
    def compute_forces(self, data):
        nt = data.ntotal; print("DBG threads", torch.get_num_threads(), "interop", torch.get_num_interop_threads(), file=sys.stderr); sys.stderr.flush()
        step("f64 matmul 1098x64x64", lambda: float((torch.randn(nt, 64, dtype=torch.float64) @ torch.randn(64, 64, dtype=torch.float64)).sum()))
        step("f32 matmul 1098x64x64", lambda: float((torch.randn(nt, 64) @ torch.randn(64, 64)).sum()))
        step("f64 Linear fwd", lambda: float(self.lin64(torch.randn(nt, 64, dtype=torch.float64)).sum()))
        step("f32 Linear fwd", lambda: float(self.lin32(torch.randn(nt, 64)).sum()))
        def bwd32():
            x = torch.randn(nt, 64, requires_grad=True); y = self.lin32(x).pow(2).sum(); (g,) = torch.autograd.grad(y, x); return float(g.abs().sum())
        step("f32 Linear fwd+bwd", bwd32)
        def idx():
            x = torch.randn(nt, 16, requires_grad=True); idx = torch.as_tensor(np.array(data.pair_i), dtype=torch.int64)
            out = torch.zeros(nt, 16).index_add(0, idx, x[idx] * 2.0); y = out.sum(); (g,) = torch.autograd.grad(y, x); return float(g.sum())
        step("index_add fwd+bwd", idx)
        step("f32 big matmul 2000x512x512", lambda: float((torch.randn(2000, 512) @ torch.randn(512, 512)).sum()))
        n = data.npairs; data.update_pair_energy(np.zeros(n)); data.update_pair_forces(np.zeros((n, 3)))
