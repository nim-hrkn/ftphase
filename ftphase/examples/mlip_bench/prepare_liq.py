"""Liquid-only timing benchmark for MLIPs added after the 2026-10-29 batch (PET via metatomic, DPA-3 via deepmd plugin).

Same job as prepare.py's `liq`: calphy ts of lqd_x0.30 (256 atoms, 1100 -> 700 K, 10k + 10k/10k steps, 3 iterations),
1 MPI rank, exclusive GPU (--gres=gpu:1), 4 CPUs. The input.yaml and lqd_x0.30.data of runs/<host>/ace/liq are the template;
only pair_style / pair_coeff / cmdargs / lammps_executable change.

    python prepare_liq.py [--submit] [--only=pet-oam-l,pet-omat-s,dpa-3.1-3m-mptrj] [--host=mygarden5]
"""
import os, shutil, subprocess, sys, yaml
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
KK = "-k on g 1 -sf kk -pk kokkos newton on neigh half"
MLIPS = {  # name: (pair_style, pair_coeff, cmdargs, lammps_executable, potential file copied next to the input)
    "pet-oam-l": (f"metatomic __WORKDIR__/pet-oam-l-v0.1.0.pt", "* * 13 3", KK, f"{ROOT}/env/metatomic/bin/lmp_metatomic.sh", "potentials/pet/pet-oam-l-v0.1.0.pt"),
    "pet-omat-s": (f"metatomic __WORKDIR__/pet-omat-s-v1.0.0.pt", "* * 13 3", KK, f"{ROOT}/env/metatomic/bin/lmp_metatomic.sh", "potentials/pet/pet-omat-s-v1.0.0.pt"),
    # the Matbench DPA-3.1-3M-FT .pth was frozen with a private deepmd-kit dev version without the LAMMPS border_op (cannot be
    # re-frozen: unknown options such as use_torch_embed); used instead: the public pretrained DPA-3.1-3M, MPtrj branch, frozen
    # with deepmd-kit 3.1.3 (`dp --pt freeze --model-branch MP_traj_v024_alldata_mixu`), see env/deepmd/README.md
    # DPA4 (SeZM) OMat24 checkpoints from huggingface.co/deepmodelingcommunity/DPA4-OMat24 (v20260805, cc-by-nc-4.0, trained with deepmd-kit 3.2.0),
    # frozen on this GPU to AOTInductor .pt2 (`DP_TRITON_INFER=2 dp --pt freeze`, env/deepmd32); LAMMPS 22Jul2025u2 (PyPI wheel) + 3.2.0 plugin,
    # the wrapper prepends `plugin load` and `atom_modify map yes`.
    "dpa4-plus-omat24": ("deepmd __WORKDIR__/DPA4-Plus-OMat24-v20260805.pt2", "* * Al Li", "", f"{ROOT}/env/deepmd32/bin/lmp_deepmd.sh", "potentials/deepmd/dpa4/DPA4-Plus-OMat24-v20260805.pt2"),
    "dpa4-air-omat24": ("deepmd __WORKDIR__/DPA4-Air-OMat24-v20260805.pt2", "* * Al Li", "", f"{ROOT}/env/deepmd32/bin/lmp_deepmd.sh", "potentials/deepmd/dpa4/DPA4-Air-OMat24-v20260805.pt2"),
    "dpa4.1-max-oam": ("deepmd __WORKDIR__/dpa-4.1-max-oam.pt2", "* * Al Li", "", f"{ROOT}/env/deepmd41/bin/lmp_deepmd.sh", "potentials/deepmd/dpa4/dpa-4.1-max-oam.pt2"),
    "dpa-3.1-3m-mptrj": ("deepmd __WORKDIR__/dpa-3.1-3m-mptrj.pth", "* * Al Li", "", f"{ROOT}/env/deepmd/bin/lmp_deepmd.sh", "potentials/deepmd/dpa-3.1-3m-mptrj.pth"),
}


def stage(host, name):
    ps, pc, cmd, exe, pot = MLIPS[name]
    base = os.path.join(HERE, "runs", host, name); liq = os.path.join(base, "liq")
    shutil.rmtree(base, ignore_errors=True); os.makedirs(liq)
    tmpl = os.path.join(HERE, "runs", host, "ace", "liq")
    shutil.copy(os.path.join(tmpl, "lqd_x0.30.data"), liq)
    shutil.copy(os.path.join(ROOT, pot), liq)
    inp = yaml.safe_load(open(os.path.join(tmpl, "input.yaml")))
    c = inp["calculations"][0]
    c["lattice"] = os.path.join(liq, "lqd_x0.30.data")
    c["pair_style"] = ps; c["pair_coeff"] = pc; c["lammps_executable"] = exe
    if cmd:
        c["md"] = {"cmdargs": cmd}
    else:
        c.pop("md", None)
    yaml.safe_dump(inp, open(os.path.join(liq, "input.yaml"), "w"), sort_keys=False)
    sb = f"""#!/bin/bash
#SBATCH -J bench-{name} -p debug -N 1 -n 1 -c 4 --gres=gpu:1 --hint=nomultithread
#SBATCH -o {base}/slurm.out -e {base}/slurm.err
unset PYTHONPATH PYTHONHOME
source /home/kino/miniforge3/etc/profile.d/conda.sh
cd {liq} && conda activate {ROOT}/env/ftphase && sed -i "s|__WORKDIR__|$PWD|g" input.yaml
export CALPHY_SKIP_PREFLIGHT=1   # plugin styles (deepmd) are not visible to calphy's `lmp -h` style check
t0=$(date +%s.%N); {ROOT}/env/ftphase/bin/calphy_kernel -i input.yaml -k 0 > calphy.out 2> calphy.err; rc=$?; t1=$(date +%s.%N)
echo -e "$(hostname)\\t{name}\\tliq\\t$(echo "$t1-$t0" | bc)\\t$rc" >> {base}/times.tsv
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader >> {base}/times.tsv
"""
    open(os.path.join(base, "run.sbatch"), "w").write(sb)
    return os.path.join(base, "run.sbatch")


if __name__ == "__main__":
    only = [a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")]
    host = ([a.split("=", 1)[1] for a in sys.argv if a.startswith("--host=")] or ["mygarden5"])[0]
    names = only[0] if only else list(MLIPS)
    scripts = [stage(host, m) for m in names]
    print("staged", scripts)
    if "--submit" in sys.argv:
        for s in scripts:
            cmd = ["sbatch", s] if host == "mygarden5" else ["ssh", host, f"sbatch {s}"]
            print(host, subprocess.run(cmd, capture_output=True, text=True).stdout.strip())
