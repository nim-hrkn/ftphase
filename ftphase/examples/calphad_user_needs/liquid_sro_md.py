"""Chemical short-range order in the ACE Al-Li liquid from the structure: partial pair distribution functions of an MD liquid
(1024 atoms, NPT at 1000 K and 0 bar) -> coordination numbers within the first shell -> Warren-Cowley parameter
    alpha_1 = 1 - N_AlLi / [x_Li (N_AlAl + N_AlLi)]      (alpha_1 < 0: unlike neighbours preferred; 0: random; > 0: clustering).
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/liquid_sro_md.py run     (3 compositions in parallel, ~10 min on 12 cores)
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/liquid_sro_md.py report  -> out/4_liquid_gr.png, out/4_liquid_gr.json
"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out", "liquid_md"); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "alli_ace_txdiagram"))
XS = (0.25, 0.5, 0.75); T = 1000.0


def run():
    from ase.build import bulk
    from ase.io import write
    from pipeline import POT
    os.makedirs(OUT, exist_ok=True); procs = []
    for x in XS:
        d = os.path.join(OUT, f"x{x:.2f}"); os.makedirs(d, exist_ok=True)
        at = bulk("Li", "bcc", a=3.35, cubic=True).repeat((8, 8, 8)); rng = np.random.default_rng(int(x * 100)); sym = np.array(["Al"] * len(at)); sym[rng.choice(len(at), int(round(x * len(at))), replace=False)] = "Li"
        at.set_chemical_symbols(sym.tolist()); write(os.path.join(d, "conf.data"), at, format="lammps-data", specorder=["Al", "Li"], masses=True)
        open(os.path.join(d, "in.lmp"), "w").write(f"""units metal
