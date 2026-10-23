"""GPU vs CPU check for stage 03B: the same four calphy reversible-scaling runs
(ACE Al-Li, fcc / liquid, x = 0 and 0.1, 800-1000 K) executed by

* examples/calphy_ace/      conda-forge LAMMPS 22 Jul 2025, 4 MPI ranks (CPU);
* examples/calphy_ace_gpu/  LAMMPS 30 Sep 2026 KOKKOS/CUDA (env/lammps-gpu), 1 rank + RTX 3060,
                            input written by calphy_ace_gpu/make_input.py (calculation_block(gpu=True)).

Reports per run: wall time (first/last calphy.log timestamp), G at 800 K and the
maximum |G_gpu - G_cpu| over the common temperature grid.  Two independent
runs differ by their random seeds and MD statistics, so the difference is a
statistical one and is compared with calphy's own error estimate when it
reports one (n_iterations = 1 gives none), and with the ~1-2 meV/atom
spread expected for 5000-step switching of 256 atoms.
"""

import glob
import json
import os
import re
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CPU = os.path.join(HERE, "calphy_ace")
GPU = os.path.join(HERE, "calphy_ace_gpu")
CPU2 = os.path.join(HERE, "calphy_ace_repeat")      # same CPU setup, new seeds (pure Al only)
GPU2 = os.path.join(HERE, "calphy_ace_gpu_repeat")  # same GPU setup, new seeds (pure Al only)
OUT = os.path.join(HERE, "out_alli_ace")

from ftphase.calphy_io import read_calphy_results


