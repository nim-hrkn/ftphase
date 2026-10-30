import sys, numpy as np, torch
from lammps.mliap.mliap_unified_abc import MLIAPUnified
def step(name, fn):
    try:
        r = fn(); print("DBG", name, "ok", r, file=sys.stderr); sys.stderr.flush()
    except Exception as e:
        print("DBG", name, "EXC", repr(e)[:150], file=sys.stderr); sys.stderr.flush()
class DbgE3nn(MLIAPUnified):
    def __init__(self):
        super().__init__(); self.ndescriptors = 1; self.nparams = 1; self.element_types = ["Al", "Li"]; self.rcutfac = 2.5
    def compute_gradients(self, data): pass
    def compute_descriptors(self, data): pass
    def compute_forces(self, data):
        nt = data.ntotal
        import e3nn; from e3nn import o3; from e3nn.nn import FullyConnectedNet
        print("DBG e3nn", e3nn.__version__, "jit enabled", torch._C._jit_can_fuse_on_cpu() if hasattr(torch._C, "_jit_can_fuse_on_cpu") else "?", file=sys.stderr); sys.stderr.flush()
        fc = FullyConnectedNet([8, 64, 64, 16], torch.nn.functional.silu)
        step("e3nn FC fwd f32", lambda: float(fc(torch.randn(nt, 8)).sum()))
        def fcbwd():
            x = torch.randn(nt, 8, requires_grad=True); (g,) = torch.autograd.grad(fc(x).pow(2).sum(), x); return float(g.abs().sum())
        step("e3nn FC fwd+bwd f32", fcbwd)
        tp = o3.FullyConnectedTensorProduct("16x0e+16x1o", "0e+1o+2e", "16x0e+16x1o")
        step("e3nn TP fwd f32", lambda: float(tp(torch.randn(nt, tp.irreps_in1.dim), torch.randn(nt, tp.irreps_in2.dim)).sum()))
        def tpbwd():
            x = torch.randn(nt, tp.irreps_in1.dim, requires_grad=True); (g,) = torch.autograd.grad(tp(x, torch.randn(nt, tp.irreps_in2.dim)).pow(2).sum(), x); return float(g.abs().sum())
        step("e3nn TP fwd+bwd f32", tpbwd)
        @torch.jit.script
        def jf(x: torch.Tensor) -> torch.Tensor:
            return (x * 2.0 + 1.0).relu().sum(dim=1)
        step("torchscript fn fwd", lambda: float(jf(torch.randn(nt, 64)).sum()))
        step("torchscript fn fwd (2nd call, fused)", lambda: float(jf(torch.randn(nt, 64)).sum()))
        n = data.npairs; data.update_pair_energy(np.zeros(n)); data.update_pair_forces(np.zeros((n, 3)))
