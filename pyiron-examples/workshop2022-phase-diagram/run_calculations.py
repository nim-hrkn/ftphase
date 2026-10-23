"""Run the calculations of pyiron potentials-workshop-2022 phase_diagram/tutorial_2.ipynb
(Al-Li with the workshop EAM 'LiAl-atomicrex'), same settings as the tutorial:
4x4x4 fcc (256 atoms), B32 cell from AlLi_poscar (432 atoms), T = 800-1000 K reversible scaling,
5000 equilibration / 5000 switching steps. Jobs run 4 at a time, 4 cores each, in project 'phase_diagram'; each job gets its own cwd under scratch/.
Environment: PYIRONRESOURCEPATHS=<this dir>/resources, PYIRONDISABLE=True (no sqlite), PYIRONPROJECTCHECKENABLED=False
"""
import os, sys, time, numpy as np
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PYIRONRESOURCEPATHS", os.path.join(HERE, "resources"))
os.environ.setdefault("PYIRONDISABLE", "True")
os.environ.setdefault("PYIRONPROJECTCHECKENABLED", "False")
os.chdir(HERE)
sys.path.insert(0, HERE)
CORES = 4
T_RANGE = [800, 1000]
N_EQ, N_SW = 5000, 5000
COMPS = [0.1, 0.2, 0.3, 0.4, 0.5]
DISABLE_PHASE_CHECKS = "--disable-phase-checks" in sys.argv
ONLY = [a.split("=",1)[1].split(",") for a in sys.argv if a.startswith("--only=")]
ONLY = ONLY[0] if ONLY else None

def run_one(args):
    name, kind, comp, seed = args
    from pyiron_atomistics import Project
    from helpers import create_structures
    pr = Project(os.path.join(HERE, "phase_diagram"))
    # calphy writes '<mode>-conf.data-<phase>-<T>-<P>.<i>.data' into the current directory; with several jobs
    # running at once they would overwrite each other, so give every job its own working directory
    wd = os.path.join(HERE, "scratch", name); os.makedirs(wd, exist_ok=True); os.chdir(wd)
    if name in pr.list_nodes():
        j = pr.load(name)
        if j.status == "finished":
            return name, "already finished", 0.0
        j.remove()
    np.random.seed(seed)  # the random substitution in helpers.create_structures
    if comp is None:  # pure Al
        if kind == "alli":
            structure = pr.create.structure.ase.read(os.path.join(HERE, "LiAl_poscar"), format="vasp"); structure[:] = "Al"
        else:
            structure = pr.create.structure.ase.bulk("Al", cubic=True, a=4.135).repeat(4)
        potential = "Al-atomicrex"
    else:
        fcc, b32 = create_structures(pr, comp, repetitions=4)
        structure = b32 if kind == "alli" else fcc
        potential = "LiAl-atomicrex"
    job = pr.create.job.Calphy(name, delete_aborted_job=True)
    job.structure = structure
    job.potential = potential
    job.server.cores = CORES
    job.calc_free_energy(temperature=T_RANGE, pressure=0,
                         reference_phase="liquid" if kind == "lqd" else "solid",
                         n_equilibration_steps=N_EQ, n_switching_steps=N_SW)
    if DISABLE_PHASE_CHECKS:
        # calphy >= 2 aborts a solid that melts (MeltedError) or a liquid that solidifies (SolidifiedError).
        # calphy 1.0.3 used in the 2022 workshop had no such check; xp_alli (Al in the B32 lattice) and
        # x3_lqd hit it, so the checks are switched off as documented in calphy's input.py.
        job.input.tolerance["solid_fraction"] = 0.0
        job.input.tolerance["liquid_fraction"] = 1.0
    t0 = time.time()
    try:
        job.run()
        st = str(job.status)
    except Exception as e:
        st = f"ERROR {type(e).__name__}: {e}"
    return name, st, time.time() - t0

if __name__ == "__main__":
    tasks = [("xp_sol", "sol", None, 0), ("xp_lqd", "lqd", None, 0), ("xp_alli", "alli", None, 0)]
    for i, c in enumerate(COMPS):
        for kind in ("sol", "lqd", "alli"):
            tasks.append((f"x{i}_{kind}", kind, c, 1000 + i))
    if ONLY: tasks = [t for t in tasks if t[0] in ONLY]
    print(f"{len(tasks)} jobs, 4 concurrent x {CORES} cores, phase checks {'OFF' if DISABLE_PHASE_CHECKS else 'on'}", flush=True)
    with ProcessPoolExecutor(max_workers=4) as ex:
        for name, st, wall in ex.map(run_one, tasks):
            print(f"[{time.strftime('%H:%M:%S')}] {name:10s} {st:20s} {wall:7.1f} s", flush=True)
    print("ALL DONE", flush=True)
