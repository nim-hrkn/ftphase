# env/deepmd32 — pip deepmd-kit 3.2.0 (torch 2.11 cu130) + PyPI LAMMPS 22Jul2025u2 with the deepmd plugin, for DPA4

Created 2026-11-06/07 (not committed; recreate with):

    mamba create -p ./env/deepmd32 -c conda-forge python=3.12 pip
    ./env/deepmd32/bin/pip install "deepmd-kit[torch,lmp]==3.2.0" ase phonopy spglib pymatgen "nvidia-cuda-nvcc==13.0.*" "nvidia-cuda-cccl==13.0.*" nvidia-cuda-runtime-cu12
    ./env/deepmd32/bin/pip install -e ./ftphase --no-deps        # ftphase-qha-run for the AiiDA code ftphase-qha-deepmd@mygarden5

Pieces: `bin/dp`, `bin/lmp` (PyPI wheel, PLUGIN, hybrid/scaled, ufm), plugin `site-packages/deepmd/lib/libdeepmd_lmpplugin.so`, wrapper
`bin/lmp_deepmd.sh` (prepends `plugin load` and `atom_modify map yes` to every -in script, puts deepmd/torch/cu12-runtime/cu13 libs on
LD_LIBRARY_PATH and strips Intel oneAPI entries). The deepmd C++ library of the wheel dlopens `libcudart.so.12` although torch is cu130:
`nvidia-cuda-runtime-cu12` provides it (otherwise "implib-gen: libcudart.so.12: failed to load", exit 245).

DPA4 (SeZM) models: `potentials/deepmd/dpa4/DPA4-{Plus,Air}-OMat24-v20260805.{pt,json}` from
https://huggingface.co/deepmodelingcommunity/DPA4-OMat24 (cc-by-nc-4.0, trained with deepmd-kit 3.2.0 on OMat24; Plus 8.8M, Air 5.1M params;
the Matbench DPA-4.1-OAM checkpoints exist only on figshare, which answers 403/202 from this host). DPA4 uses the AOTInductor `.pt2` export,
compiled for this GPU/libtorch (`dpa4_freeze_check.sbatch`): `DP_TRITON_INFER=2 DP_TF32_INFER=0 dp --pt freeze -c X.pt -o X` with
`CUDA_HOME=site-packages/nvidia/cu13` (pip CUDA 13 toolkit: needs nvcc and the CCCL headers `nv/target`, else "CUDA_HOME not set" /
"fatal error: nv/target"); 3-4 min per model, 61 / 96 MB. Verified (Slurm 23218 + srun): LAMMPS `pair_style deepmd X.pt2` = ASE
`deepmd.calculator.DP` exactly (Air -833.24708 eV / -6408.95 bar, Plus -833.39324 eV / -4963.34 bar on the 256-atom Al-Li liquid cell),
hybrid/scaled with ufm runs; 50-step NVT 0.064 (Air) / 0.139 (Plus) s/step incl. warm-up. calphy: LAMMPS stays on the CPU and the model on the
GPU (like the pair_style mace route), the calphy preflight must be skipped (`CALPHY_SKIP_PREFLIGHT=1`, AiiDA code `calphy-plugin@mygarden5`).
WorkChain: `run_aiida.py --mlip dpa4-plus-omat24 | dpa4-air-omat24` (QHA via `ftphase-qha-deepmd`, `qha_calculator: deepmd`).
The DPA-3.1-3M-FT route (3.1.3 env/deepmd) is described in `env/deepmd/README.md`.
