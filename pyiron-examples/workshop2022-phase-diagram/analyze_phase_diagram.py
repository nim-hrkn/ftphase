"""Analysis part of tutorial_2.ipynb (pyiron potentials-workshop-2022, Al-Li, EAM 'LiAl-atomicrex'),
plus a T-x phase diagram assembled from the same data.

Steps (as in the tutorial): free energies at a temperature from the 18 reversible-scaling jobs,
ideal-mixing configurational entropy added to fcc and B32 (not to the liquid), cubic polynomial fits in x,
normalisation to the liquid end-point line, common tangents by fsolve (tutorial, 800/900/950 K).
Added here: for a grid of temperatures, the lower convex hull of the three fitted curves
gives single-phase and two-phase regions -> T-x diagram (0 <= x_Li <= 0.5).
Caveat from the tutorial: 256/432-atom cells and 5 ps switching -> qualitative only.
"""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PYIRONRESOURCEPATHS", os.path.join(HERE, "resources"))
os.environ.setdefault("PYIRONDISABLE", "True")
os.environ.setdefault("PYIRONPROJECTCHECKENABLED", "False")
os.chdir(HERE); sys.path.insert(0, HERE)
from pyiron_atomistics import Project
from helpers import fe_at, normalise_fe, find_common_tangent
from calphy.integrators import kb
from scipy.spatial import ConvexHull

OUT = os.path.join(HERE, "analysis"); os.makedirs(OUT, exist_ok=True)
pr = Project("phase_diagram")
comp = np.arange(0, 0.6, 0.1)
jobs = {"fcc": [pr.load("xp_sol")] + [pr.load(f"x{i}_sol") for i in range(5)],
        "lqd": [pr.load("xp_lqd")] + [pr.load(f"x{i}_lqd") for i in range(5)],
        "b32": [pr.load("xp_alli")] + [pr.load(f"x{i}_alli") for i in range(5)]}
# actual compositions realised by the random substitution (integer atom counts)
def x_li(job):
    s = job.structure; return np.mean(np.array(s.get_chemical_symbols()) == "Li")
xreal = {k: np.array([x_li(j) for j in v]) for k, v in jobs.items()}
smix = -kb * np.array([(x*np.log(x) + (1-x)*np.log(1-x)) if 0 < x < 1 else 0.0 for x in comp])
colors = {"fcc": "#e58080", "lqd": "#66cfff", "b32": "#ffc766"}
grid = np.linspace(0, 0.5, 1000)

def curves(T):
    F = {k: np.array([fe_at(j, T) for j in v]) for k, v in jobs.items()}
    Fmix = {"fcc": F["fcc"] - T*smix, "b32": F["b32"] - T*smix, "lqd": F["lqd"]}
    fits = {k: np.polyfit(comp, Fmix[k], 3) for k in Fmix}
    return F, Fmix, fits

rows = ["phase\tx_nominal\tx_actual\tF_800K_eV_per_atom\tF_900K\tF_1000K"]
for k in jobs:
    for i in range(6):
        rows.append(f"{k}\t{comp[i]:.1f}\t{xreal[k][i]:.4f}\t{fe_at(jobs[k][i],800):.5f}\t{fe_at(jobs[k][i],900):.5f}\t{fe_at(jobs[k][i],1000):.5f}")
open(os.path.join(OUT, "free_energies.tsv"), "w").write("\n".join(rows) + "\n")

# --- tutorial figures at 800, 900, 950 K ---
tangent_log = []
for T, pairs in [(800, [("fcc", "b32", [0.0, 0.25])]), (900, [("fcc", "b32", [0.0, 0.25])]),
                 (950, [("fcc", "lqd", [0.1, 0.3]), ("b32", "lqd", [0.3, 0.5])])]:
    F, Fmix, fits = curves(T)
    fe = {k: np.polyval(fits[k], grid) for k in fits}
    lqd_norm, m, c = normalise_fe(fe["lqd"], grid)
    norm = {k: fe[k] - (m*grid + c) for k in fe}
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for k in ("fcc", "lqd", "b32"):
        ax[0].plot(comp, Fmix[k], "o", color=colors[k], markeredgecolor="#424242", label=k)
        ax[0].plot(grid, fe[k], "-", color=colors[k])
        ax[1].plot(grid, norm[k], "-", color=colors[k], label=k)
    for a, b, guess in pairs:
        ct = find_common_tangent(fits[a], fits[b], guess)
        tangent_log.append(f"{T}\t{a}-{b}\t{ct[0]:.4f}\t{ct[1]:.4f}")
        ax[1].plot(ct, [np.polyval(fits[a], ct[0]) - (m*ct[0]+c), np.polyval(fits[b], ct[1]) - (m*ct[1]+c)], color="#424242")
    ax[0].set(xlabel=r"$x_{Li}$", ylabel="F + ideal mixing (eV/atom)", title=f"{T} K: fits (ideal S_conf added to fcc, B32)")
    ax[1].set(xlabel=r"$x_{Li}$", ylabel="F - liquid end-point line (eV/atom)", title=f"{T} K: common tangents (tutorial fsolve)")
    ax[0].legend(); ax[1].legend(); fig.tight_layout(); fig.savefig(os.path.join(OUT, f"free_energy_{T}K.png"), dpi=130); plt.close(fig)
