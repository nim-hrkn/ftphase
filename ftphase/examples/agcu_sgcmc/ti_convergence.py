"""Why does the calphy TI route put the EAM Ag melting point at 1320-1330 K when coexistence MD gives 1265-1290 K
(authors: 1267 K)?  Convergence test of the solid and liquid Frenkel-Ladd / UFM free energies of pure Ag at
1275 K (inside the coexistence bracket, so G_solid - G_liquid should be about 0 +/- 1 meV/atom):

    cell size   256 (4x4x4, the production setting) vs 2048 atoms (8x8x8)
    switching   10000 (production) vs 50000 steps, 3 iterations

    python ti_convergence.py prepare     -> calphy_ti/input_ti.yaml (8 fe blocks)
    python ti_convergence.py submit      -> calphy -i input_ti.yaml (Slurm, 4 ranks each, env/ftphase)
    python ti_convergence.py analyse     -> out/ti_convergence.md  (G per atom, error, G_s - G_l per setting)
"""

import argparse
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "potentials/agcu/CuAg.eam.alloy")
CAL = os.path.join(HERE, "calphy_ti")
T = 1275.0


def prepare():
    from ase.build import bulk

    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    from ftphase.structures import write_lammps_data

    os.makedirs(CAL, exist_ok=True)
    blocks = []
    q = slurm_queue(os.path.join(ROOT, "env/ftphase"), cores=4, memory="8GB")
    for n_rep, n_atoms in ((4, 256), (8, 2048)):
        at = bulk("Ag", "fcc", a=4.09, cubic=True).repeat((n_rep, n_rep, n_rep))
        data = write_lammps_data(at, os.path.join(CAL, f"ag_{n_atoms}.data"), ["Ag", "Cu"])
        for n_sw in (10000, 50000):
            for ph in ("solid", "liquid"):
                tag = f"{ph[:3]}_{n_atoms}_{n_sw // 1000}k"
                blocks.append(calculation_block(tag, "fe", ["Ag", "Cu"], [107.8682, 63.546], data, "eam/alloy", f"* * {POT} Ag Cu", T, pressure=0,
                                                reference_phase=ph, n_equilibration_steps=10000, n_switching_steps=n_sw, n_iterations=3, queue=q, folder_prefix=tag))
    write_series_input(os.path.join(CAL, "input_ti.yaml"), blocks)
    print(f"{len(blocks)} calphy fe blocks -> {CAL}/input_ti.yaml")


def submit():
    env = dict(os.environ)
    env["PATH"] = os.path.join(ROOT, "env/ftphase/bin") + os.pathsep + env["PATH"]
    r = subprocess.run(["calphy", "-i", "input_ti.yaml"], cwd=CAL, env=env, capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-2000:])
    print(subprocess.run(["squeue", "-u", os.environ.get("USER", ""), "-o", "%.7i %.28j %.9T %.6M"], capture_output=True, text=True).stdout)


def analyse():
    import yaml

    rows = {}
    for d in sorted(glob.glob(os.path.join(CAL, "*-fe-*/"))):
        rp = os.path.join(d, "report.yaml")
        if not os.path.exists(rp):
            continue
        rep = yaml.safe_load(open(rp))
        tag = os.path.basename(d.rstrip("/")).split("-fe-")[0]
        rows[tag] = (rep["results"]["free_energy"], rep["results"]["error"], rep["results"].get("reference_system"), rep["results"].get("work"))
    L = [f"# calphy fe convergence, pure Ag (EAM Williams 2006) at {T:.0f} K; coexistence MD bracket 1265-1290 K -> G_s - G_l should be ~ 0", "",
         "| cell | switching | G_solid (eV/atom) | G_liquid (eV/atom) | G_s - G_l (meV/atom) | errors (meV) |", "|---|---|---|---|---|---|"]
    for n_atoms in (256, 2048):
        for k in ("10k", "50k"):
            s_ = rows.get(f"sol_{n_atoms}_{k}"); l_ = rows.get(f"liq_{n_atoms}_{k}")
            if s_ and l_:
                L.append(f"| {n_atoms} | {k} | {s_[0]:.5f} | {l_[0]:.5f} | {(s_[0] - l_[0]) * 1000:+.2f} | {s_[1] * 1000:.2f} / {l_[1] * 1000:.2f} |")
            else:
                L.append(f"| {n_atoms} | {k} | {'ok' if s_ else 'missing'} | {'ok' if l_ else 'missing'} | | |")
    L += ["", "A positive G_s - G_l at 1275 K means the TI route makes the liquid too unstable (melting point too high).",
          "The entropy of fusion of Ag is about 1.1 k_B, so 1 meV/atom corresponds to about 10 K."]
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    with open(os.path.join(HERE, "out", "ti_convergence.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prepare", "submit", "analyse"]); a = ap.parse_args()
    {"prepare": prepare, "submit": submit, "analyse": analyse}[a.cmd]()
