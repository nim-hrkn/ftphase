# NequIP / Allegro on Matbench Discovery: LAMMPS deployment survey (2026-10-30)

Web survey (subagent, primary sources). [V] = verified on the cited page, [I] = inferred.

## Leaderboard entries (https://matbench-discovery.materialsproject.org/, model YAMLs in github.com/janosh/matbench-discovery/models/{nequip,allegro})

| Entry | Training set | F1 | κ_SRME | CPS | Params | Weights |
|---|---|---|---|---|---|---|
| NequIP-OAM-XL | MPtrj+OMat24+sAlex | 0.906 | 0.125 | 0.886 | 32.1 M | nequip.net:mir-group/NequIP-OAM-XL:0.1 |
| **NequIP-OAM-L** | MPtrj+OMat24+sAlex | 0.893 | 0.166 | 0.870 | 9.6 M | nequip.net:mir-group/NequIP-OAM-L:0.1 |
| Allegro-OAM-L | MPtrj+OMat24+sAlex | 0.895 | 0.319 | 0.840 | 9.7 M | nequip.net:mir-group/Allegro-OAM-L:0.1 |
| NequIP-MP-L / Allegro-MP-L | MPtrj | 0.761 / 0.751 | 0.466 / 0.504 | | | benchmarking only (Zenodo note) |
| NequIP-GNoME | GNoME | 0.829 | – | – | | not downloadable |

Paper: arXiv:2607.28461 (Kavanagh … Kozinsky, v2 2026-09-19): NequIP preferred over Allegro for phonons (Allegro strictly local).
Weights: `*.nequip.zip` package files, CC-BY-4.0, Zenodo 10.5281/zenodo.18775904 (record "0.1a" with fixed packages; prefer it),
e.g. https://zenodo.org/api/records/18775904/files/NequIP-OAM-L-0.1.nequip.zip/content (78.5 MB). The `nequip.net:...` ID downloads
and caches automatically. NequIP-OAM-L: r_c 6 Å, 6 layers, l_max 3, ZBL on. Allegro-OAM-L: r_c 7 Å, 4 layers, ZBL off.

## LAMMPS routes (nequip docs, integrations/lammps/)
- (a) `nequip-compile ... --mode aotinductor --target pair_nequip|pair_allegro` + `pair_nequip_allegro` plugin (patched LAMMPS
  >= patch_10Sep2025, `NEQUIP_AOT_COMPILE=ON`, cuDNN; Kokkos only for `pair_allegro`; `pair_nequip` single rank). TorchScript mode is
  dead on torch >= 2.10. hybrid/scaled not mentioned.
- (b) **ML-IAP** (beta): `pip install nequip [nequip-allegro] cython==3.0.11 cupy-cuda12x`;
  `nequip-prepare-lmp-mliap nequip.net:mir-group/NequIP-OAM-L:0.1 NequIP-OAM-L.nequip.lmp.pt --modifiers enable_OpenEquivariance`
  (output must end in `.nequip.lmp.pt`; Allegro: `enable_CuEquivarianceContracter` / `enable_TritonContracter`);
  input `atom_modify map yes / newton on / pair_style mliap unified X.nequip.lmp.pt 0 / pair_coeff * * Al Li`, run with
  `-k on g 1 -sf kk -pk kokkos newton on neigh half`. Same LAMMPS build flags as env/lammps-gpu-mliap (ML-IAP + PYTHON + KOKKOS, shared lib).
  Multi-rank yes (paper: up to 256 GPUs). Set `TORCHINDUCTOR_AUTOGRAD_CACHE=1 TORCHINDUCTOR_FX_GRAPH_CACHE=1 TORCHINDUCTOR_CACHE_DIR=...`
  so each calphy job does not recompile.

## Versions
nequip 0.19.1 (2026-09-01): python >= 3.10, torch >= 2.2 (no upper bound), e3nn >= 0.6,< 0.7, lightning >= 2.6, torchmetrics >= 1.6.
nequip-allegro 0.8.3: only `nequip >= 0.18`. torch 2.11 + cu128 + py3.12 within range (compat page lists issues for 2.9.1/2.10 only).
Fits env/torch (sevenn e3nn 0.6, cupy present; lightning new); not env/mace (e3nn 0.4.4). OpenEquivariance: torch >= 2.7, gcc >= 9.

## Recommendation
Try **NequIP-OAM-L 0.1 via ML-IAP** in `lmp_gpumliap` (PYTHONHOME = env/torch after `pip install nequip`): best phonons among
the downloadable NequIP/Allegro models at a size the RTX 3060 handles; OAM-XL as a second step. Verify locally what no doc states:
`hybrid/scaled/kk` energy and virial (λ=1, λ=1.222, UFM mix) with the nequip wrapper, speed at 108/256 atoms, and that nequip +
openequivariance + lightning coexist with sevenn and mattersim in env/torch. Fallback: Allegro-OAM-L (worse phonons, strictly local).
