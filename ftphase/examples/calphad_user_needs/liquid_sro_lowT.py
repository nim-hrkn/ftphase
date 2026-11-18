"""Short-range order of the Li-rich ACE Al-Li liquid on cooling to 500 K (2026-11-17).  At 500 K the equilibrium liquid exists only for
x_Li > ~0.99 (hull of extend_range.py: Al4Li9 + liquid between 0.692 and 0.991); at x_Li = 0.75-0.95 the liquid is supercooled, which
MD can follow as long as it does not crystallise.  1024 atoms, NPT 0 bar, melt at 1600 K, then 1000 -> 700 -> 500 K in one run
(12 ps equilibration + 20 ps sampling each): partial g(r), first-shell coordination, Warren-Cowley alpha_1, and the mean-square
displacement of each species (liquid check: diffusion coefficient).
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/liquid_sro_lowT.py run | report   -> out/4_liquid_lowT.json / .png
"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out", "liquid_md_lowT"); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "alli_ace_txdiagram"))
XS = (0.75, 0.90, 0.95); TS = (1000, 700, 500)


def run():
    from ase.build import bulk
    from ase.io import write
    from pipeline import POT
    os.makedirs(OUT, exist_ok=True); procs = []
    for x in XS:
        d = os.path.join(OUT, f"x{x:.2f}"); os.makedirs(d, exist_ok=True)
        at = bulk("Li", "bcc", a=3.35, cubic=True).repeat((8, 8, 8)); rng = np.random.default_rng(int(x * 100)); sym = np.array(["Al"] * len(at)); sym[rng.choice(len(at), int(round(x * len(at))), replace=False)] = "Li"
        at.set_chemical_symbols(sym.tolist()); write(os.path.join(d, "conf.data"), at, format="lammps-data", specorder=["Al", "Li"], masses=True)
        L = [f"""units metal
boundary p p p
atom_style atomic
read_data conf.data
mass 1 26.9815
mass 2 6.94
pair_style pace
pair_coeff * * {POT} Al Li
group al type 1
group li type 2
timestep 0.002
velocity all create 3000.0 {int(x * 1000) + 7} dist gaussian
thermo 1000
thermo_style custom step temp press vol pe
compute g all rdf 240 1 1 1 2 2 2 cutoff 6.0
variable v equal vol
fix 1 all npt temp 1600.0 1600.0 0.1 iso 0.0 0.0 1.0
run 3000
unfix 1"""]
        for T in TS:
            L.append(f"""fix 1 all npt temp {T} {T} 0.1 iso 0.0 0.0 1.0
