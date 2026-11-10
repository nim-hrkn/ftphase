"""Submit the ftphase T-x WorkChain (stages 01-07) to the AiiDA daemon.

    env/ftphase/bin/python run_aiida.py [--name alli_ace] [--smoke] [--computer mygarden5] [--no-gpu]

Case: ACE Al-Li (AlLi-6gen-18May.yace), Al-rich half x_Li <= 0.5, the same physics as example 5
(fcc random cells, B32 anti-sites, L1_2 Al3Li point phase, calphy liquids 1100 -> 700 K on the GPU).
``--smoke`` shrinks everything (1 fcc cell + 1 liquid, 1000 steps, 2 volumes) to check the chain
in a few minutes.  After ``submit`` nothing depends on this process: the daemon (profile
``ftphase``) runs the calcfunctions, Slurm the CalcJobs.  Follow with

    verdi -p ftphase process status <pk>      # tree of the WorkChain
    verdi -p ftphase process report <pk>      # messages
    python fetch_results.py <pk>              # copy REPORT.md, png, tables to out/<name>/
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LMP_GPU = os.path.join(ROOT, "env/lammps-gpu/bin/lmp_gpu")
LMP_GPU_GRACE = os.path.join(ROOT, "env/lammps-gpu-grace/bin/lmp_gpugrace")   # 22Jul2025u6 + grace.patch: grace/fs/kk, grace/1l/kk, hybrid/scaled/kk
# MLIP variants for the Al-Li comparison (same cells, same spec; only the potential, pair style and GPU binary change)
MLIPS = {"ace": {"potential": POT, "pair_style": "pace", "pair_coeff": "* * {potential} Al Li", "model": "AlLi-6gen-18May.yace (ACE)", "lmp_gpu": LMP_GPU, "tag": ""},
         "grace-fs": {"potential": os.path.join(ROOT, "potentials/grace/GRACE-FS-OAM.yaml"), "pair_style": "grace/fs", "pair_coeff": "* * {potential} Al Li",
                      "model": "GRACE-FS-OAM (foundation, FS, 6 A)", "lmp_gpu": LMP_GPU_GRACE, "tag": "_grace_fs"},
         # GRACE 1L/2L/3L exist only as Kokkos styles: calphy uses grace/<n>l/kk/fp32 (true-fp32 radial MLP, 3.3x faster than fp64,
         # < 1e-3 meV/atom difference; calphy's preflight needs the literal style name in the binary); the QHA stage runs
         # LAMMPSlib with the Kokkos arguments on the GPU too (the conda LAMMPS Kokkos is CUDA-only), so those QHA jobs request a GPU
         "grace-1l": {"potential": os.path.join(ROOT, "potentials/grace/GRACE-1L-OMAT-medium-base-fp64-kokkos.npz"), "pair_style": "grace/1l/kk/fp32", "qha_pair_style": "grace/1l/kk/fp32", "pair_coeff": "* * {potential} Al Li",
                      "model": "GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export)", "lmp_gpu": LMP_GPU_GRACE, "tag": "_grace_1l", "qha_gpu": True},
         "grace-2l": {"potential": os.path.join(ROOT, "potentials/grace/GRACE-2L-OMAT-medium-base-fp64-kokkos.npz"), "pair_style": "grace/2l/kk/fp32", "qha_pair_style": "grace/2l/kk/fp32", "pair_coeff": "* * {potential} Al Li",
                      "model": "GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export)", "lmp_gpu": LMP_GPU_GRACE, "tag": "_grace_2l", "qha_gpu": True},
         "grace-3l": {"potential": os.path.join(ROOT, "potentials/grace/GRACE-3L-OMAT-large-kokkos.npz"), "pair_style": "grace/3l/kk/fp32", "qha_pair_style": "grace/3l/kk/fp32", "pair_coeff": "* * {potential} Al Li",
                      "model": "GRACE-3L-OMAT-large (foundation, 3 layers, fp32 kokkos export)", "lmp_gpu": LMP_GPU_GRACE, "tag": "_grace_3l", "qha_gpu": True}}
KK_ARGS = ["-k", "on", "g", "1", "-sf", "kk", "-pk", "kokkos", "newton", "on", "neigh", "half"]
# libtorch-type MLIPs: the pair style itself runs on the GPU (no Kokkos, no hybrid/scaled/kk); calphy drives the plain
# LAMMPS build (env/lammps-torch, wrapper scripts set the libtorch path) with 1 rank on a GPU job; QHA uses the ASE
# calculator of the package (env/torch for SevenNet, env/mace for MACE: separate envs because of the e3nn pin) with the
# checkpoint / .model file, while calphy gets the deployed TorchScript file -> WorkChain input potential_qha.
_SEV = os.path.join(ROOT, "potentials/sevenn"); _MAC = os.path.join(ROOT, "potentials/mace")
LMP_SEVENN = os.path.join(ROOT, "env/lammps-torch/bin/lmp_sevenn.sh"); LMP_MACE = os.path.join(ROOT, "env/lammps-torch/bin/lmp_mace.sh")
# ML-IAP unified (2026-10-30): lmp_gpumliap runs the pickled MACE model inside LAMMPS (Kokkos coupling, hybrid/scaled/kk); the model path
# goes into pair_style ("mliap unified {potential} 0"), and calphy gets the Kokkos cmdargs through calphy_extra gpu=True ("calphy_gpu").
# Verified against pair_style mace: ftphase/examples/calphy_mliap_mace (G within 0.15 meV/atom, 1.85x faster). Only on hosts with env/lammps-gpu-mliap.
LMP_MLIAP_MACE = os.path.join(ROOT, "env/lammps-gpu-mliap/bin/lmp_mliap_mace.sh")
LMP_MLIAP_MATTERSIM = os.path.join(ROOT, "env/lammps-gpu-mliap/bin/lmp_mliap_mattersim.sh")   # PYTHONHOME env/torch (mattersim 1.2.5)
_MS = os.path.join(ROOT, "potentials", "mattersim")
LMP_MLIAP_NEQUIP = os.path.join(ROOT, "env/lammps-gpu-mliap/bin/lmp_mliap_nequip.sh")
LMP_DEEPMD32 = os.path.join(ROOT, "env/deepmd32/bin/lmp_deepmd.sh")
LMP_DEEPMD41 = os.path.join(ROOT, "env/deepmd41/bin/lmp_deepmd.sh")   # deepmd-kit git 1ded5d2 (DPA-4.1 models), torch 2.13 cu132; built by env/deepmd41/build.sh   # PyPI LAMMPS 22Jul2025u2 + deepmd-kit 3.2.0 plugin; wrapper prepends plugin load + atom_modify map yes
_DPA4 = os.path.join(ROOT, "potentials", "deepmd", "dpa4")
LMP_METATOMIC = os.path.join(ROOT, "env/metatomic/bin/lmp_metatomic.sh")   # conda lammps-metatomic 4Jul2026 KOKKOS (metatomic/kk, hybrid/scaled/kk); wrapper moves pair_style after read_data
_PET = os.path.join(ROOT, "potentials", "pet")   # PYTHONHOME env/torch (nequip 0.19.1 + openequivariance)
_NQ = os.path.join(ROOT, "potentials", "nequip")


def _sevenn_ckpt(name):
    import glob
    f = glob.glob(os.path.join(ROOT, "env/torch/lib/python3.12/site-packages/sevenn/pretrained_potentials", name, "*.pth"))
    return f[0] if f else None


# MACE: float32 everywhere (calphy TorchScript -f32, QHA MACECalculator default_dtype float32; 4.7x faster than float64, PE identical to 1e-5 eV)
MLIPS.update({
    "sevenn-0": {"potential": os.path.join(_SEV, "7net-0_oeq.pt"), "potential_qha": _sevenn_ckpt("SevenNet_0__11Jul2024"), "pair_style": "e3gnn", "pair_coeff": "* * {potential} Al Li",
                 "model": "SevenNet-0 (11Jul2024, MPtrj; oeq deployment)", "lmp_gpu": LMP_SEVENN, "tag": "_sevenn_0", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "sevenn"},
    "sevenn-mf-ompa": {"potential": os.path.join(_SEV, "7net-mf-ompa_mpa_oeq.pt"), "potential_qha": _sevenn_ckpt("SevenNet_MF_ompa"), "pair_style": "e3gnn", "pair_coeff": "* * {potential} Al Li",
                       "model": "SevenNet-MF-ompa (modal mpa; oeq deployment)", "lmp_gpu": LMP_SEVENN, "tag": "_sevenn_mf_ompa", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "sevenn", "qha_modal": "mpa"},
    # cuEquivariance fp32 export (2026-11-03): 0.020 s/step at 256 atoms vs 0.090 for the e3nn export (-mliap_lammps-f32.pt), same energies
    "mace-mpa-0": {"potential": os.path.join(_MAC, "macempa0mediummodel-cueq.model-mliap_lammps.pt"), "potential_qha": os.path.join(_MAC, "macempa0mediummodel.model"), "pair_style": "mliap unified {potential} 0", "pair_coeff": "* * Al Li",
                   "model": "MACE-MPA-0 medium (float32, ML-IAP, cuEquivariance)", "lmp_gpu": LMP_MLIAP_MACE, "tag": "_mace_mpa_0", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-mace", "qha_calculator": "mace", "qha_dtype": "float32"},
    # MatterSim (M3GNet, float32) through ML-IAP unified (official MatterSimMLIAP export, test/mattersim_to_mliap.py; Slurm 22999: ASE energy
    # within 6 ueV/atom, hybrid/scaled/kk correct, 5M 0.040 s/step at 256 atoms). QHA: MatterSimCalculator in env/torch on the checkpoint.
    "mattersim-5m": {"potential": os.path.join(_MS, "mattersim-v1.0.0-5M_mliap.pt"), "potential_qha": os.path.join(_MS, "mattersim-v1.0.0-5M.pth"), "pair_style": "mliap unified {potential} 0", "pair_coeff": "* * Al Li",
                     "model": "MatterSim-v1.0.0-5M (float32, ML-IAP)", "lmp_gpu": LMP_MLIAP_MATTERSIM, "tag": "_mattersim_5m", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "mattersim"},
    "mattersim-1m": {"potential": os.path.join(_MS, "mattersim-v1.0.0-1M_mliap.pt"), "potential_qha": os.path.join(_MS, "mattersim-v1.0.0-1M.pth"), "pair_style": "mliap unified {potential} 0", "pair_coeff": "* * Al Li",
                     "model": "MatterSim-v1.0.0-1M (float32, ML-IAP)", "lmp_gpu": LMP_MLIAP_MATTERSIM, "tag": "_mattersim_1m", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "mattersim"},
    # NequIP-OAM-L 0.1 (MIR group, CC-BY-4.0; Matbench F1 0.893, kappa_SRME 0.166) through ML-IAP unified: nequip-prepare-lmp-mliap export with
    # OpenEquivariance (Slurm 23000: hybrid/scaled/kk correct, 0.0125/0.029 s/step at 108/256 atoms). QHA: the package file is AOTI-compiled for the
    # job's device inside the runner (nequip-compile --target ase, ~2 min) and used through NequIPCalculator.
    "nequip-oam-l": {"potential": os.path.join(_NQ, "NequIP-OAM-L-0.1.nequip.lmp.pt"), "potential_qha": os.path.join(_NQ, "NequIP-OAM-L-0.1.nequip.zip"), "pair_style": "mliap unified {potential} 0", "pair_coeff": "* * Al Li",
                     "model": "NequIP-OAM-L 0.1 (ML-IAP, OpenEquivariance)", "lmp_gpu": LMP_MLIAP_NEQUIP, "tag": "_nequip_oam_l", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "nequip"},
    # NequIP-OAM-M 0.1 (Zenodo 10.5281/zenodo.18775904 "0.1a", md5 e5b44583f4421be702b35d76503754cd), same export and QHA route as OAM-L (2026-11-01)
    "nequip-oam-m": {"potential": os.path.join(_NQ, "NequIP-OAM-M-0.1.nequip.lmp.pt"), "potential_qha": os.path.join(_NQ, "NequIP-OAM-M-0.1.nequip.zip"), "pair_style": "mliap unified {potential} 0", "pair_coeff": "* * Al Li",
                     "model": "NequIP-OAM-M 0.1 (ML-IAP, OpenEquivariance)", "lmp_gpu": LMP_MLIAP_NEQUIP, "tag": "_nequip_oam_m", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "nequip"},
    # NequIP-OAM-S 0.1 (smallest OAM package, 5.6 MB; same export/route as OAM-L/M; 2026-11-02)
    "nequip-oam-s": {"potential": os.path.join(_NQ, "NequIP-OAM-S-0.1.nequip.lmp.pt"), "potential_qha": os.path.join(_NQ, "NequIP-OAM-S-0.1.nequip.zip"), "pair_style": "mliap unified {potential} 0", "pair_coeff": "* * Al Li",
                     "model": "NequIP-OAM-S 0.1 (ML-IAP, OpenEquivariance)", "lmp_gpu": LMP_MLIAP_NEQUIP, "tag": "_nequip_oam_s", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-torch", "qha_calculator": "nequip"},
    # PET-OAM-L 0.1.0 (lab-cosmo/upet, 255M, OMat24 -> sAlex+MPtrj, PBE/MP level; exported with `mtt export` in env/metatomic; 2026-11-07, user decision after the
    # liquid timing: 585 min per liquid = 62x ACE). calphy on the GPU through pair_style metatomic/kk; QHA with metatomic's ASE calculator (env/metatomic, GPU).
    # pair_coeff maps LAMMPS types to atomic numbers; the elements list of the spec is converted below (Al Li -> 13 3).
    "pet-oam-l": {"potential": os.path.join(_PET, "pet-oam-l-v0.1.0.pt"), "potential_qha": os.path.join(_PET, "pet-oam-l-v0.1.0.pt"), "pair_style": "metatomic {potential}", "pair_coeff": "* * Al Li",
                  "model": "PET-OAM-L 0.1.0 (metatomic, float32)", "lmp_gpu": LMP_METATOMIC, "tag": "_pet_oam_l", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-metatomic", "qha_calculator": "metatomic", "pair_coeff_Z": True},
    "pet-omat-s": {"potential": os.path.join(_PET, "pet-omat-s-v1.0.0.pt"), "potential_qha": os.path.join(_PET, "pet-omat-s-v1.0.0.pt"), "pair_style": "metatomic {potential}", "pair_coeff": "* * Al Li",
                   "model": "PET-OMat-S 1.0.0 (metatomic, float32)", "lmp_gpu": LMP_METATOMIC, "tag": "_pet_omat_s", "torch": True, "calphy_gpu": True, "qha_gpu": True, "qha_code": "ftphase-qha-metatomic", "qha_calculator": "metatomic", "pair_coeff_Z": True},
    # DPA4 (SeZM) OMat24 v20260805 from huggingface.co/deepmodelingcommunity/DPA4-OMat24 (cc-by-nc-4.0, deepmd-kit 3.2.0; 2026-11-07): the frozen .pt2
    # (AOTInductor, compiled on this GPU with DP_TRITON_INFER=2) runs on the GPU through pair_style deepmd with LAMMPS on the CPU (no Kokkos; like the
    # pair_style mace route), so calphy_gpu is off; the calphy code must skip the style preflight (plugin style): calphy_code "calphy-plugin".
    # QHA: deepmd's ASE calculator with the same .pt2 (env/deepmd32, GPU). The Matbench DPA-4.1-OAM checkpoints are figshare-only (403 from here).
    "dpa4-plus-omat24": {"potential": os.path.join(_DPA4, "DPA4-Plus-OMat24-v20260805.pt2"), "potential_qha": os.path.join(_DPA4, "DPA4-Plus-OMat24-v20260805.pt2"), "pair_style": "deepmd {potential}", "pair_coeff": "* * Al Li",
                         "model": "DPA4-Plus-OMat24 v20260805 (deepmd 3.2.0, .pt2)", "lmp_gpu": LMP_DEEPMD32, "tag": "_dpa4_plus_omat24", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-deepmd", "qha_calculator": "deepmd", "calphy_code": "calphy-plugin"},
    "dpa4-air-omat24": {"potential": os.path.join(_DPA4, "DPA4-Air-OMat24-v20260805.pt2"), "potential_qha": os.path.join(_DPA4, "DPA4-Air-OMat24-v20260805.pt2"), "pair_style": "deepmd {potential}", "pair_coeff": "* * Al Li",
                        "model": "DPA4-Air-OMat24 v20260805 (deepmd 3.2.0, .pt2)", "lmp_gpu": LMP_DEEPMD32, "tag": "_dpa4_air_omat24", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-deepmd", "qha_calculator": "deepmd", "calphy_code": "calphy-plugin"},
    # DPA-4.1-Max-OAM (Matbench: 99M params, MPtrj+OMat24+sAlex, F1 0.913, kappa_SRME 0.090; figshare 70537500 downloaded by the user 2026-11-08,
    # sha256 fb19a96e...; deepmd-kit commit 1ded5d2, torch 2.13 cu132 in env/deepmd41). Same route as DPA4-OMat24: .pt2 frozen on this GPU
    # (env/deepmd41/dpa41_freeze_check.sh), pair_style deepmd through the plugin LAMMPS, calphy-plugin code, QHA code ftphase-qha-deepmd41.
    # DPA-4.1-Air-OAM (Matbench: 5.1M params, same MPtrj+OMat24+sAlex data as Max, F1 0.902, kappa_SRME 0.129; figshare 70537293 downloaded by the
    # user 2026-11-11; Max does not fit the 12 GB GPU at 256 atoms). Same route as Max (env/deepmd41, .pt2 frozen on this GPU).
    "dpa4.1-air-oam": {"potential": os.path.join(_DPA4, "dpa-4.1-air-oam.pt2"), "potential_qha": os.path.join(_DPA4, "dpa-4.1-air-oam.pt2"), "pair_style": "deepmd {potential}", "pair_coeff": "* * Al Li",
                       "model": "DPA-4.1-Air-OAM (deepmd 1ded5d2, .pt2)", "lmp_gpu": LMP_DEEPMD41, "tag": "_dpa41_air_oam", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-deepmd41", "qha_calculator": "deepmd", "calphy_code": "calphy-plugin", "qha_env": "deepmd41"},
    "dpa4.1-max-oam": {"potential": os.path.join(_DPA4, "dpa-4.1-max-oam.pt2"), "potential_qha": os.path.join(_DPA4, "dpa-4.1-max-oam.pt2"), "pair_style": "deepmd {potential}", "pair_coeff": "* * Al Li",
                       "model": "DPA-4.1-Max-OAM (deepmd 1ded5d2, .pt2)", "lmp_gpu": LMP_DEEPMD41, "tag": "_dpa41_max_oam", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-deepmd41", "qha_calculator": "deepmd", "calphy_code": "calphy-plugin", "qha_env": "deepmd41"},
    # the pair_style mace route of pk 4293 (env/lammps-torch, lmp_mace.sh prepends atom_modify map yes), kept for comparison runs
    "mace-mpa-0-pairstyle": {"potential": os.path.join(_MAC, "macempa0mediummodel.model-lammps-f32.pt"), "potential_qha": os.path.join(_MAC, "macempa0mediummodel.model"), "pair_style": "mace no_domain_decomposition", "pair_coeff": "* * {potential} Al Li",
                   "model": "MACE-MPA-0 medium (float32)", "lmp_gpu": LMP_MACE, "tag": "_mace_mpa_0_pairstyle", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-mace", "qha_calculator": "mace", "qha_dtype": "float32"},
    "mace-omat-0": {"potential": os.path.join(_MAC, "maceomat0mediummodel.model-lammps.pt"),   # (float64 TorchScript; make a -f32 copy with mace_create_lammps_model --dtype float32 before using it) "potential_qha": os.path.join(_MAC, "maceomat0mediummodel.model"), "pair_style": "mace no_domain_decomposition", "pair_coeff": "* * {potential} Al Li",
                    "model": "MACE-OMAT-0 medium (float32)", "lmp_gpu": LMP_MACE, "tag": "_mace_omat_0", "torch": True, "qha_gpu": True, "qha_code": "ftphase-qha-mace", "qha_calculator": "mace", "qha_dtype": "float32"},
})
POT_AGCU = os.path.join(ROOT, "potentials/agcu/CuAg.eam.alloy")   # Williams, Mishin, Hamilton 2006 (NIST), setfl order Cu Ag


def candidates(li_side: bool = False):
    from ase.build import bulk
    from ase import Atoms
    from ase.spacegroup import crystal

    b32 = crystal(["Al", "Li"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=227, cellpar=[6.37, 6.37, 6.37, 90, 90, 90])
    l12 = Atoms("LiAl3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[4.0, 4.0, 4.0], pbc=True)
    c = {"fcc-Al": (bulk("Al", "fcc", a=4.05, cubic=True), 0.0), "bcc-Li": (bulk("Li", "bcc", a=3.49, cubic=True), 1.0), "B32-AlLi": (b32, 0.5), "L12-Al3Li": (l12, 0.25)}
    if li_side:   # Li-rich intermetallics of example 6 (user-supplied Materials Project CIFs): Al2Li3 R-3m (15-atom hexagonal cell), Al4Li9 C2/m (26 atoms)
        from ase.io import read
        sd = os.path.join(ROOT, "ftphase", "examples", "alli_ace_txdiagram", "structures")
        c["Al2Li3"] = (read(os.path.join(sd, "mp-16506-Li3Al2.cif")), 0.6)
        c["Al4Li9"] = (read(os.path.join(sd, "mp-568404-Li9Al4.cif")), 9 / 13)
    return c


def li_side_spec(spec):
    """Extend the Al-Li spec to 0.5 < x_Li < 1 with solids only (2026-11-11, user request): bcc Li solid solution (32-atom random cells,
    x_Li 0.75-1.0, 2 configurations, like the fcc series) and the point phases Al2Li3 / Al4Li9; the Li-side liquids are not computed,
    so the diagram is meaningful only below the Li-side solidus (SGTE: bcc melts at 453 K)."""
    spec["candidates"].update({"Al2Li3": 0.6, "Al4Li9": 9 / 13})
    spec["solids"] += [
        {"phase": "bcc", "kind": "solution", "base": "bcc-Li", "repeat": [2, 2, 4], "x": [0.75, 0.8125, 0.875, 0.9375, 1.0], "n_configs": 2, "series": "random", "seed": 0,
         "supercell": [2, 2, 2], "mesh": 60.0},
        {"phase": "Al2Li3", "kind": "point", "base": "Al2Li3", "x": [0.6], "supercell": [2, 2, 1], "mesh": 60.0},
        {"phase": "Al4Li9", "kind": "point", "base": "Al4Li9", "x": [9 / 13], "supercell": [1, 2, 2], "mesh": 60.0},
    ]
    asm = spec["assemble"]
    asm["fits"]["bcc"] = "poly"; asm["poly_orders"] = {**asm.get("poly_orders", {}), "bcc": 2}
    asm["config_terms"]["bcc"] = "ideal"
    asm["sigma"].update({"bcc": 0.002, "Al2Li3": 0.002, "Al4Li9": 0.002})
    asm["drop_edge_beyond_liquid"] = False
    asm["title"] = asm["title"].replace("x_Li <= 0.5", "0 <= x_Li <= 1, Li side solids only")
    return spec


def candidates_agcu():
    from ase.build import bulk

    return {"fcc-Ag": (bulk("Ag", "fcc", a=4.09, cubic=True), 0.0), "fcc-Cu": (bulk("Cu", "fcc", a=3.615, cubic=True), 1.0)}


def make_spec_agcu(smoke: bool, gpu: bool):
    """Ag-Cu: one fcc solution over the whole range (random 32-atom cells, 2 configurations) + liquid.
    The eutectic and the fcc miscibility gap come out of one fitted fcc curve (ideal + Redlich-Kister)
    and the liquid; solids near T_m use calphy TI (spec['solids_ti']) instead of QHA."""
    xs = [0.0, 1 / 32, 2 / 32, 4 / 32, 8 / 32, 12 / 32, 16 / 32, 20 / 32, 24 / 32, 28 / 32, 30 / 32, 31 / 32, 1.0]
    spec = {
        "elements": ["Ag", "Cu"], "masses": [107.8682, 63.546], "x_element": "Cu", "model": "CuAg.eam.alloy (Williams-Mishin-Hamilton 2006 EAM)",
        "pair_style": "eam/alloy", "pair_coeff": "* * {potential} Ag Cu", "atom_types": {"Ag": 1, "Cu": 2},
        "candidates": {"fcc-Ag": 0.0, "fcc-Cu": 1.0}, "known_ground_states": ["fcc-Ag", "fcc-Cu"],
        "relax": {"fmax": 1e-3, "cell": True},
        "solids": [{"phase": "fcc", "kind": "solution", "base": "fcc-Ag", "repeat": [2, 2, 2], "x": xs, "n_configs": 2, "series": "random", "seed": 0,
                    "supercell": [2, 2, 2], "mesh": 60.0}],
        "solids_ti": {"phases": ["fcc"], "T_sweep": [900.0, 1400.0], "T_hi_by_x": [[0.0, 1360.0], [1.0, 1480.0]], "min_atoms": 2000,   # 256-atom Frenkel-Ladd cells are ~7 meV/atom too low (ti_convergence.py); 4x4x4 of 32 = 2048
                      "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000], "n_iterations": 1, "mode": "ts"},
        "liquids": {"base": "fcc-Ag", "repeat": [4, 4, 4], "x": [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0], "seed": 100, "T_sweep": [1500.0, 950.0],
                    "T_override": {"0.0": 1050.0, "1.0": 1100.0}, "n_repeats": 1, "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000],
                    "n_iterations": 3, "mode": "ts", "pressure": 0.0},
        "qha": {"T_max": 1400.0, "T_step": 25.0, "scales": [0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08], "eos": "vinet", "imaginary": "drop",
                "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}},
        "assemble": {"T_min": 900.0, "T_max": 1400.0, "T_step": 10.0, "fits": {"fcc": "rk", "liquid": "rk"}, "poly_orders": {"fcc": 4, "liquid": 4}, "poly_order": 4,
                     "config_terms": {"fcc": "ideal"}, "sigma": {"fcc": 0.002, "liquid": 0.0014}, "hull": {"min_width": 0.005, "gap_tol": 2.5},
                     "drop_edge_beyond_liquid": False, "sensitivity_samples": 30, "liquid_sigma_floor": 0.0014, "T_residuals": 1100.0,
                     "title": "EAM Ag-Cu (Williams-Mishin-Hamilton 2006), 0 GPa: fcc (calphy TI >= 900 K, QHA below) + calphy liquid [AiiDA]", "xlabel": "x_Cu"},
    }
    if smoke:
        spec["solids"][0].update({"x": [0.0, 0.5, 1.0], "n_configs": 1, "repeat": [1, 1, 1], "supercell": [2, 2, 2], "mesh": [4, 4, 4]})
        spec["solids_ti"].update({"T_sweep": [1000.0, 1100.0], "T_hi_by_x": [[0.0, 1100.0], [1.0, 1100.0]], "min_atoms": 100, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000]})
        spec["liquids"].update({"x": [0.0, 0.5], "repeat": [3, 3, 3], "T_sweep": [1500.0, 1200.0], "T_override": {}, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1})
        spec["qha"].update({"T_step": 100.0, "scales": [0.97, 0.985, 1.0, 1.015, 1.03, 1.05]})
        spec["assemble"].update({"T_min": 1000.0, "T_max": 1400.0, "sensitivity_samples": 5, "title": "smoke test Ag-Cu"})
    return spec


POT_NIAL = os.path.join(ROOT, "potentials/nial/Mishin-Ni-Al-2009.eam.alloy")   # Purja Pun & Mishin 2009 (NIST)


def candidates_nial():
    from ase import Atoms
    from ase.build import bulk
    from ase.spacegroup import crystal

    return {"fcc-Al": (bulk("Al", "fcc", a=4.05, cubic=True), 0.0), "fcc-Ni": (bulk("Ni", "fcc", a=3.52, cubic=True), 1.0),
            "B2-NiAl": (Atoms("NiAl", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0.5)], cell=[2.88] * 3, pbc=True), 0.5),
            "L12-Ni3Al": (Atoms("AlNi3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[3.57] * 3, pbc=True), 0.75),
            "Ni2Al3": (crystal(["Al", "Al", "Ni"], [(0, 0, 0), (1 / 3, 2 / 3, 0.149), (1 / 3, 2 / 3, 0.648)], spacegroup=164, cellpar=[4.03, 4.03, 4.89, 90, 90, 120]), 0.4),
            "NiAl3": (crystal(["Al", "Al", "Ni"], [(0.183, 0.069, 0.334), (0.039, 0.25, 0.842), (0.876, 0.25, 0.443)], spacegroup=62, cellpar=[6.61, 7.37, 4.81, 90, 90, 90]), 0.25)}


def make_spec_nial(smoke: bool, gpu: bool):
    """Ni-Al (example 7 in the WorkChain): fcc(Al) and fcc(Ni) random solutions, B2 NiAl with Ni anti-sites
    (Ni-rich) and Ni vacancies (Al-rich), L1_2 Ni3Al with anti-sites on both sides, Ni2Al3 / NiAl3 point phases,
    liquid 0 <= x_Ni <= 1 in steps of 0.1 (Al lattice for x <= 0.5, Ni lattice above) swept from 2000 K down to a
    composition-dependent stop temperature (as in nial_eam/pipeline.py).  Solids by QHA only."""
    t_stop = {0.0: 850.0, 0.1: 850.0, 0.2: 950.0, 0.3: 1100.0, 0.4: 1300.0, 0.5: 1500.0, 0.6: 1450.0, 0.7: 1350.0, 0.8: 1400.0, 0.9: 1450.0, 1.0: 1500.0}
    spec = {
        "elements": ["Al", "Ni"], "masses": [26.9815, 58.6934], "x_element": "Ni", "model": "Mishin-Ni-Al-2009.eam.alloy (Purja Pun & Mishin 2009 EAM)",
        "pair_style": "eam/alloy", "pair_coeff": "* * {potential} Al Ni", "atom_types": {"Al": 1, "Ni": 2},
        "candidates": {"fcc-Al": 0.0, "fcc-Ni": 1.0, "B2-NiAl": 0.5, "L12-Ni3Al": 0.75, "Ni2Al3": 0.4, "NiAl3": 0.25},
        "known_ground_states": ["fcc-Al", "fcc-Ni", "B2-NiAl", "L12-Ni3Al", "Ni2Al3", "NiAl3"],
        "relax": {"fmax": 1e-3, "cell": True},
        "solids": [
            {"phase": "fccAl", "kind": "solution", "base": "fcc-Al", "repeat": [2, 2, 2], "x": [0.0, 1 / 32, 2 / 32], "n_configs": 1, "series": "random", "seed": 0, "supercell": [2, 2, 2], "mesh": 60.0},
            {"phase": "fccNi", "kind": "solution", "base": "fcc-Ni", "repeat": [2, 2, 2], "x": [0.75, 0.8125, 0.875, 0.9375, 1.0], "n_configs": 1, "series": "random", "seed": 0, "supercell": [2, 2, 2], "mesh": 60.0},
            {"phase": "B2", "kind": "limited", "base": "B2-NiAl", "repeat": [3, 3, 3], "seed": 1, "supercell": [2, 2, 2], "mesh": 60.0,
             "defects": [{"replace": ["Al", "Ni"], "n": 1}, {"replace": ["Al", "Ni"], "n": 2}, {"replace": ["Al", "Ni"], "n": 4}, {"replace": ["Al", "Ni"], "n": 6},
                         {"vacancy": "Ni", "n": 1}, {"vacancy": "Ni", "n": 2}, {"vacancy": "Ni", "n": 3}]},
            {"phase": "L12", "kind": "limited", "base": "L12-Ni3Al", "repeat": [2, 2, 2], "seed": 2, "supercell": [2, 2, 2], "mesh": 60.0,
             "defects": [{"replace": ["Al", "Ni"], "n": 1}, {"replace": ["Ni", "Al"], "n": 1}]},
            {"phase": "Ni2Al3", "kind": "point", "base": "Ni2Al3", "x": [0.4], "supercell": [3, 3, 2], "mesh": 60.0},
            {"phase": "NiAl3", "kind": "point", "base": "NiAl3", "x": [0.25], "supercell": [2, 2, 2], "mesh": 60.0},
        ],
        "liquids": {"base": "fcc-Al", "base_hi": [0.5, "fcc-Ni"], "repeat": [4, 4, 4], "x": [round(0.1 * i, 1) for i in range(11)], "seed": 100,
                    "T_sweep": [2000.0, 850.0], "T_override": {f"{k:.1f}": v for k, v in t_stop.items()}, "n_repeats": 1, "n_equilibration_steps": 10000,
                    "n_switching_steps": [10000, 10000], "n_iterations": 3, "mode": "ts", "pressure": 0.0},
        "qha": {"T_max": 2000.0, "T_step": 25.0, "scales": [0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08], "eos": "vinet", "imaginary": "drop",
                "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}},
        "assemble": {"T_min": 900.0, "T_max": 2000.0, "T_step": 10.0, "liquid_partial": True, "drop_edge_beyond_liquid": False,
                     "fits": {"fccAl": "poly", "fccNi": "poly", "liquid": "rk", "B2": "poly", "L12": "poly"}, "poly_order": 3,
                     "poly_orders": {"liquid": 4, "fccAl": 2, "fccNi": 3, "B2": 1, "L12": 1},
                     "config_terms": {"fccAl": "ideal", "fccNi": "ideal", "B2": "sublattice:b2_triple_defect", "L12": "sublattice:b32_antisite@0.75"},
                     "entropy_models": {"B2": ["b2_triple_defect", 0.5], "L12": ["b32_antisite@0.75", 0.75]},
                     "sigma": {"fccAl": 0.002, "fccNi": 0.002, "B2": 0.002, "L12": 0.002, "Ni2Al3": 0.002, "NiAl3": 0.002, "liquid": 0.0014},
                     "hull": {"min_width": 0.005, "gap_tol": 2.5}, "sensitivity_samples": 30, "liquid_sigma_floor": 0.0014, "T_residuals": 1500.0,
                     "title": "EAM Ni-Al (Purja Pun & Mishin 2009), 0 GPa: QHA solids + calphy liquid [AiiDA]", "xlabel": "x_Ni"},
    }
    if smoke:
        spec["solids"] = [dict(spec["solids"][0], x=[0.0], supercell=[1, 1, 1], mesh=[4, 4, 4]), dict(spec["solids"][1], x=[1.0], supercell=[1, 1, 1], mesh=[4, 4, 4]),
                          dict(spec["solids"][2], repeat=[2, 2, 2], defects=[{"replace": ["Al", "Ni"], "n": 1}, {"vacancy": "Ni", "n": 1}], supercell=[1, 1, 1], mesh=[4, 4, 4])]
        spec["liquids"].update({"x": [0.0, 0.5, 1.0], "repeat": [3, 3, 3], "T_sweep": [2000.0, 1700.0], "T_override": {}, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1})
        spec["qha"].update({"T_step": 100.0, "scales": [0.97, 0.985, 1.0, 1.015, 1.03, 1.05]})
        spec["assemble"].update({"T_min": 1700.0, "T_max": 2000.0, "sensitivity_samples": 5, "title": "smoke test Ni-Al"})
    return spec


def candidates_ptrh():
    """Pt-Rh (2026-11-04): fcc ends, the fcc-based ordered phases of Saengdeejing et al., npj Comput. Mater. 12, 362 (2026):
    PtRh '40' (NbP type, I4_1/amd, tI8), PtRh3 D0_22 (I4/mmm, tI8) and its anti-structure Pt3Rh D0_22 (stable only in PFP)."""
    from ase.build import bulk
    from pymatgen.core import Lattice, Structure
    from pymatgen.io.ase import AseAtomsAdaptor

    def tet(sg, a, c, species, coords):
        return AseAtomsAdaptor.get_atoms(Structure.from_spacegroup(sg, Lattice.tetragonal(a, c), species, coords))

    return {"fcc-Pt": (bulk("Pt", "fcc", a=3.924, cubic=True), 0.0), "fcc-Rh": (bulk("Rh", "fcc", a=3.803, cubic=True), 1.0),
            "PtRh-40": (tet("I4_1/amd", 3.899, 7.811, ["Pt", "Rh"], [[0, 0, 0], [0, 0, 0.5]]), 0.5),
            "PtRh3-D022": (tet("I4/mmm", 3.867, 7.738, ["Pt", "Rh", "Rh"], [[0, 0, 0], [0, 0, 0.5], [0, 0.5, 0.25]]), 0.75),
            "Pt3Rh-D022": (tet("I4/mmm", 3.937, 7.861, ["Rh", "Pt", "Pt"], [[0, 0, 0], [0, 0, 0.5], [0, 0.5, 0.25]]), 0.25)}


def make_spec_ptrh(smoke: bool, gpu: bool):
    """Pt-Rh with a universal MLIP (--mlip required): fcc solution 0 <= x_Rh <= 1 (random 32-atom cells, 2 configurations),
    the ordered phases PtRh (40), PtRh3 and Pt3Rh (D0_22) with anti-site defect cells and the analytic two-sublattice
    entropy (same CEF approximation as the paper), liquid 0..1 swept from 2500 K down (T_m Pt 2041 K, Rh 2237 K).
    Solids by QHA (classical level in the assembly); the ordering reactions of the paper lie at 146-258 K, the melting
    range needs the 2000-atom solid TI of mlip_solids_ti.py afterwards.  Assembly 100-2400 K."""
    xs = [0.0, 1 / 32, 2 / 32, 4 / 32, 8 / 32, 12 / 32, 16 / 32, 20 / 32, 24 / 32, 28 / 32, 30 / 32, 31 / 32, 1.0]
    spec = {
        "elements": ["Pt", "Rh"], "masses": [195.084, 102.9055], "x_element": "Rh", "model": "(set by --mlip)",
        "pair_style": "eam/alloy", "pair_coeff": "* * {potential} Pt Rh", "atom_types": {"Pt": 1, "Rh": 2},
        "candidates": {"fcc-Pt": 0.0, "fcc-Rh": 1.0, "PtRh-40": 0.5, "PtRh3-D022": 0.75, "Pt3Rh-D022": 0.25},
        "known_ground_states": ["fcc-Pt", "fcc-Rh", "PtRh-40", "PtRh3-D022"],
        "relax": {"fmax": 1e-3, "cell": True},
        "solids": [
            {"phase": "fcc", "kind": "solution", "base": "fcc-Pt", "repeat": [2, 2, 2], "x": xs, "n_configs": 2, "series": "random", "seed": 0, "supercell": [2, 2, 2], "mesh": 60.0},
            {"phase": "PtRh", "kind": "limited", "base": "PtRh-40", "repeat": [2, 2, 1], "seed": 1, "supercell": [2, 2, 2], "mesh": 60.0,
             "defects": [{"replace": ["Pt", "Rh"], "n": 1}, {"replace": ["Pt", "Rh"], "n": 2}, {"replace": ["Rh", "Pt"], "n": 1}, {"replace": ["Rh", "Pt"], "n": 2}]},
            {"phase": "PtRh3", "kind": "limited", "base": "PtRh3-D022", "repeat": [2, 2, 1], "seed": 2, "supercell": [2, 2, 2], "mesh": 60.0,
             "defects": [{"replace": ["Pt", "Rh"], "n": 1}, {"replace": ["Pt", "Rh"], "n": 2}, {"replace": ["Rh", "Pt"], "n": 1}, {"replace": ["Rh", "Pt"], "n": 2}, {"replace": ["Rh", "Pt"], "n": 3}]},
            {"phase": "Pt3Rh", "kind": "limited", "base": "Pt3Rh-D022", "repeat": [2, 2, 1], "seed": 3, "supercell": [2, 2, 2], "mesh": 60.0,
             "defects": [{"replace": ["Rh", "Pt"], "n": 1}, {"replace": ["Rh", "Pt"], "n": 2}, {"replace": ["Pt", "Rh"], "n": 1}, {"replace": ["Pt", "Rh"], "n": 2}, {"replace": ["Pt", "Rh"], "n": 3}]},
        ],
        "liquids": {"base": "fcc-Pt", "base_hi": [0.5, "fcc-Rh"], "repeat": [4, 4, 4], "x": [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0], "seed": 100,
                    "T_sweep": [2500.0, 1900.0], "T_override": {"0.8": 2000.0, "1.0": 2100.0}, "n_repeats": 1, "n_equilibration_steps": 10000,
                    "n_switching_steps": [10000, 10000], "n_iterations": 3, "mode": "ts", "pressure": 0.0},
        "qha": {"T_max": 2400.0, "T_step": 25.0, "scales": [0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08, 1.10, 1.12], "eos": "vinet", "imaginary": "drop",   # linear scales; fcc Pt needs V/V0 1.14 (a-scale 1.045) at 2400 K (GRACE-2L smoke)
                "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}},
        "assemble": {"T_min": 100.0, "T_max": 2400.0, "T_step": 10.0, "liquid_partial": True, "drop_edge_beyond_liquid": False,
                     "fits": {"fcc": "rk", "liquid": "rk", "PtRh": "poly", "PtRh3": "poly", "Pt3Rh": "poly"}, "poly_order": 3,
                     "poly_orders": {"fcc": 4, "liquid": 4, "PtRh": 1, "PtRh3": 1, "Pt3Rh": 1},
                     "config_terms": {"fcc": "ideal", "PtRh": "sublattice:b32_antisite", "PtRh3": "sublattice:b32_antisite@0.75", "Pt3Rh": "sublattice:b32_antisite@0.25"},
                     "entropy_models": {"PtRh": ["b32_antisite", 0.5], "PtRh3": ["b32_antisite@0.75", 0.75], "Pt3Rh": ["b32_antisite@0.25", 0.25]},
                     "sigma": {"fcc": 0.002, "PtRh": 0.002, "PtRh3": 0.002, "Pt3Rh": 0.002, "liquid": 0.0014},
                     "hull": {"min_width": 0.005, "gap_tol": 2.5}, "sensitivity_samples": 30, "liquid_sigma_floor": 0.0014, "T_residuals": 2000.0,
                     "title": "Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA]", "xlabel": "x_Rh"},
    }
    if smoke:
        spec["solids"] = [dict(spec["solids"][0], x=[0.0, 0.5, 1.0], n_configs=1, supercell=[1, 1, 1], mesh=[4, 4, 4]),
                          dict(spec["solids"][1], repeat=[1, 1, 1], defects=[{"replace": ["Pt", "Rh"], "n": 1}], supercell=[1, 1, 1], mesh=[4, 4, 4])]
        # >= 3 liquid compositions: the assembly keeps only temperatures with >= 3 liquid points (liquid_partial), 2 gave an empty grid (pk 8702)
        spec["liquids"].update({"x": [0.0, 0.5, 1.0], "repeat": [3, 3, 3], "T_sweep": [2500.0, 2200.0], "T_override": {}, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1})
        spec["qha"].update({"T_step": 100.0, "scales": [0.97, 0.99, 1.01, 1.03, 1.06, 1.09]})
        spec["assemble"].update({"T_min": 2000.0, "T_max": 2400.0, "sensitivity_samples": 5, "title": "smoke test Pt-Rh"})
    if not gpu:
        spec["liquids"]["cpu"] = True
    return spec


SYSTEMS = {"alli": (lambda: POT, lambda: candidates(), lambda sm, g: make_spec(sm, g), "ACE Al-Li T-x diagram, stages 01-07 with provenance"),
           "agcu": (lambda: POT_AGCU, candidates_agcu, make_spec_agcu, "EAM Ag-Cu T-x diagram (eutectic + fcc miscibility gap), stages 01-07 with provenance"),
           "nial": (lambda: POT_NIAL, candidates_nial, make_spec_nial, "Ni-Al T-x diagram (B2/L1_2 with composition width), stages 01-07 with provenance"),
           "ptrh": (lambda: None, candidates_ptrh, make_spec_ptrh, "Pt-Rh T-x diagram with a universal MLIP (fcc + ordered PtRh/PtRh3/Pt3Rh + liquid), stages 01-07 with provenance")}
SYSTEM_TAG = {"alli": "Al-Li", "agcu": "Ag-Cu", "nial": "Ni-Al", "ptrh": "Pt-Rh"}


def make_spec(smoke: bool, gpu: bool):
    spec = {
        "elements": ["Al", "Li"], "masses": [26.9815, 6.94], "x_element": "Li", "model": "AlLi-6gen-18May.yace (ACE)",
        "pair_style": "pace", "pair_coeff": "* * {potential} Al Li", "atom_types": {"Al": 1, "Li": 2},
        "candidates": {"fcc-Al": 0.0, "bcc-Li": 1.0, "B32-AlLi": 0.5, "L12-Al3Li": 0.25},
        "known_ground_states": ["fcc-Al", "bcc-Li", "B32-AlLi"],
        "relax": {"fmax": 1e-3, "cell": True},
        "solids": [
            {"phase": "fcc", "kind": "solution", "base": "fcc-Al", "repeat": [2, 2, 2], "x": [0.0, 0.0625, 0.125, 0.1875, 0.25], "n_configs": 2, "series": "random", "seed": 0,
             "supercell": [2, 2, 2], "mesh": 60.0},
            {"phase": "Al3Li", "kind": "point", "base": "L12-Al3Li", "x": [0.25], "supercell": [3, 3, 3], "mesh": 60.0},
            {"phase": "B32", "kind": "limited", "base": "B32-AlLi", "antisites": True, "supercell": [2, 2, 2], "mesh": 60.0},
        ],
        "liquids": {"base": "fcc-Al", "repeat": [4, 4, 4], "x": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5], "seed": 100, "T_sweep": [1100.0, 700.0], "T_override": {"0.1": 800.0},
                    "n_repeats": 1, "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000], "n_iterations": 3, "mode": "ts", "pressure": 0.0},
        "qha": {"T_max": 1100.0, "T_step": 25.0, "scales": [0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05], "eos": "vinet", "imaginary": "drop",
                "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}},
        "assemble": {"T_min": 700.0, "T_max": 1100.0, "T_step": 10.0, "fits": {"fcc": "poly", "liquid": "poly", "B32": "spline"}, "poly_order": 3,
                     "config_terms": {"fcc": "ideal", "B32": "sublattice:b32_antisite"}, "sigma": {"fcc": 0.002, "B32": 0.002, "Al3Li": 0.002, "liquid": 0.0014},
                     "hull": {"min_width": 0.005, "gap_tol": 2.5}, "drop_edge_beyond_liquid": True, "sensitivity_samples": 30, "liquid_sigma_floor": 0.0014,
                     "title": "ACE Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram]", "xlabel": "x_Li"},
    }
    if smoke:
        spec["solids"] = [{"phase": "fcc", "kind": "solution", "base": "fcc-Al", "repeat": [1, 1, 1], "x": [0.0, 0.25], "n_configs": 1, "series": "random", "seed": 0, "supercell": [2, 2, 2], "mesh": [4, 4, 4]},
                          {"phase": "B32", "kind": "limited", "base": "B32-AlLi", "antisites": True, "supercell": [1, 1, 1], "mesh": [4, 4, 4]}]
        spec["liquids"].update({"x": [0.0, 0.2], "repeat": [3, 3, 3], "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1, "T_sweep": [1100.0, 900.0]})
        spec["qha"].update({"T_step": 100.0, "scales": [0.97, 0.99, 1.01, 1.03, 1.05, 1.07]})  # 1100 K needs V0 beyond 1.03^3
        spec["assemble"].update({"T_min": 900.0, "sensitivity_samples": 5, "title": "smoke test"})
    if not gpu:
        spec["liquids"]["cpu"] = True
    return spec


def _load_code(label):
    """load_code that tolerates the duplicate (identical, unused) registrations of ftphase-qha-torch/-mace@mygarden6 (pk 2390/2395, 2391/2396)."""
    from aiida import orm
    from aiida.common.exceptions import MultipleObjectsError

    try:
        return orm.load_code(label)
    except MultipleObjectsError:
        name, _, comp = label.partition("@")
        qb = orm.QueryBuilder().append(orm.Computer, filters={"label": comp}, tag="c").append(orm.Code, with_computer="c", filters={"label": name}, project=["*"])
        codes = sorted((r[0] for r in qb.all()), key=lambda c: c.pk)
        return codes[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", choices=sorted(SYSTEMS), default="alli", help="alli = ACE Al-Li (example 8), agcu = EAM Ag-Cu (example 9), nial = EAM Ni-Al (example 7 in the WorkChain)")
    ap.add_argument("--name", default=None, help="run name (default: alli_ace or agcu_eam)")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--computer", default="mygarden5", help="computer for the calphy jobs (and for QHA unless --qha-computer)")
    ap.add_argument("--qha-computer", default=None, help="run the QHA CalcJobs on another computer, e.g. mygardenx2 (CPU only: torch calculators switch to device cpu; GRACE 1L/2L/3L need a GPU for QHA and are refused)")
    ap.add_argument("--profile", default=os.environ.get("AIIDA_PROFILE", "ftphase"))
    ap.add_argument("--no-gpu", action="store_true", help="run calphy on CPU ranks (default: 1 GPU per liquid)")
    ap.add_argument("--cpu-cores", type=int, default=4, help="LAMMPS ranks per calphy job with --no-gpu")
    ap.add_argument("--qha-cores", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="build the inputs, print them, do not submit")
    ap.add_argument("--mlip", choices=sorted(MLIPS), default="ace", help="alli only: which potential (ace = AlLi-6gen ACE; grace-fs / grace-1l = GRACE foundation models, lmp_gpugrace)")
    ap.add_argument("--li-side", action="store_true", help="alli: add the Li side (bcc random series x_Li 0.75-1, Al2Li3, Al4Li9 point phases); use with --solid-only --t-window 300 1100")
    ap.add_argument("--solid-only", action="store_true", help="skip the liquids and assemble the solid phases alone over --T-window (spec assemble.allow_solid_only); name gets _solid")
    ap.add_argument("--T-window", dest="t_window", nargs=2, type=float, default=None, help="assembly T_min T_max for --solid-only (default ptrh: 100 2400)")
    ap.add_argument("--ends-ti", action="store_true", help="ptrh: calphy solid TI (>= 2000 atoms) of the pure fcc end cells, first configuration per x (spec solids_ti with the x filter); name gets _ti")
    ap.add_argument("--b32-ti", action="store_true", help="alli: add spec['solids_ti'] for B32 (calphy ts 700 -> 880 K, >= 2000-atom cells, GPU); unchanged QHA/liquid CalcJobs are reused from the cache when caching is enabled for ftphase.qha / ftphase.calphy")
    a = ap.parse_args()

    from aiida import load_profile, orm
    from aiida.engine import submit
    from aiida.plugins import WorkflowFactory

    load_profile(a.profile)
    gpu = not a.no_gpu
    pot_fn, cand_fn, spec_fn, descr = SYSTEMS[a.system]
    spec = spec_fn(a.smoke, gpu)
    if a.li_side:
        assert a.system == "alli", "--li-side is for alli"
        spec = li_side_spec(spec)
        cand_fn = lambda: candidates(li_side=True)
    name = (a.name or {"alli": "alli_ace", "agcu": "agcu_eam", "nial": "nial_eam", "ptrh": "ptrh"}[a.system]) + ("_smoke" if a.smoke else "")
    use_mlip = a.mlip != "ace"
    if a.system == "ptrh" and not use_mlip:
        raise SystemExit("ptrh has no system-specific potential: give --mlip (e.g. nequip-oam-m, mace-mpa-0, sevenn-mf-ompa, grace-2l)")           # "ace" = the system's own potential (ACE for Al-Li, EAM for Ag-Cu and Ni-Al)
    lmp_gpu = LMP_GPU; torch_mlip = bool(use_mlip and MLIPS[a.mlip].get("torch")); pot_qha = None
    if a.system != "alli" and not use_mlip:
        lmp_gpu = LMP_GPU
    qha_cpu_host = a.qha_computer in ("mygardenx1", "mygardenx2")   # no GPU there
    if qha_cpu_host and use_mlip and MLIPS[a.mlip].get("qha_gpu") and not torch_mlip:
        raise SystemExit(f"{a.mlip}: the QHA stage needs the GPU (Kokkos-only pair style); do not use --qha-computer {a.qha_computer}")
    if use_mlip:
        ml = MLIPS[a.mlip]
        from ase.data import atomic_numbers
        pc_elems = " ".join(str(atomic_numbers[e]) for e in spec["elements"]) if ml.get("pair_coeff_Z") else " ".join(spec["elements"])   # metatomic wants atomic numbers
        spec.update({"pair_style": ml["pair_style"], "pair_coeff": ml["pair_coeff"].replace("Al Li", pc_elems), "model": ml["model"]})
        if "assemble" in spec and "title" in spec["assemble"]:
            if a.system == "alli":
                spec["assemble"]["title"] = spec["assemble"]["title"].replace("ACE Al-Li", f"{ml['model'].split(' (')[0]} Al-Li")
            else:
                spec["assemble"]["title"] = f"{ml['model'].split(' (')[0]} {SYSTEM_TAG[a.system]}, 0 GPa: QHA solids + calphy liquid [AiiDA]"
        if a.system in ("agcu", "nial"):
            spec.pop("solids_ti", None)   # MLIP comparison: solids by QHA only (user decision 2026-10-30)
        if ml.get("qha_gpu"):
            spec["qha_cmdargs"] = KK_ARGS
        for k in ("qha_pair_style", "qha_calculator", "qha_device", "qha_dtype", "qha_modal"):
            if k in ml:
                spec[k] = ml[k]
        if ml.get("torch"):   # stage 01 relaxations run in a subprocess of the calculator's env (the daemon has no torch)
            spec["qha_python"] = os.path.join(ROOT, "env", ml.get("qha_env") or {"mace": "mace", "metatomic": "metatomic", "deepmd": "deepmd32"}.get(ml["qha_calculator"], "torch"), "bin", "python")
            if qha_cpu_host:
                spec["qha_device"] = "cpu"
        pot_fn = (lambda f=ml["potential"]: f); lmp_gpu = ml["lmp_gpu"]; pot_qha = ml.get("potential_qha")
        name = (a.name or a.system + ml["tag"]) + ("_smoke" if a.smoke else "")
    if a.li_side:
        name += "_liside"
    if a.solid_only:
        spec["assemble"]["allow_solid_only"] = True
        if a.t_window:
            spec["assemble"]["T_min"], spec["assemble"]["T_max"] = float(a.t_window[0]), float(a.t_window[1])
        elif a.system == "ptrh" and not a.smoke:
            spec["assemble"]["T_min"], spec["assemble"]["T_max"] = 100.0, 2400.0
        spec["assemble"]["title"] = spec["assemble"].get("title", "") + " (solids only)"
        name += "_solid"
    if a.ends_ti:
        assert a.system == "ptrh"
        spec["solids_ti"] = {"phases": ["fcc"], "x": [0.0, 1.0], "one_per_x": True, "T_sweep": [1700.0, 2350.0], "T_hi_by_x": [[0.0, 2150.0], [1.0, 2350.0]], "min_atoms": 2000,
                             "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000], "n_iterations": 1, "mode": "ts"}   # Pt 2041 K, Rh 2237 K (expt); caps ~1.05 T_m
        if a.smoke:
            spec["solids_ti"].update({"T_sweep": [1900.0, 2100.0], "T_hi_by_x": [[0.0, 2100.0], [1.0, 2100.0]], "min_atoms": 100, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000]})
        name += "_ti"
    if a.b32_ti:
        assert a.system == "alli"
        # same B32 cells as the QHA series (16 atoms, 2x2x2 of the B32 cube -> 5x5x5 repeat = 2000 atoms); 700 -> 880 K covers the congruent melting
        spec["solids_ti"] = {"phases": ["B32"], "T_sweep": [700.0, 880.0], "min_atoms": 2000, "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000], "n_iterations": 2}
        name = (a.name or "alli_ace_b32ti") + ("_smoke" if a.smoke else "")
    cands = {"".join(c if c.isalnum() else "_" for c in n): orm.StructureData(ase=at) for n, (at, x) in cand_fn().items()}
    for k, s in cands.items():
        s.label = k
    inputs = {
        "spec": orm.Dict(dict=spec),
        "potential": orm.SinglefileData(file=pot_fn()),
        "candidates": cands,
        "qha_code": _load_code(f"{MLIPS[a.mlip].get('qha_code', 'ftphase-qha') if use_mlip else 'ftphase-qha'}@{a.qha_computer or a.computer}"),
        "calphy_code": orm.load_code(f"{MLIPS[a.mlip].get('calphy_code', 'calphy') if use_mlip else 'calphy'}@{a.computer}"),
        "qha_options": orm.Dict(dict={"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1, "num_cores_per_mpiproc": a.qha_cores}, "max_wallclock_seconds": 24 * 3600,
                                      "queue_name": "debug", "withmpi": False,
                                      "custom_scheduler_commands": "#SBATCH --hint=nomultithread" + ("\n#SBATCH --gres=gpu:1" if (use_mlip and MLIPS[a.mlip].get("qha_gpu") and not qha_cpu_host) else "")}),
        "calphy_options": orm.Dict(dict={"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1 if (gpu or torch_mlip) else a.cpu_cores}, "max_wallclock_seconds": 48 * 3600,
                                         "queue_name": "debug", "withmpi": False,
                                         "custom_scheduler_commands": "#SBATCH --hint=nomultithread" + ("\n#SBATCH --gres=gpu:1" if (gpu or torch_mlip) else "")}),
        "calphy_extra": orm.Dict(dict={"gpu": False, "cores": 1, "lammps_executable": lmp_gpu, **({"extra": MLIPS[a.mlip]["calphy_block_extra"]} if MLIPS[a.mlip].get("calphy_block_extra") else {})} if (torch_mlip and not MLIPS[a.mlip].get("calphy_gpu"))
                                  else ({"gpu": True, "lammps_executable": lmp_gpu} if (gpu or torch_mlip) else {"gpu": False, "cores": a.cpu_cores})),   # calphy_gpu (ML-IAP): Kokkos cmdargs + hybrid/scaled/kk like ACE/GRACE
        "metadata": {"label": f"ftphase txdiagram {name}", "description": descr},
    }
    if a.solid_only:
        inputs["skip_liquids"] = orm.Bool(True)
    if pot_qha:
        inputs["potential_qha"] = orm.SinglefileData(file=pot_qha)
    if a.dry_run:
        print(json.dumps(spec, indent=1)); print({k: (v.get_dict() if isinstance(v, orm.Dict) else type(v).__name__) for k, v in inputs.items() if k != "metadata"})
        return
    node = submit(WorkflowFactory("ftphase.txdiagram"), **inputs)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    rec = {"pk": node.pk, "uuid": node.uuid, "name": name, "profile": a.profile, "submitted": time.strftime("%F %T"), "gpu": gpu, "smoke": a.smoke, "computer": a.computer, "qha_computer": a.qha_computer or a.computer, "mlip": a.mlip}
    with open(os.path.join(HERE, "out", f"{name}.pk.json"), "w") as f:
        json.dump(rec, f, indent=1)
    with open(os.path.join(HERE, "out", "submissions.log"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"submitted TxDiagramWorkChain pk={node.pk} uuid={node.uuid} ({name}); follow with: verdi -p {a.profile} process status {node.pk}")


if __name__ == "__main__":
    sys.exit(main())
