"""Post-processing of 02_EAM_phase_diagram.ipynb (Menon et al. 2024, Al-Li, EAM) with calphy 2.3.0.
Differences from the 2024 notebook: the table job is found by name instead of pk 2998; the EAM dataset
contains only fcc, b32 and liquid (no al3li), so that phase is skipped; plot_phase_diagram now needs the
tangent types and the phase list; temperature step 2 K instead of 1 K.
"""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
os.environ.setdefault("PYIRONRESOURCEPATHS", os.path.join(HERE, "resources"))
os.environ.setdefault("PYIRONSQLFILE", os.path.join(HERE, "pyiron.db"))
os.environ.setdefault("PYIRONPROJECTCHECKENABLED", "False")
import calphy.phase_diagram as ph
from pyiron_atomistics import Project
pr = Project("phase_diagram_eam")
jt = pr.job_table(recursive=True)
df = pr.load(int(jt[jt.hamilton == "TableJob"].iloc[0].id)).get_dataframe()
print("rows", len(df), "phases", sorted(df.phase.unique()))
spec = {"fcc": dict(ideal_configurational_entropy=True, entropy_correction=0.00, composition_cutoff=0.03),
        "liquid": dict(ideal_configurational_entropy=False, composition_cutoff=0.03),
        "b32": dict(ideal_configurational_entropy=True, entropy_correction=0.5, composition_cutoff=0.03),
        "al3li": dict(ideal_configurational_entropy=True, entropy_correction=0.25, composition_cutoff=0.03,
                      composition_interval=(0.24, 0.26), fit_order=2)}
phases = [p for p in ["fcc", "liquid", "b32", "al3li"] if p in set(df.phase)]
temps = np.arange(700, 901, 2)
tangents, ttypes, used_T = [], [], []
for T in temps:
    dl = [ph.get_phase_free_energy(df, p, T, plot=False, **spec[p]) for p in phases]
    dl = ph.get_free_energy_mixing(dl)
    tn, _, tt, _ = ph.get_common_tangents(dl, remove_self_tangents_for=["liquid-liquid"])
    tangents.append(tn); ttypes.append(tt); used_T.append(T)
fig = ph.plot_phase_diagram(tangents, used_T, ttypes, phases)
ax = plt.gca(); ax.set_xlabel(r"$x_\mathrm{Li}$"); ax.set_ylabel("Temperature (K)"); ax.set_xlim(0, 0.5); ax.set_ylim(700, 900)
ax.set_title("Al-Li, EAM (Menon et al. 2024 dataset), calphy 2.3.0 post-processing")
plt.savefig("phase_diagram_eam.png", dpi=140, bbox_inches="tight")
with open("two_phase_regions_eam.tsv", "w") as f:
    f.write("T_K\tpair\tx1\tx2\n")
    for T, tn, tt in zip(used_T, tangents, ttypes):
        for pair, lab in zip(tn, tt): f.write(f"{T}\t{lab}\t{pair[0]:.4f}\t{pair[1]:.4f}\n")
print("tangent types seen:", sorted({l for tt in ttypes for l in tt})); print("done")
