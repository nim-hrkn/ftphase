import sys, time, importlib.util
if "mace" in sys.argv[2]:
    import h5py, mace.data  # env h5py before liblammps.so (libhdf5 clash)
sys.path.append("/home/kino/kino/Claude/Projects/PhaseDiagram/env/ftphase/lib/python3.12/site-packages")
import lammps.mliap.loader as L
from lammps import lammps
M, kind = sys.argv[1], sys.argv[2]
def act(lmp):
    for name in ["mliap_model_python_couple", "mliap_unified_couple", "mliap_unified_couple_kokkos"]:
        if name in sys.modules: continue
        loader = L.DynamicLoader(name, lmp.lib)
        spec = importlib.util.spec_from_loader(name, loader); m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m; loader.exec_module(m)
base = """units metal
boundary p p p
atom_style atomic
atom_modify map yes
newton on
read_data conf.data
mass 1 26.9815
mass 2 6.94
thermo_style custom step pe press pxx pxy vol
"""
ps = f"mliap unified {M} 0" if kind == "mace" else "mliap unified EXISTS 0"
cases = {"plain": f"pair_style {ps}\npair_coeff * * Al Li",
         "hs1": f"variable lam equal 1.0\npair_style hybrid/scaled v_lam {ps}\npair_coeff * * mliap Al Li",
         "hs1222": f"variable lam equal 1.222222\npair_style hybrid/scaled v_lam {ps}\npair_coeff * * mliap Al Li"}
for k, pair in cases.items():
    lmp = lammps(cmdargs=["-log", "none", "-screen", "none", "-k", "on", "g", "1", "-sf", "kk", "-pk", "kokkos", "newton", "on", "neigh", "half"])
    act(lmp)
    if kind == "sevenn":
        from sevenn.mliap import SevenNetMLIAPWrapper
        sys.modules["mliap_unified_couple_kokkos"].load_from_python(SevenNetMLIAPWrapper(M, element_types=["Al", "Li"]))
    out = []
    lmp.commands_string(base + pair + "\nrun 0")
    out.append((lmp.get_thermo('pe'), lmp.get_thermo('press')))
    lmp.commands_string("change_box all x final 0.0 12.851 y final 0.0 12.851 z final 0.0 12.851 remap units box\nrun 0")
    out.append((lmp.get_thermo('pe'), lmp.get_thermo('press')))
    if k == "plain":
        lmp.commands_string("velocity all create 600.0 4928459 loop geom\nfix 1 all nve\ntimestep 0.001\nrun 20")
        t0 = time.time(); lmp.command("run 100"); dt = (time.time() - t0) / 100
        out.append(dt)
    print(k, " | ".join(f"pe={a:.6f} press={b:.4f}" if isinstance(a, float) else "" for a, b in out[:2]), (f"| {out[2]:.4f} s/step (108 atoms, 100 NVE steps)" if len(out) > 2 else ""), flush=True)
    lmp.close()
