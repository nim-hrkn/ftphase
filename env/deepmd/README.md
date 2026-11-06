# env/deepmd — deepmd-kit 3.1.3 (PyTorch 2.12 cu129, OpenMPI) + conda-forge LAMMPS 29 Aug 2024 with the deepmd plugin, for DPA-3

Created 2026-11-06 (not committed; recreate with):

    mamba create -p ./env/deepmd -c conda-forge python=3.12 "deepmd-kit=3.1.3=cuda129py312*_mpi_openmpi_3" \
      "lammps=2024.8.29=*mpi_openmpi*" "cuda-version>=12.9,<13" ase pip

deepmd-kit 3.1.3 pins `lammps ==2024.8.29` (plugin ABI); the plugin `lib/deepmd_lmp/dpplugin.so` is auto-loaded through
`LAMMPS_PLUGIN_PATH` by the wrapper `bin/lmp_deepmd.sh` (exec of `bin/lmp_mpi`). `pair_style deepmd model.pth` runs the model on the
GPU by itself (torch), LAMMPS stays on the CPU (no Kokkos; like the `pair_style mace` route), `pair_coeff * * Al Li` (type_map names).
Model: `potentials/deepmd/dpa-3.1-3m-ft.pth` (frozen TorchScript, 18 MB, CC-BY-4.0) from
https://huggingface.co/deepmodelingcommunity/DPA-3.1-3M-FT (the Matbench Discovery checkpoint; figshare 55141895 only answers 202).
Checks: `dpa_check.sbatch` (ASE `deepmd.calculator.DP` vs LAMMPS single point, hybrid/scaled+ufm, 50-step NVT).

Findings 2026-11-06:
- `dpa-3.1-3m-ft.pth` (the Matbench checkpoint) loads in ASE (`deepmd.calculator.DP`, -835.234741 eV for the 256-atom test cell)
  but **cannot run in LAMMPS**: inside `pair_style deepmd` the message-passing path calls `border_op`, and the file was frozen
  without the custom op library ("border_op is not available since customized PyTorch OP library is not built when freezing").
  Re-freezing is impossible with public code: `dp convert-backend` fails on `use_torch_embed` and other descriptor options that
  neither 3.1.3, 3.2.0 (pip env `env/deepmd32`, torch 2.11 cu130, PyPI lammps 22Jul2025u2 + plugin; wrapper `env/deepmd32/bin/lmp_deepmd.sh`)
  nor the GitHub master know; the frozen graph names the source path `deepmd-kit-devmodel`, i.e. a private development version.
- Used instead: the public multi-task pretrained **DPA-3.1-3M** (`DPA-3.1-3M.pt`, 47 MB, v3.1.0 code, 32 branches), branch
  `MP_traj_v024_alldata_mixu` (MPtrj, PBE/MP level) frozen here with 3.1.3 and its op library:
  `dp --pt freeze -c DPA-3.1-3M.pt -o dpa-3.1-3m-mptrj.pth --model-branch MP_traj_v024_alldata_mixu`. LAMMPS (plugin, CPU
  single point) gives -835.2116 eV / -3899.69 bar = the ASE reference (-835.211605 / -3899.70); hybrid/scaled with ufm runs.
  It is not the leaderboard model (no sAlex fine-tuning); the `Omat24` branch is the other PBE-level choice.
- Running `dp` from a shell with Intel oneAPI on LD_LIBRARY_PATH fails (`libfabric.so.1: version FABRIC_1.9 not found`); unset it
  (the wrapper strips `/opt/intel` entries).