open(os.path.join(OUT, "common_tangents_tutorial.tsv"), "w").write("T_K\tpair\tx1\tx2\n" + "\n".join(tangent_log) + "\n")

# --- T-x diagram from the lower convex hull of the three fitted curves ---
def hull_regions(T, npts=501):
    _, _, fits = curves(T)
    xs = np.linspace(0, 0.5, npts)
    pts, lab = [], []
    for k in ("fcc", "b32", "lqd"):
        pts.append(np.c_[xs, np.polyval(fits[k], xs)]); lab += [k]*npts
    pts = np.vstack(pts); lab = np.array(lab)
    # relative to the liquid end-point line so the hull is numerically well conditioned
    m = (pts[-1, 1] - pts[2*npts, 1]) / 0.5; pts[:, 1] -= m*pts[:, 0]
    hull = ConvexHull(pts)
    # lower envelope: walk the hull vertices sorted by x, keep left turns only
    v = hull.vertices
    idx = sorted(v, key=lambda i: pts[i, 0])
    env = []
    for i in idx:
        while len(env) >= 2:
            a, b = pts[env[-2]], pts[env[-1]]; p = pts[i]
            if (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0]) <= 0: env.pop()
            else: break
        env.append(i)
    regions = []  # (x_left, x_right, kind)
    for i, j in zip(env[:-1], env[1:]):
        dx = pts[j, 0] - pts[i, 0]
        if lab[i] != lab[j] or dx > 1.5*(0.5/(npts-1)):
            regions.append((pts[i, 0], pts[j, 0], f"{lab[i]}+{lab[j]}"))
    return regions

Ts = np.arange(800, 1001, 5)
dT = 5
regions = []  # (T, x_left, x_right, kind) with kind ordered alphabetically so "fcc+b32" == "b32+fcc"
for T in Ts:
    for xl, xr, kind in hull_regions(T):
        if xr - xl < 1e-6: continue  # coincident end points of two curves at x=0 or x=0.5, not a region
        a, b = kind.split("+"); kind = "+".join(sorted([a, b])) if a != b else f"{a}+{a} (gap)"
        regions.append((T, xl, xr, kind))
cmap = {"b32+fcc": "#9e9e9e", "fcc+lqd": "#ef9a9a", "b32+lqd": "#ffe082"}
fig, ax = plt.subplots(figsize=(6.5, 5))
seen = set()
for T, xl, xr, kind in regions:  # one horizontal band per temperature and region: no polygon across temperatures
    ax.fill_betweenx([T - dT/2, T + dT/2], xl, xr, color=cmap.get(kind, "#bdbdbd"), alpha=0.75,
                     linewidth=0, label=None if kind in seen else kind); seen.add(kind)
ax.set(xlim=(0, 0.5), ylim=(800, 1000), xlabel=r"$x_{Li}$", ylabel="Temperature (K)",
       title="Al-Li (workshop EAM): two-phase regions from the lower hull of fitted F(x)")
ax.legend(fontsize=8, loc="upper right"); fig.tight_layout(); fig.savefig(os.path.join(OUT, "phase_diagram_Tx.png"), dpi=130)
lines = ["T_K\tregion\tx_left\tx_right"] + [f"{T:.0f}\t{kind}\t{xl:.4f}\t{xr:.4f}" for T, xl, xr, kind in regions]
open(os.path.join(OUT, "two_phase_regions.tsv"), "w").write("\n".join(lines) + "\n")
print("\n".join(tangent_log)); print("regions written:", len(lines)-1)
