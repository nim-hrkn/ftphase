"""Compare the ML-IAP run in this folder with the example-8 `pair_style mace` job (pk 4356).

Prints G(T) from report.yaml / temperature_sweep.dat at a few temperatures, the difference in meV/atom,
and the LAMMPS time per 10000-step segment of both jobs.  Writes compare.md.
"""
import glob
import os
import re
import sys

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REF = "/home/kino/aiida_run/ftphase/b0/7b/edaa-1e7f-40d7-8e83-2df70be3b9bd"   # CalcJob pk 4356 (alli_mace_mpa_0, lqd_x0.00)
TEMPS = [1100, 1000, 900, 800, 700]


def job_dir(root):
    d = sorted(glob.glob(os.path.join(root, "lqd_x0.00-ts-*")))
    d = [x for x in d if os.path.isdir(x)]
    if not d:
        sys.exit(f"no calphy job folder under {root}")
    return d[0]


def sweep(d):
    a = np.loadtxt(os.path.join(d, "temperature_sweep.dat"))
    o = np.argsort(a[:, 0])
    return a[o, 0], a[o, 1], a[o, 2]


def g_at(d, T):
    t, g, e = sweep(d)
    return float(np.interp(T, t, g)), float(np.interp(T, t, e))


def seg_times(d):
    """(file, loop time, steps) of every MLIP segment >= 10000 steps.  calphy overwrites *.log.lammps per
    iteration, so these are samples, not the whole job; the pure-UFM reference run (< 1 s) is skipped."""
    out = []
    for f in sorted(glob.glob(os.path.join(d, "*.log.lammps"))):
        for m in re.finditer(r"Loop time of ([\d.eE+-]+) on (\d+) procs for (\d+) steps", open(f).read()):
            if int(m.group(3)) >= 10000 and float(m.group(1)) > 100.0:
                out.append((os.path.basename(f), float(m.group(1)), int(m.group(3))))
    return out


def wall_hours(d):
    ts = []
    for line in open(os.path.join(d, "calphy.log")):
        m = re.match(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", line)
        if m:
            ts.append(m.group(1))
    if len(ts) < 2:
        return float("nan")
    from datetime import datetime
    f = "%Y-%m-%d %H:%M:%S"
    return (datetime.strptime(ts[-1], f) - datetime.strptime(ts[0], f)).total_seconds() / 3600.0


rows = []
for label, root in (("pair_style mace fp32 (pk 4356)", REF), ("ML-IAP unified fp32 (this run)", HERE)):
    d = job_dir(root)
    rep = yaml.safe_load(open(os.path.join(d, "report.yaml")))
    segs = seg_times(d)
    sps = [t / n for _, t, n in segs]
    rows.append(dict(label=label, dir=d, report=rep, segs=segs,
                     s_per_step=float(np.median(sps)) if sps else float("nan"),
                     total_h=wall_hours(d),
                     G={T: g_at(d, T) for T in TEMPS}))

lines = ["# MACE-MPA-0 fp32 Al liquid 1100->700 K: ML-IAP unified vs pair_style mace (calphy ts, 256 atoms)", ""]
lines.append("| | " + " | ".join(r["label"] for r in rows) + " | diff (meV/atom) |")
lines.append("|---|" + "---|" * (len(rows) + 1))
r0 = rows[0]["report"]["results"]
r1 = rows[1]["report"]["results"]
for key in ("free_energy", "work", "reference_system", "dissipation", "ts_dissipation", "error"):
    v0, v1 = float(r0[key]), float(r1[key])
    lines.append(f"| {key} at 1100 K (eV/atom) | {v0:.6f} | {v1:.6f} | {1000*(v1-v0):+.2f} |")
for T in TEMPS:
    (g0, e0), (g1, e1) = rows[0]["G"][T], rows[1]["G"][T]
    lines.append(f"| G({T} K) (eV/atom) | {g0:.6f} ± {e0:.5f} | {g1:.6f} ± {e1:.5f} | {1000*(g1-g0):+.2f} |")
for r in rows:
    av = r["report"]["average"]
    lines.append(f"| vol/atom at 1100 K (Å^3) {r['label'].split('(')[0].strip()} | {av['vol_atom']:.4f} | | |")
lines.append("")
lines.append("| | " + " | ".join(r["label"] for r in rows) + " |")
lines.append("|---|---|---|")
lines.append("| LAMMPS s/step (median of the logged 10000-step MLIP segments) | " + " | ".join(f"{r['s_per_step']:.4f}" for r in rows) + " |")
lines.append("| logged segments | " + " | ".join(str(len(r['segs'])) for r in rows) + " |")
lines.append("| calphy wall time (h, calphy.log first to last line) | " + " | ".join(f"{r['total_h']:.2f}" for r in rows) + " |")
lines.append("")
lines.append(f"reference job dir: {rows[0]['dir']}")
lines.append(f"this run: {rows[1]['dir']}")
lines.append("The pk 4356 job shared the GPU with other AiiDA jobs at times; its s/step is an upper bound.")
txt = "\n".join(lines)
print(txt)
open(os.path.join(HERE, "compare.md"), "w").write(txt + "\n")