def wall_seconds(folder):
    log = os.path.join(folder, "calphy.log")
    if not os.path.exists(log):
        return None
    ts = []
    with open(log) as f:
        for line in f:
            m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+", line)
            if m:
                ts.append(datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"))
    return (ts[-1] - ts[0]).total_seconds() if len(ts) > 1 else None


def crossing(T, dG):
    s = np.sign(dG)
    idx = np.where(np.diff(s) != 0)[0]
    if idx.size == 0:
        return None
    i = idx[0]
    return float(T[i] - dG[i] * (T[i + 1] - T[i]) / (dG[i + 1] - dG[i]))


def melting_point(df):
    """fcc_x0 vs lqd_x0 crossing on a 1 K grid, or None if a phase is missing."""
    sol = df[(df.phase == "fcc_x0")].sort_values("T"); liq = df[(df.phase == "lqd_x0")].sort_values("T")
    if sol.empty or liq.empty:
        return None
    T = np.arange(max(sol["T"].min(), liq["T"].min()), min(sol["T"].max(), liq["T"].max()) + 1e-9, 1.0)
    return crossing(T, np.interp(T, sol["T"], sol["G"]) - np.interp(T, liq["T"], liq["G"]))


def load(folder, tag):
    if not os.path.isdir(folder):
        return None
    try:
        df = read_calphy_results(folder, reference_element="Li", model="ACE AlLi-6gen-18May", source_prefix=tag + "/").df
    except Exception as e:  # folder exists but nothing finished yet
        print(tag, "not readable:", e)
        return None
    return df if len(df) else None


def main():
    cpu = load(CPU, "cpu"); gpu = load(GPU, "gpu")
    cpu2 = load(CPU2, "cpu-repeat"); gpu2 = load(GPU2, "gpu-repeat")
    res = {"runs": []}
    for ph in sorted(set(cpu.phase)):
        for x in sorted(set(cpu[cpu.phase == ph].x)):
            c = cpu[(cpu.phase == ph) & np.isclose(cpu.x, x)].sort_values("T")
            g = gpu[(gpu.phase == ph) & np.isclose(gpu.x, x)].sort_values("T")
            if c.empty or g.empty:
                continue
            T = np.arange(max(c["T"].min(), g["T"].min()), min(c["T"].max(), g["T"].max()) + 1e-9, 5.0)
            dG = np.interp(T, g["T"], g["G"]) - np.interp(T, c["T"], c["G"])
            fc = glob.glob(os.path.join(CPU, f"{ph}-ts-*/"))
            fg = glob.glob(os.path.join(GPU, f"{ph}-ts-*/"))
            res["runs"].append({
                "phase": ph, "x": float(x), "n_T": int(T.size),
                "G_cpu_800K_eV": float(np.interp(800.0, c["T"], c["G"])), "G_gpu_800K_eV": float(np.interp(800.0, g["T"], g["G"])),
                "dG_gpu_minus_cpu_800K_meV": float(dG[0] * 1000), "max_abs_dG_meV": float(np.abs(dG).max() * 1000),
                "mean_dG_meV": float(dG.mean() * 1000),
                "G_err_cpu_meV": float(c["G_err"].max() * 1000), "G_err_gpu_meV": float(g["G_err"].max() * 1000),
                "wall_cpu_s": wall_seconds(fc[0]) if fc else None, "wall_gpu_s": wall_seconds(fg[0]) if fg else None,
            })
    # run-to-run spread with new seeds (pure Al only) and the resulting melting point of each data set
    res["repeats"] = []
    for ph in ("fcc_x0", "lqd_x0"):
        base = cpu[cpu.phase == ph].sort_values("T")
        row = {"phase": ph}
        for tag, df in (("gpu", gpu), ("cpu_repeat", cpu2), ("gpu_repeat", gpu2)):
            if df is None:
                continue
            d = df[df.phase == ph].sort_values("T")
            if d.empty:
                continue
            T = np.arange(800.0, 1000.0 + 1e-9, 5.0)
            dG = np.interp(T, d["T"], d["G"]) - np.interp(T, base["T"], base["G"])
            row[f"{tag}_minus_cpu_meV_800_900_1000"] = [float(np.interp(t, T, dG) * 1000) for t in (800, 900, 1000)]
        res["repeats"].append(row)
    res["Tm_K"] = {tag: melting_point(df) for tag, df in (("cpu", cpu), ("gpu", gpu), ("cpu_repeat", cpu2), ("gpu_repeat", gpu2)) if df is not None}
    # all available independent samples per phase at 900 K -> standard deviation of G
    for ph in ("fcc_x0", "lqd_x0"):
        vals = []
        for df in (cpu, gpu, cpu2, gpu2):
            if df is None:
                continue
            d = df[df.phase == ph].sort_values("T")
            if not d.empty:
                vals.append(float(np.interp(900.0, d["T"], d["G"])))
        if len(vals) > 1:
            res[f"G_900K_std_meV_{ph}"] = float(np.std(vals, ddof=1) * 1000)
            res[f"G_900K_n_samples_{ph}"] = len(vals)
    res["note"] = ("CPU: LAMMPS 22Jul2025, 4 MPI ranks; GPU: LAMMPS 30Sep2026 KOKKOS/CUDA sm_86, 1 rank + RTX 3060, pace product. "
                   "Different random seeds, so dG is the run-to-run statistical spread, not a GPU/CPU numerical difference "
                   "(the single-point energies agree to all printed digits).")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "gpu_vs_cpu.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        for ph in sorted(set(cpu.phase)):
            for x in sorted(set(cpu[cpu.phase == ph].x)):
                c = cpu[(cpu.phase == ph) & np.isclose(cpu.x, x)].sort_values("T")
                g = gpu[(gpu.phase == ph) & np.isclose(gpu.x, x)].sort_values("T")
                if c.empty or g.empty:
                    continue
                T = np.arange(max(c["T"].min(), g["T"].min()), min(c["T"].max(), g["T"].max()) + 1e-9, 5.0)
                ax.plot(T, (np.interp(T, g["T"], g["G"]) - np.interp(T, c["T"], c["G"])) * 1000, label=f"{ph} x={x:.3f}")
        ax.axhline(0, color="k", lw=0.5)
        ax.set_xlabel("T (K)"); ax.set_ylabel("G_GPU - G_CPU (meV/atom)"); ax.legend(fontsize=8)
        ax.set_title("calphy ts, ACE Al-Li: KOKKOS/CUDA run minus CPU run")
        fig.savefig(os.path.join(OUT, "gpu_vs_cpu.png"), dpi=150, bbox_inches="tight")
    except Exception as e:  # pragma: no cover
        print("plot failed", e)


if __name__ == "__main__":
    main()
