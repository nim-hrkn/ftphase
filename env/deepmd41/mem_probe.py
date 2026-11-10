"""GPU memory of the DPA-4.1-Max-OAM .pt2 vs cell size (ASE DP calculator), to see what fits on the 12 GB RTX 3060."""
import sys, torch
from ase.build import bulk
from deepmd.calculator import DP
calc = DP(model=sys.argv[1])
for n in (1, 2, 3, 4):
    at = bulk("Al", "fcc", a=4.05, cubic=True) * (n, n, n)
    at.symbols[: len(at) // 3] = "Li"
    torch.cuda.reset_peak_memory_stats(); torch.cuda.empty_cache()
    try:
        at.calc = calc; e = at.get_potential_energy()
        print(f"{len(at):4d} atoms: E/atom {e/len(at):.4f} eV, peak GPU {torch.cuda.max_memory_allocated()/2**30:.2f} GiB, reserved {torch.cuda.memory_reserved()/2**30:.2f} GiB", flush=True)
    except Exception as ex:
        print(f"{len(at):4d} atoms: FAILED {str(ex)[:120]}", flush=True); break
