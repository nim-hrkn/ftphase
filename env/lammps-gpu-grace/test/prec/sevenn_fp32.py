import numpy as np, torch, warnings
warnings.filterwarnings("ignore")
from ase.build import bulk
from sevenn.calculator import SevenNetCalculator
rng = np.random.default_rng(0)
a = bulk("Al", "fcc", a=4.05, cubic=True).repeat((4, 4, 4))
syms = np.array(a.get_chemical_symbols(), dtype=object); syms[rng.choice(len(a), int(0.3 * len(a)), replace=False)] = "Li"; a.set_chemical_symbols(list(syms)); a.rattle(0.08, seed=1)
calc = SevenNetCalculator(model="7net-0", device="cpu")
def ef(at):
    at = at.copy(); at.calc = calc; return at.get_potential_energy(), at.get_forces()
E0, F0 = ef(a)
# 1) rigid translations and permutations: exact invariance in exact arithmetic -> spread = float32 rounding noise
Es, Fs = [], []
for i in range(8):
    b = a.copy(); b.translate(rng.uniform(-3, 3, 3)); b.wrap(); p = rng.permutation(len(b)); b = b[p]
    E, F = ef(b); Es.append(E); Fs.append(F[np.argsort(p)])
Es = np.array(Es); n = len(a)
print(f"SevenNet-0 float32, {n} atoms: energy spread under rigid translation+permutation: std {Es.std()/n*1e6:.2f} ueV/atom, max dev {np.abs(Es-E0).max()/n*1e6:.2f} ueV/atom")
dF = np.array(Fs) - F0; print(f"  force noise: RMS {np.sqrt((dF**2).mean())*1000:.3f} meV/A, max {np.abs(dF).max()*1000:.2f} meV/A (force RMS {np.sqrt((F0**2).mean()):.3f} eV/A)")
print(f"  net force |sum F| = {np.linalg.norm(F0.sum(0))*1000:.3f} meV/A")
# 2) finite-difference check of forces (central, h = 0.01 A) on 5 atoms: fp32 energy noise limits dE/h
errs = []
for i in rng.choice(n, 5, replace=False):
    for k in range(3):
        bp = a.copy(); bp.positions[i, k] += 0.01; bm = a.copy(); bm.positions[i, k] -= 0.01
        errs.append(-(ef(bp)[0] - ef(bm)[0]) / 0.02 - F0[i, k])
errs = np.array(errs); print(f"  finite-difference force error (h=0.01 A): RMS {np.sqrt((errs**2).mean())*1000:.2f} meV/A, max {np.abs(errs).max()*1000:.2f} meV/A")
