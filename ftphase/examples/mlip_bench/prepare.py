"""Timing benchmark of the MLIPs under identical conditions on the GPU (RTX 3060, mygarden5 and mygarden6).

For each MLIP the same two jobs of the comparison WorkChains are rerun alone on an otherwise idle node:
  qha   = the QHA job of cell s03_fcc (32-atom fcc Al28Li4, phonopy 2x2x2 supercell = 256 atoms, 9 volumes,
          mesh 60 A, cell relaxation first), input.json of the original CalcJob, calculator on the GPU
  liq   = the calphy liquid job lqd_x0.30 (256 atoms, ts 1100 -> 700 K, 10k equilibration + 10k/10k switching,
          3 iterations), input.yaml of the original CalcJob, LAMMPS on the GPU, 1 MPI rank
Both run inside one Slurm job with --gres=gpu:1 and 4 CPUs (the QHA setting); wall times go to times.tsv.

    python prepare.py            -> runs/<host>/<mlip>/{qha,liq}/ + run.sbatch per MLIP
    python prepare.py --submit   also sbatch them (mygarden5 locally, mygarden6 over ssh)
"""
import json, os, shutil, subprocess, sys
from aiida import load_profile
load_profile("ftphase")
from aiida.orm import load_node

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
KK = ["-k", "on", "g", "1", "-sf", "kk", "-pk", "kokkos", "newton", "on", "neigh", "half"]
SEV = os.path.join(ROOT, "env/torch/lib/python3.12/site-packages/sevenn/pretrained_potentials")
MLIPS = {  # name: (qha CalcJob pk, liquid CalcJob pk, qha potential file, liquid potential file, qha env, qha overrides)
    "ace": (1572, 1598, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace",
            "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace", "ftphase",
            {"pair_style": "pace product", "cmdargs": KK}),
    "grace-fs": (1512, 1545, "potentials/grace/GRACE-FS-OAM.yaml", "potentials/grace/GRACE-FS-OAM.yaml", "ftphase",
                 {"pair_style": "grace/fs", "cmdargs": KK}),
    "sevenn-0": (3875, 3901, None, "potentials/sevenn/7net-0_oeq.pt", "torch", {"device": "cuda"}),
    "sevenn-mf-ompa": (3936, 3962, None, "potentials/sevenn/7net-mf-ompa_mpa_oeq.pt", "torch", {"device": "cuda"}),
}
HOSTS = ["mygarden5", "mygarden6"]


def stage(host, name):
    qpk, lpk, qpot, lpot, env, over = MLIPS[name]
    base = os.path.join(HERE, "runs", host, name)
    shutil.rmtree(base, ignore_errors=True)
    for sub, pk in (("qha", qpk), ("liq", lpk)):
        d = os.path.join(base, sub); os.makedirs(d)
        n = load_node(pk)
        for f in n.base.repository.list_object_names():
            if f in (".aiida", "_aiidasubmit.sh"):
                continue
            with open(os.path.join(d, f), "wb") as fh:
                fh.write(n.base.repository.get_object_content(f, mode="rb"))
    q = os.path.join(base, "qha", "input.json"); inp = json.load(open(q))
    if qpot is None:   # torch checkpoint: the file the original job received
        qpot = [os.path.join(SEV, s, f) for s in os.listdir(SEV) for f in os.listdir(os.path.join(SEV, s)) if f == inp["potential"]][0]
    else:
        qpot = os.path.join(ROOT, qpot)
    shutil.copy(qpot, os.path.join(base, "qha", os.path.basename(qpot))); inp["potential"] = os.path.basename(qpot)
    inp.update(over); json.dump(inp, open(q, "w"), indent=1)
    lp = os.path.join(ROOT, lpot); shutil.copy(lp, os.path.join(base, "liq", os.path.basename(lp)))
    sb = f"""#!/bin/bash
#SBATCH -J bench-{name} -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread --exclusive
#SBATCH -o {base}/slurm.out -e {base}/slurm.err
unset PYTHONPATH PYTHONHOME
source /home/kino/miniforge3/etc/profile.d/conda.sh
cd {base}/qha && conda activate {ROOT}/env/{env}
t0=$(date +%s.%N); {ROOT}/env/{env}/bin/ftphase-qha-run input.json > qha.out 2> qha.err; rc=$?; t1=$(date +%s.%N)
echo -e "$(hostname)\\t{name}\\tqha\\t$(echo "$t1-$t0" | bc)\\t$rc" >> {base}/times.tsv
conda deactivate
cd {base}/liq && conda activate {ROOT}/env/ftphase && sed -i "s|__WORKDIR__|$PWD|g" input.yaml
t0=$(date +%s.%N); {ROOT}/env/ftphase/bin/calphy_kernel -i input.yaml -k 0 > calphy.out 2> calphy.err; rc=$?; t1=$(date +%s.%N)
echo -e "$(hostname)\\t{name}\\tliq\\t$(echo "$t1-$t0" | bc)\\t$rc" >> {base}/times.tsv
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader >> {base}/times.tsv
"""
    open(os.path.join(base, "run.sbatch"), "w").write(sb)
    return os.path.join(base, "run.sbatch")


if __name__ == "__main__":
    scripts = {h: [stage(h, m) for m in MLIPS] for h in HOSTS}
    print("staged", sum(len(v) for v in scripts.values()), "jobs")
    if "--submit" in sys.argv:
        subprocess.run(["rsync", "-a", os.path.join(HERE, "runs", "mygarden6") + "/", f"mygarden6:{os.path.join(HERE, 'runs', 'mygarden6')}/"], check=True)
        for h, ss in scripts.items():
            for s in ss:
                cmd = ["sbatch", s] if h == "mygarden5" else ["ssh", h, f"sbatch {s}"]
                print(h, subprocess.run(cmd, capture_output=True, text=True).stdout.strip())
