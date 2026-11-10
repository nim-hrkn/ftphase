# env/deepmd41 — deepmd-kit git 1ded5d2 (DPA-4.1 models), torch 2.13 cu132, LAMMPS plugin (built 2026-11-10 by build.sh, 6 attempts)

Build pitfalls fixed in `build.sh`: pip CUDA wheels lack unversioned `.so` names (symlinks), the C++ interface with the LAMMPS plugin
insists on TensorFlow headers (`tensorflow-cpu==2.18.1`), the pip nvcc's ptxas rejects its own PTX (use the conda-forge CUDA 13.2 toolkit:
cuda-nvcc, cuda-cudart-dev, cuda-cccl, cuda-nvrtc-dev, libcublas-dev, libcufft-dev; torch's FindCUDA needs the headers linked into
`include/`), and FindMPI picked Intel oneAPI MPI (use the pip mpich). Result: `deepmd 3.2.1.dev45+g1ded5d2`, `bin/lmp` (PyPI 22Jul2025u2)
+ `libdeepmd_lmpplugin.so`, wrapper `bin/lmp_deepmd.sh`, QHA code `ftphase-qha-deepmd41@mygarden5`.

DPA-4.1-Max-OAM (`potentials/deepmd/dpa4/dpa-4.1-max-oam-inference.pt`, user download of figshare 70537500): `dp --pt freeze` writes
the AOTInductor `.pt2` in 48 min on the RTX 3060 (`dp` cuts the `-o` name at the first dot: `-o dpa41maxoam`, then rename);
`dpa-4.1-max-oam.pt2` is 1.19 GB. **It does not fit the 12 GB RTX 3060 for 256-atom cells**: ASE/LAMMPS inference needs 0.84 GiB
(4 atoms), 2.1 GiB (32), 5.6 GiB (108) and runs out of memory at 256 atoms (`mem_probe.py`, 2026-11-10). calphy liquids (256 atoms)
and the 2048-atom solid TI are therefore impossible here; DPA-4.1-Air-OAM (5.1M params, figshare 70537293) is the candidate that fits.
