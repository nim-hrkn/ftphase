import re, sys, numpy as np, torch
from mliap_torch_lj_autograd import MLIAPUnifiedTorchLJAutograd
class DbgLibs(MLIAPUnifiedTorchLJAutograd):
    def compute_forces(self, data):
        if not getattr(self, "_done", False):
            self._done = True
            libs = sorted({l.split()[-1] for l in open('/proc/self/maps') if re.search(r'gomp|iomp|libomp|openblas|mkl|libstdc\+\+|libgcc_s|libpython', l)})
            print("DBG libs:", " ".join(l.replace('/home/kino/kino/Claude/Projects/PhaseDiagram/', '') for l in libs), file=sys.stderr)
            a = torch.randn(600, 600, dtype=torch.float64); print("DBG matmul ok", float((a @ a).sum()) != 0, file=sys.stderr)
            x = torch.zeros(10, dtype=torch.float64); x.index_add_(0, torch.tensor([1, 1, 2]), torch.ones(3, dtype=torch.float64)); print("DBG index_add ok", x.tolist()[1:3], file=sys.stderr)
            import e3nn, torch_geometric; print("DBG e3nn", e3nn.__version__, "torch_geometric", torch_geometric.__version__, file=sys.stderr)
            import mattersim.forcefield; print("DBG mattersim import ok", file=sys.stderr)
        super().compute_forces(data)