run 6000
reset_timestep 0
compute mA{T} al msd com yes
compute mB{T} li msd com yes
fix 2 all ave/time 10 1000 10000 c_g[*] file rdf_{T}.dat mode vector
fix 3 all ave/time 10 1000 10000 v_v file vol_{T}.dat
fix 4 all ave/time 100 1 100 c_mA{T}[4] c_mB{T}[4] file msd_{T}.dat
run 10000
unfix 1
unfix 2
unfix 3
unfix 4
uncompute mA{T}
uncompute mB{T}
write_data final_{T}.data""")
        open(os.path.join(d, "in.lmp"), "w").write("\n".join(L) + "\n")
        procs.append(subprocess.Popen([os.path.join(ROOT, "env/ftphase/bin/mpirun"), "-np", "4", os.path.join(ROOT, "env/ftphase/bin/lmp_mpi"), "-in", "in.lmp", "-log", "log.lammps", "-screen", "none"], cwd=d, env=dict(os.environ, OMP_NUM_THREADS="1")))
    print("exit codes", [p.wait() for p in procs])


def report():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    res = {}; PAIRS = ("Al-Al", "Al-Li", "Li-Li"); col = {1000: "#d62728", 700: "#ff7f0e", 500: "#1f77b4"}
    fig, axes = plt.subplots(3, len(XS), figsize=(4.9 * len(XS), 7.6), sharex=True, squeeze=False)
    for j, x in enumerate(XS):
        for T in TS:
            d = os.path.join(OUT, f"x{x:.2f}"); f = os.path.join(d, f"rdf_{T}.dat")
            if not os.path.exists(f):
                continue
            a = np.loadtxt(f, skiprows=4); r = a[:, 1]; g = {"Al-Al": a[:, 2], "Al-Li": a[:, 4], "Li-Li": a[:, 6]}; cn = {"Al-Al": a[:, 3], "Al-Li": a[:, 5], "Li-Li": a[:, 7]}
            gt = (1 - x) ** 2 * g["Al-Al"] + 2 * x * (1 - x) * g["Al-Li"] + x ** 2 * g["Li-Li"]; ip = int(np.argmax(gt)); rc = float(r[ip + int(np.argmin(gt[ip:ip + 120]))]); k = int(np.argmin(abs(r - rc)))
            n_aa, n_ab, n_bb = float(cn["Al-Al"][k]), float(cn["Al-Li"][k]), float(cn["Li-Li"][k]); n_ba = n_ab * (1 - x) / x
            m = np.loadtxt(os.path.join(d, f"msd_{T}.dat"), skiprows=2); t = m[:, 0] * 0.002; h = len(t) // 2
            D = [float(np.polyfit(t[h:], m[h:, c], 1)[0] / 6 * 1e-4 * 1e5) for c in (1, 2)]      # A^2/ps -> 1e-5 cm^2/s  (1 A^2/ps = 1e-4 cm^2/s)
            i2 = ip + int(np.argmin(gt[ip:ip + 120])); second = gt[i2:]; split = bool(np.sum((second[1:-1] > second[:-2]) & (second[1:-1] > second[2:]) & (second[1:-1] > 1.05)) > 1)
            res[f"{x:.2f}@{T}"] = {"x_Li": x, "T_K": T, "first_minimum_A": round(rc, 2), "N_AlAl": round(n_aa, 2), "N_AlLi": round(n_ab, 2), "N_LiLi": round(n_bb, 2), "N_LiAl": round(n_ba, 2),
                                   "random_N_AlAl": round((1 - x) * (n_aa + n_ab), 2), "alpha1_around_Al": round(1 - n_ab / (x * (n_aa + n_ab)), 3), "alpha1_around_Li": round(1 - n_ba / ((1 - x) * (n_bb + n_ba)), 3),
                                   "peak_height": {p: round(float(v.max()), 2) for p, v in g.items()}, "peak_A": {p: round(float(r[int(np.argmax(v))]), 2) for p, v in g.items()},
                                   "D_Al_1e-5cm2_s": round(D[0], 2), "D_Li_1e-5cm2_s": round(D[1], 2), "msd_Li_20ps_A2": round(float(m[-1, 2]), 1), "total_g_peak": round(float(gt.max()), 2), "g_min_over_max": round(float(gt[i2] / gt.max()), 3)}
            for i, p in enumerate(PAIRS):
                axes[i, j].plot(r, g[p], color=col[T], lw=1.3, label=f"{T} K, α₁ = {res[f'{x:.2f}@{T}']['alpha1_around_Al']:+.2f}, D_Li = {D[1]:.1f}")
        for i, p in enumerate(PAIRS):
            ax = axes[i, j]; ax.set(xlim=(2, 6)); ax.legend(fontsize=7)
            if i == 0: ax.set_title(f"x_Li = {x:.2f}", fontsize=9)
            if i == 2: ax.set_xlabel("r (Å)")
            if j == 0: ax.set_ylabel(f"{p}:  g(r)")
    fig.suptitle("ACE Al-Li liquid on cooling (1024 atoms, NPT): partial pair distribution functions; α₁ = Warren-Cowley parameter around Al, D_Li in 1e-5 cm²/s", fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "out", "4_liquid_lowT.png"), dpi=150); json.dump(res, open(os.path.join(HERE, "out", "4_liquid_lowT.json"), "w"), indent=1)
    for k, v in res.items():
        print(k, {q: v[q] for q in ("N_AlAl", "random_N_AlAl", "N_AlLi", "alpha1_around_Al", "D_Al_1e-5cm2_s", "D_Li_1e-5cm2_s", "g_min_over_max", "peak_height")})


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
