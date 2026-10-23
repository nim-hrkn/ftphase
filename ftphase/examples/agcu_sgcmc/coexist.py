"""Solid-liquid coexistence MD (interface method) for pure Ag and Cu with the Williams-Mishin-Hamilton 2006 EAM:
an independent check of the melting points from the calphy TI route (A), which came out 40-60 K above the
authors' interface Monte Carlo values (Ag 1267 K, Cu 1327 K; Williams et al. 2006 p. 830).

    python coexist.py prepare      write runs_coexist/<El>_T<T>/in.coex for T on a grid around the two estimates
    python coexist.py submit       sbatch them on this host (CPU, 4 ranks each, env/ftphase mpirun)
    python coexist.py analyse      slope of the solid fraction (via the per-atom energy) -> melting bracket

Protocol per run: fcc 8x8x24 cells (6144 atoms); stage 1 equilibrates the whole solid at T under NPT iso to get
a(T); stage 2 melts the upper half (z > Lz/2) at 2.0 T_est with the lower half frozen; stage 3 runs the whole box at
T with NPT coupled along z only for 400 ps and records the mean potential energy per atom every 10 ps.  Below T_m
the solid grows and pe decreases; above T_m the liquid grows and pe increases.  The bracket is the T where the
slope changes sign.
"""

import argparse
import glob
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "potentials/agcu/CuAg.eam.alloy")
RUNS = os.path.join(HERE, "runs_coexist")
ELEMENTS = {"Ag": {"a": 4.09, "mass": 107.8682, "type": 1, "T": [1240, 1265, 1290, 1315, 1340]},
            "Cu": {"a": 3.615, "mass": 63.546, "type": 2, "T": [1300, 1325, 1350, 1375, 1400]}}


def lammps_input(el, T):
    e = ELEMENTS[el]
    return f"""# coexistence MD {el} T={T} K
units metal
atom_style atomic
boundary p p p
lattice fcc {e['a']}
region box block 0 8 0 8 0 24
create_box 2 box
create_atoms {e['type']} box
mass 1 107.8682
mass 2 63.546
pair_style eam/alloy
pair_coeff * * {POT} Ag Cu
timestep 0.002
velocity all create {T} 4711 loop geom
# stage 1: solid at T, isotropic NPT -> lattice parameter at T
fix s1 all npt temp {T} {T} 0.2 iso 0.0 0.0 2.0
thermo 1000
run 10000
unfix s1
# stage 2: melt the upper half, lower half frozen
region upper block INF INF INF INF $(lz/2) INF units box
group upper region upper
group lower subtract all upper
fix fr lower setforce 0.0 0.0 0.0
velocity upper create {2.0 * T} 1234 loop geom
fix s2 upper nvt temp {2.0 * T} {2.0 * T} 0.2
run 15000
unfix s2
velocity upper create {T} 777 loop geom
fix s2b upper nvt temp {T} {T} 0.2
run 5000
unfix s2b
unfix fr
# stage 3: whole box at T, NPT coupled along z only; record pe/atom every 10 ps
velocity all scale {T}
fix s3 all npt temp {T} {T} 0.2 z 0.0 0.0 2.0
variable epa equal pe/atoms
fix avg all ave/time 100 50 5000 v_epa file pe.dat
thermo 5000
thermo_style custom step temp pe lz v_epa
run 200000
"""


def prepare():
    os.makedirs(RUNS, exist_ok=True)
    tags = []
    for el, e in ELEMENTS.items():
        for T in e["T"]:
            d = os.path.join(RUNS, f"{el}_T{T}")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "in.coex"), "w") as f:
                f.write(lammps_input(el, T))
            tags.append(f"{el}_T{T}")
    print("prepared", tags)
    return tags


def submit(ranks=4):
    jobs = {}
    for d in sorted(glob.glob(os.path.join(RUNS, "*_T*"))):
        tag = os.path.basename(d)
        cmd = ["sbatch", "--parsable", "-p", "debug", "-n", str(ranks), "--hint=nomultithread", "--mem=4GB", "-J", f"coex_{tag}", f"--chdir={d}",
               "-o", "slurm.out", "-e", "slurm.err", "--wrap", f"{ROOT}/env/ftphase/bin/mpirun -np {ranks} {ROOT}/env/ftphase/bin/lmp_mpi -in in.coex -log log.lammps -screen none"]
        jobs[tag] = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        print(tag, jobs[tag])
    with open(os.path.join(RUNS, "jobs.json"), "w") as f:
        json.dump(jobs, f, indent=1)


def analyse():
    rows = []
    for d in sorted(glob.glob(os.path.join(RUNS, "*_T*"))):
        p = os.path.join(d, "pe.dat")
        if not os.path.exists(p):
            continue
        a = np.loadtxt(p, comments="#", ndmin=2)
        if len(a) < 10:
            continue
        t = a[:, 0] * 0.002 / 1000.0     # ps -> ns
        pe = a[:, 1]
        half = len(a) // 2
        slope = np.polyfit(t[half:], pe[half:], 1)[0]      # eV/atom per ns over the second half
        tag = os.path.basename(d); el, T = tag.split("_T")
        rows.append({"element": el, "T": float(T), "slope_meV_per_atom_per_ns": slope * 1000, "pe_start": pe[0], "pe_end": pe[-1], "n": len(a)})
    rows.sort(key=lambda r: (r["element"], r["T"]))
    L = ["| element | T (K) | d(pe)/dt (meV/atom/ns, 2nd half) | pe start -> end (eV/atom) | verdict |", "|---|---|---|---|---|"]
    for r in rows:
        v = "solid grows (T < Tm)" if r["slope_meV_per_atom_per_ns"] < -0.5 else ("liquid grows (T > Tm)" if r["slope_meV_per_atom_per_ns"] > 0.5 else "stationary (T ~ Tm)")
        L.append(f"| {r['element']} | {r['T']:.0f} | {r['slope_meV_per_atom_per_ns']:+.2f} | {r['pe_start']:.4f} -> {r['pe_end']:.4f} | {v} |")
    out = "\n".join(L)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    with open(os.path.join(HERE, "out", "coexist_REPORT.md"), "w") as f:
        f.write("# Solid-liquid coexistence MD (EAM Williams 2006): melting brackets of Ag and Cu\n\n" + out + "\n")
    print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prepare", "submit", "analyse"]); a = ap.parse_args()
    {"prepare": prepare, "submit": submit, "analyse": analyse}[a.cmd]()
