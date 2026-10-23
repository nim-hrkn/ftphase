"""Examples 3/4 revisited: the ACE Al melting point from calphy TI with a 2048-atom solid cell.

The 256-atom solid Frenkel-Ladd cells of examples 3/4 carry a finite-size error of several meV/atom
(agcu_sgcmc/ti_convergence.py: +50-60 K on the melting point for EAM Ag).  Here fcc Al is run as an
8x8x8 cell (2048 atoms) with calphy reversible scaling 800 -> 1000 K on the GPU; the liquid comes from
the three 256-atom x = 0 sweeps of examples 5/6 (1100 -> 700 K; the liquid route is converged at 256).

    python alli_ace_melting_2048.py prepare   -> calphy_ace_melt2048/input.yaml (+ submit with calphy -i)
    python alli_ace_melting_2048.py analyse   -> out_alli_ace/melting_2048.md: crossing T of the 2048-atom solid
                                                  and of the 256-atom solid (example 4) with the liquid
"""

import glob
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LMP_GPU = os.path.join(ROOT, "env/lammps-gpu/bin/lmp_gpu")
ENV = os.path.join(ROOT, "env/ftphase")
CAL = os.path.join(HERE, "calphy_ace_melt2048")
OUT = os.path.join(HERE, "out_alli_ace")
LIQ_DIRS = sorted(glob.glob(os.path.join(HERE, "alli_ace_txdiagram/calphy_liquid/lqd_x0.00-ts-*/")) + glob.glob(os.path.join(HERE, "alli_ace_txdiagram/calphy_liquid_more/lqd_x0.00_r*-ts-*/")))
SOLID256 = sorted(glob.glob(os.path.join(HERE, "calphy_ace_gpu/fcc_x0-ts-*/")) + glob.glob(os.path.join(HERE, "calphy_ace_gpu_repeat/fcc_x0*-ts-*/")))


def prepare():
    from ase.build import bulk

    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    from ftphase.structures import write_lammps_data

    os.makedirs(CAL, exist_ok=True)
    at = bulk("Al", "fcc", a=4.05, cubic=True).repeat((8, 8, 8))
    data = write_lammps_data(at, os.path.join(CAL, "fcc_al_2048.data"), ["Al", "Li"])
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks = [calculation_block("fcc2048", "ts", ["Al", "Li"], [26.9815, 6.94], data, "pace", f"* * {POT} Al Li", [800.0, 1000.0], pressure=0,
                                reference_phase="solid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=2, queue=q,
                                folder_prefix="fcc2048", gpu=True, lammps_executable=LMP_GPU)]
    write_series_input(os.path.join(CAL, "input.yaml"), blocks)
    env = dict(os.environ); env["PATH"] = os.path.join(ENV, "bin") + os.pathsep + env["PATH"]
    r = subprocess.run(["calphy", "-i", "input.yaml"], cwd=CAL, env=env, capture_output=True, text=True)
    print(r.stdout[-800:], r.stderr[-800:])


def _sweep(d):
    a = np.loadtxt(os.path.join(d, "temperature_sweep.dat"), ndmin=2)
    o = np.argsort(a[:, 0]); return a[o, 0], a[o, 1]


def _cross(Ts, Gs, Tl, Gl):
    lo, hi = max(Ts.min(), Tl.min()), min(Ts.max(), Tl.max()); T = np.linspace(lo, hi, 4000)
    d = np.interp(T, Ts, Gs) - np.interp(T, Tl, Gl)
    i = np.where(np.diff(np.sign(d)) != 0)[0]
    return ([float(T[j]) for j in i], (lo, hi), d)


def analyse():
    liq = [_sweep(d) for d in LIQ_DIRS if os.path.exists(os.path.join(d, "temperature_sweep.dat"))]
    Tl = liq[0][0]; Gl = np.mean([np.interp(Tl, t, g) for t, g in liq], axis=0)
    L = ["# ACE Al melting point: calphy solid TI with 2048 vs 256 atoms, liquid = mean of %d 256-atom sweeps (x = 0)" % len(liq), "",
         "| solid cell | sweep (K) | crossing with the liquid (K) | G_s - G_l at 900 K (meV/atom) |", "|---|---|---|---|"]
    for label, dirs in (("2048 atoms (this run)", sorted(glob.glob(os.path.join(CAL, "fcc2048-ts-*/")))), ("256 atoms (examples 3/4)", SOLID256)):
        for d in dirs:
            if not os.path.exists(os.path.join(d, "temperature_sweep.dat")):
                continue
            Ts, Gs = _sweep(d)
            c, (lo, hi), dd = _cross(Ts, Gs, Tl, Gl)
            d900 = float(np.interp(900.0, Ts, Gs) - np.interp(900.0, Tl, Gl)) * 1000 if lo <= 900 <= hi else float("nan")
            L.append(f"| {label} ({os.path.basename(d.rstrip('/'))[:30]}) | {Ts.min():.0f}-{Ts.max():.0f} | {', '.join(f'{v:.0f}' for v in c) or 'none in overlap'} | {d900:+.2f} |")
    L += ["", "Experiment 933.5 K; the QHA route of example 6 (mesh 60 A) gives 896 K; the 256-atom TI of example 4 gave 902-927 K across seeds."]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "melting_2048.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"prepare": prepare, "analyse": analyse}[sys.argv[1]]()