boundary p p p
atom_style atomic
read_data conf.data
mass 1 26.9815
mass 2 6.94
pair_style pace
pair_coeff * * {POT} Al Li
timestep 0.002
velocity all create 3000.0 {int(x * 1000) + 7} dist gaussian
thermo 500
thermo_style custom step temp press vol pe
fix 1 all npt temp 1600.0 1600.0 0.1 iso 0.0 0.0 1.0
run 3000
unfix 1
fix 1 all npt temp {T} {T} 0.1 iso 0.0 0.0 1.0
run 4000
reset_timestep 0
compute g all rdf 240 1 1 1 2 2 2 cutoff 6.0
fix 2 all ave/time 10 800 8000 c_g[*] file rdf.dat mode vector
variable v equal vol
fix 3 all ave/time 10 800 8000 v_v file vol.dat
run 8000
""")
        env = dict(os.environ, OMP_NUM_THREADS="1")
        procs.append(subprocess.Popen([os.path.join(ROOT, "env/ftphase/bin/mpirun"), "-np", "4", os.path.join(ROOT, "env/ftphase/bin/lmp_mpi"), "-in", "in.lmp", "-log", "log.lammps", "-screen", "none"], cwd=d, env=env))
    print("exit codes", [p.wait() for p in procs])


def crystal_shells(at, rmax=6.0):
    """{pair: (distances, mean number of such neighbours per central atom of the first species)} of a crystal."""
    from ase.neighborlist import neighbor_list
    i, j, d = neighbor_list("ijd", at, rmax); sym = np.array(at.get_chemical_symbols()); out = {}
    for a, b in (("Al", "Al"), ("Al", "Li"), ("Li", "Li"), ("Li", "Al")):
        m = (sym[i] == a) & (sym[j] == b); na = int((sym == a).sum())
        if na == 0 or not m.any():
            out[f"{a}-{b}"] = (np.array([]), np.array([])); continue
        dd = np.round(d[m], 2); u, c = np.unique(dd, return_counts=True); out[f"{a}-{b}"] = (u, c / na)
    return out


def report():
    """Partial g(r) of the liquid with the neighbour shells of the crystalline compound nearest in composition (sticks), and the
    first-shell partial coordination numbers: liquid / random mixture of the same total coordination / crystal."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ase.io import read
    from ftphase.validate import relax
    from pipeline import ace, b32_alli, l12_al3li
    calc = ace(); sd = os.path.join(HERE, "..", "alli_ace_txdiagram", "structures")
    cry = {0.25: ("Al3Li (L1_2)", l12_al3li()), 0.5: ("B32 AlLi", b32_alli()), 0.75: ("Al4Li9 (x = 0.692)", read(os.path.join(sd, "mp-568404-Li9Al4.cif")))}
    res = {}; PAIRS = ("Al-Al", "Al-Li", "Li-Li"); fig, axes = plt.subplots(3, len(XS), figsize=(4.9 * len(XS), 7.6), sharex=True, sharey=True, squeeze=False); col = {"Al-Al": "#1f77b4", "Al-Li": "#d62728", "Li-Li": "#2ca02c"}
    for j, x in enumerate(XS):
        d = os.path.join(OUT, f"x{x:.2f}"); a = np.loadtxt(os.path.join(d, "rdf.dat"), skiprows=4); r = a[:, 1]
        g = {"Al-Al": a[:, 2], "Al-Li": a[:, 4], "Li-Li": a[:, 6]}; cn = {"Al-Al": a[:, 3], "Al-Li": a[:, 5], "Li-Li": a[:, 7]}
        gt = (1 - x) ** 2 * g["Al-Al"] + 2 * x * (1 - x) * g["Al-Li"] + x ** 2 * g["Li-Li"]; ip = int(np.argmax(gt)); rc = float(r[ip + int(np.argmin(gt[ip:ip + 120]))])
        k = int(np.argmin(abs(r - rc))); n_aa, n_ab = float(cn["Al-Al"][k]), float(cn["Al-Li"][k]); n_bb = float(cn["Li-Li"][k]); n_ba = n_ab * (1 - x) / x
        alpha = 1 - n_ab / (x * (n_aa + n_ab)); alpha_b = 1 - n_ba / ((1 - x) * (n_bb + n_ba))
        cname, cat = cry[x]; cat = relax(cat, calc, fmax=2e-3, cell=True).atoms; cat.calc = None; sh = crystal_shells(cat); xc = cat.get_chemical_symbols().count("Li") / len(cat)
        cn_c = {p: float(c[u <= rc].sum()) if len(u) else 0.0 for p, (u, c) in sh.items()}; first = {p: (float(u[0]) if len(u) else None) for p, (u, c) in sh.items()}
        a_c = 1 - cn_c["Al-Li"] / (xc * (cn_c["Al-Al"] + cn_c["Al-Li"])) if cn_c["Al-Al"] + cn_c["Al-Li"] > 0 else None
        res[f"{x:.2f}"] = {"T_K": T, "first_minimum_A": round(rc, 2), "liquid_peak_A": {p: round(float(r[int(np.argmax(v))]), 2) for p, v in g.items()}, "liquid_peak_height": {p: round(float(v.max()), 2) for p, v in g.items()},
                           "liquid_N": {"Al-Al": round(n_aa, 2), "Al-Li": round(n_ab, 2), "Li-Li": round(n_bb, 2), "Li-Al": round(n_ba, 2)},
                           "random_N": {"Al-Al": round((1 - x) * (n_aa + n_ab), 2), "Al-Li": round(x * (n_aa + n_ab), 2), "Li-Li": round(x * (n_bb + n_ba), 2), "Li-Al": round((1 - x) * (n_bb + n_ba), 2)},
                           "warren_cowley_alpha1_around_Al": round(alpha, 3), "warren_cowley_alpha1_around_Li": round(alpha_b, 3),
                           "crystal": cname, "crystal_x": round(xc, 4), "crystal_first_distance_A": first, "crystal_N_within_cutoff": {p: round(v, 2) for p, v in cn_c.items()}, "crystal_alpha1_around_Al": None if a_c is None else round(a_c, 3)}
        for i, p in enumerate(PAIRS):       # one panel per pair, stacked vertically: sticks of different pairs at the same distance no longer hide each other
            ax = axes[i, j]; ax.plot(r, g[p], color=col[p], lw=1.5, label=p + " liquid"); u, c = sh[p]; m = u <= 6.0; u, c = u[m], c[m]
            if len(u):                      # low-symmetry crystals have many slightly different distances: sum the neighbours in 0.15 A bins (weighted mean distance)
                kb = np.floor(u / 0.15).astype(int); u, c = np.array([np.average(u[kb == q], weights=c[kb == q]) for q in np.unique(kb)]), np.array([c[kb == q].sum() for q in np.unique(kb)])
            ax.vlines(u, 0, 0.12 * c, color=col[p], lw=2.6, alpha=0.6, label=p + " crystal (number of neighbours)")
            for uu, cc in zip(u, c):
                ax.text(uu, 0.12 * cc + 0.06, f"{cc:.0f}" if abs(cc - round(cc)) < 0.05 else f"{cc:.1f}", ha="center", va="bottom", fontsize=6.5, color=col[p])
            ax.axvline(rc, color="0.6", lw=0.6, ls="--"); ax.set(xlim=(2.0, 6)); ax.legend(fontsize=7, loc="upper right")
            if i == 0:
                ax.set_title(f"x_Li = {x:.2f}, {T:.0f} K, α₁ = {alpha:+.2f}; crystal: {cname}", fontsize=8.5)
            if i == 2:
                ax.set_xlabel("r (Å)")
            if j == 0:
                ax.set_ylabel(f"{p}:  g(r)")
    fig.suptitle("ACE Al-Li liquid (1024 atoms, NPT): partial pair distribution functions (curves) against the neighbour shells of the nearest compound (sticks, height 0.12 × number of neighbours, number written above; distances within 0.15 Å are summed);\nrows = pair, columns = composition; dashed = first minimum of the total g(r); α₁ = Warren-Cowley parameter around Al (< 0 = unlike neighbours preferred)", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "out", "4_liquid_gr.png"), dpi=150); json.dump(res, open(os.path.join(HERE, "out", "4_liquid_gr.json"), "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1]]()
