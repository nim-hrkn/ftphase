"""calphy input for one MACE-MPA-0 (fp32) liquid run through ML-IAP unified on the GPU.

Same system and settings as the example-8 WorkChain job pk 4356 (`alli_mace_mpa_0`, `lqd_x0.00`:
256 Al atoms, mode ts 1100 -> 700 K, P = 0, 10000 equilibration, 10000 + 10000 switching, 3 iterations),
which ran `pair_style mace no_domain_decomposition` through env/lammps-torch/bin/lmp_mace.sh.  Here the
same MACE-MPA-0 weights in float32 are loaded as a pickled ML-IAP model inside lmp_gpumliap
(`pair_style mliap unified <model> 0`, Kokkos coupling, `hybrid/scaled/kk`).

    ../../../env/ftphase/bin/python make_input.py      # writes input.yaml (+ copies the lattice)
    sbatch run.sbatch                                   # calphy_kernel inside one GPU Slurm job
    ../../../env/ftphase/bin/python compare.py          # vs the pk 4356 results
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ftphase", "src"))

from ftphase.calphy_io import calculation_block, write_series_input  # noqa: E402

REF_WORKDIR = "/home/kino/aiida_run/ftphase/b0/7b/edaa-1e7f-40d7-8e83-2df70be3b9bd"   # CalcJob pk 4356
MODEL = os.path.join(ROOT, "potentials", "mace", "macempa0mediummodel.model-mliap_lammps-f32.pt")
LMP = os.path.join(ROOT, "env", "lammps-gpu-mliap", "bin", "lmp_mliap_mace.sh")

lattice = os.path.join(HERE, "lqd_x0.00.data")
if not os.path.exists(lattice):
    shutil.copy(os.path.join(REF_WORKDIR, "lqd_x0.00.data"), lattice)

blk = calculation_block(
    name="lqd_x0.00",
    mode="ts",
    elements=["Al", "Li"],
    masses=[26.9815, 6.94],
    lattice_file=lattice,
    reference_phase="liquid",
    temperature=[1100.0, 700.0],
    pressure=0.0,
    pair_style=f"mliap unified {MODEL} 0",
    pair_coeff="* * Al Li",
    n_equilibration_steps=10000,
    n_switching_steps=[10000, 10000],
    n_iterations=3,
    folder_prefix="lqd_x0.00",
    queue={"scheduler": "local", "cores": 1},     # calphy_kernel runs inside run.sbatch (one GPU job)
    gpu=True,
    lammps_executable=LMP,
)
print(write_series_input(os.path.join(HERE, "input.yaml"), [blk]))
print(open(os.path.join(HERE, "input.yaml")).read())
