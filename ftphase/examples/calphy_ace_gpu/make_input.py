"""Write the GPU counterpart of examples/calphy_ace/input_ace_ts.yaml.

Same four calphy reversible-scaling runs (fcc Al and fcc Al0.9Li0.1, solid and
liquid, 800-1000 K, 5000 + 5000 steps, ACE AlLi-6gen-18May) but executed by the
KOKKOS/CUDA LAMMPS in env/lammps-gpu (stable 30 Sep 2026, built by
env/lammps-gpu/build.sh) on the single RTX 3060 through Slurm --gres=gpu:1.
``calculation_block(gpu=True, lammps_executable=...)`` rewrites pace -> pace
product, sets md.cmdargs, cores=1 and refuses binaries without
hybrid/scaled/kk.  Run from this directory:

    ../../../env/ftphase/bin/python make_input.py
    source ../../../env/ftphase/bin/activate; calphy -i input_ace_gpu.yaml
"""

import os
import shutil

from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input, gpu_capability

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CPU_DIR = os.path.join(HERE, "..", "calphy_ace")
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LMP_GPU = os.path.join(ROOT, "env/lammps-gpu/bin/lmp_gpu")
ENV = os.path.join(ROOT, "env/ftphase")


def main():
    cap = gpu_capability(LMP_GPU)
    print("LAMMPS:", cap["version"], {k: cap[k] for k in ("kokkos", "pace_kk", "hybrid_scaled_kk", "ufm", "ti_spring")})
    if not cap["all_modes"]:
        raise SystemExit("this binary cannot run calphy ts/liquid on the GPU")
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks = []
    for tag, data in (("x0", "fcc_Al_256.data"), ("x0.1", "fcc_Al0.9Li0.1_256.data")):
        src = os.path.join(CPU_DIR, data)
        dst = os.path.join(HERE, data)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        for ref, prefix in (("solid", "fcc"), ("liquid", "lqd")):
            blocks.append(calculation_block(
                f"{prefix}_{tag}", "ts", ["Al", "Li"], [26.9815, 6.94], dst, "pace", f"* * {POT} Al Li",
                [800.0, 1000.0], pressure=0, reference_phase=ref, n_equilibration_steps=5000, n_switching_steps=5000,
                queue=q, folder_prefix=f"{prefix}_{tag}", gpu=True, lammps_executable=LMP_GPU))
    out = write_series_input(os.path.join(HERE, "input_ace_gpu.yaml"), blocks)
    print("wrote", out)


if __name__ == "__main__":
    main()
