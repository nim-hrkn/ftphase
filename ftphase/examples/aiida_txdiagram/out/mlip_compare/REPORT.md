# Same system, different MLIPs: ace (AlLi-6gen-18May.yace (ACE)) vs grace-fs (GRACE-FS-OAM (foundation, FS, 6 A)) vs grace-1l (GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export)) vs grace-2l (GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export)) vs sevenn-0 (SevenNet-0 (11Jul2024, MPtrj; oeq deployment)) vs sevenn-mf-ompa (SevenNet-MF-ompa (modal mpa; oeq deployment)) vs mace-mpa-0 (MACE-MPA-0 medium (float32))

## 01: 0 K formation energies of the candidate phases (eV/atom, vs the pure end members of the same MLIP) and hull status

| candidate | x | ace E_form | ace on hull | grace-fs E_form | grace-fs on hull | grace-1l E_form | grace-1l on hull | grace-2l E_form | grace-2l on hull | sevenn-0 E_form | sevenn-0 on hull | sevenn-mf-ompa E_form | sevenn-mf-ompa on hull | mace-mpa-0 E_form | mace-mpa-0 on hull |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fcc-Al | 0.0 | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes |
| L12-Al3Li | 0.25 | -0.0941 | yes | -0.1301 | yes | -0.0940 | yes | -0.0897 | yes | -0.1113 | yes | -0.0928 | no (+0 meV) | -0.0868 | no (+2 meV) |
| B32-AlLi | 0.5 | -0.1789 | yes | -0.2114 | yes | -0.1776 | yes | -0.1763 | yes | -0.1817 | yes | -0.1864 | yes | -0.1775 | yes |
| bcc-Li | 1.0 | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes | +0.0000 | yes |

Relaxed volumes (A^3/atom): ace: fcc-Al 16.54, bcc-Li 20.40, B32-AlLi 16.13, L12-Al3Li 16.26; grace-fs: fcc-Al 16.90, bcc-Li 18.91, B32-AlLi 15.77, L12-Al3Li 16.21; grace-1l: fcc-Al 16.43, bcc-Li 20.39, B32-AlLi 16.02, L12-Al3Li 16.25; grace-2l: fcc-Al 16.42, bcc-Li 20.28, B32-AlLi 15.85, L12-Al3Li 16.13; sevenn-0: fcc-Al 16.46, bcc-Li 20.14, B32-AlLi 16.08, L12-Al3Li 16.30; sevenn-mf-ompa: fcc-Al 16.55, bcc-Li 20.43, B32-AlLi 16.08, L12-Al3Li 16.27; mace-mpa-0: fcc-Al 16.47, bcc-Li 20.17, B32-AlLi 15.94, L12-Al3Li 16.37

## 03A: solids, G(T) - G(lowest T) of the end members (eV/atom; vibrational + thermal expansion, classical level)

| phase, x | T (K) | ace | grace-fs | grace-1l | grace-2l | sevenn-0 | sevenn-mf-ompa | mace-mpa-0 |
|---|---|---|---|---|---|---|---|---|
| fcc, x = 0.0 | 700 | -0.2124 (from 0 K) | -0.2812 (from 0 K) | -0.2133 (from 0 K) | -0.2130 (from 0 K) | -0.2780 (from 0 K) | -0.2248 (from 0 K) | -0.2271 (from 0 K) |
| fcc, x = 0.0 | 800 | -0.2671 (from 0 K) | -0.3516 (from 0 K) | -0.2680 (from 0 K) | -0.2677 (from 0 K) | -0.3480 (from 0 K) | -0.2808 (from 0 K) | -0.2838 (from 0 K) |
| B32, x = 0.5 | 700 | -0.1880 (from 0 K) | -0.1935 (from 0 K) | -0.1872 (from 0 K) | -0.1863 (from 0 K) | -0.2092 (from 0 K) | -0.1877 (from 0 K) | -0.1862 (from 0 K) |
| B32, x = 0.5 | 800 | -0.2369 (from 0 K) | -0.2437 (from 0 K) | -0.2361 (from 0 K) | -0.2354 (from 0 K) | -0.2615 (from 0 K) | -0.2371 (from 0 K) | -0.2348 (from 0 K) |
| Al3Li, x = 0.25 | 700 | -0.1932 (from 0 K) | -0.2164 (from 0 K) | -0.1982 (from 0 K) | -0.1955 (from 0 K) | -0.2314 (from 0 K) | -0.1993 (from 0 K) | -0.2070 (from 0 K) |
| Al3Li, x = 0.25 | 800 | -0.2438 (from 0 K) | -0.2718 (from 0 K) | -0.2495 (from 0 K) | -0.2466 (from 0 K) | -0.2898 (from 0 K) | -0.2506 (from 0 K) | -0.2598 (from 0 K) |

## 03A: fcc Al thermal expansion V(T)/V(T_min) and B32 anti-site cost

* ace: fcc Al V(800 K)/V(0 K) = 1.0590; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -60.6 meV, x=0.5000: +0.0 meV, x=0.5625: +114.0 meV
* grace-fs: fcc Al V(800 K)/V(0 K) = 1.1179; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -91.9 meV, x=0.5000: +0.0 meV, x=0.5625: +136.3 meV
* grace-1l: fcc Al V(800 K)/V(0 K) = 1.0621; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -71.5 meV, x=0.5000: +0.0 meV, x=0.5625: +123.8 meV
* grace-2l: fcc Al V(800 K)/V(0 K) = 1.0623; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -65.9 meV, x=0.5000: +0.0 meV, x=0.5625: +120.0 meV
* sevenn-0: fcc Al V(800 K)/V(0 K) = 1.1144; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -80.6 meV, x=0.5000: +0.0 meV, x=0.5625: +123.3 meV
* sevenn-mf-ompa: fcc Al V(800 K)/V(0 K) = 1.0429; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -53.7 meV, x=0.5000: +0.0 meV, x=0.5625: +117.0 meV
* mace-mpa-0: fcc Al V(800 K)/V(0 K) = 1.0467; B32 G(x) at lowest T relative to x = 0.5: x=0.4375: -67.6 meV, x=0.5000: +0.0 meV, x=0.5625: +119.0 meV

## 03B: liquid minus solid at the same composition (eV/atom; negative = liquid stable)

| x | solid | T (K) | ace | grace-fs | grace-1l | grace-2l | sevenn-0 | sevenn-mf-ompa | mace-mpa-0 |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | fcc | 700 | +0.0218 | +0.0252 | +0.0211 | +0.0253 | +0.0547 | +0.0287 | +0.0316 |
| 0.0 | fcc | 800 | +0.0102 | +0.0257 | +0.0088 | +0.0138 | +0.0575 | +0.0194 | +0.0227 |
| 0.0 | fcc | 900 | -0.0014 | +0.0276 | -0.0039 | +0.0025 | +0.0604 | +0.0095 | +0.0133 |
| 0.5 | B32 | 700 | +0.0216 | +0.0143 | +0.0161 | +0.0146 | +0.0254 | +0.0292 | +0.0170 |
| 0.5 | B32 | 800 | +0.0073 | -0.0002 | +0.0016 | +0.0011 | +0.0152 | +0.0159 | +0.0031 |
| 0.5 | B32 | 900 | -0.0079 | -0.0158 | -0.0139 | -0.0132 | +0.0037 | +0.0014 | -0.0119 |
| 0.25 | Al3Li | 700 | - | - | - | - | - | - | - |
| 0.25 | Al3Li | 800 | - | - | - | - | - | - | - |
| 0.25 | Al3Li | 900 | - | - | - | - | - | - | - |

## 06-07: diagram features

| feature | ace | grace-fs | grace-1l | grace-2l | sevenn-0 | sevenn-mf-ompa | mace-mpa-0 |
|---|---|---|---|---|---|---|---|
| lowest T with liquid (eutectic bracket) | 770.0 K; [{'phase_a': 'fcc', 'x_a': 0.16364377524805, 'phase_b': 'liquid', 'x_b': 0.30798874073804}, {'phase_a': 'liquid', 'x_a': 0.3186591999339, 'phase_b': 'B32', 'x_b': 0.48252157594643}] | 750.0 K; [{'phase_a': 'fcc', 'x_a': 0.22897993508857, 'phase_b': 'liquid', 'x_b': 0.31614408553575}, {'phase_a': 'liquid', 'x_a': 0.3225, 'phase_b': 'B32', 'x_b': 0.4375}] | 730.0 K; [{'phase_a': 'fcc', 'x_a': 0.19933310830403, 'phase_b': 'liquid', 'x_b': 0.32749027318013}, {'phase_a': 'liquid', 'x_a': 0.34103111618082, 'phase_b': 'B32', 'x_b': 0.47651984883512}] | 760.0 K; [{'phase_a': 'fcc', 'x_a': 0.18077421020613, 'phase_b': 'liquid', 'x_b': 0.35424178872743}, {'phase_a': 'liquid', 'x_a': 0.37255999420705, 'phase_b': 'B32', 'x_b': 0.49778514103138}] | 940.0 K; [{'phase_a': 'fcc', 'x_a': 0.25, 'phase_b': 'liquid', 'x_b': 0.5}] | 860.0 K; [{'phase_a': 'fcc', 'x_a': 0.1646686003817, 'phase_b': 'liquid', 'x_b': 0.31794680655389}, {'phase_a': 'liquid', 'x_a': 0.33473752065243, 'phase_b': 'B32', 'x_b': 0.50250503185564}] | 780.0 K; [{'phase_a': 'fcc', 'x_a': 0.23758585322855, 'phase_b': 'liquid', 'x_b': 0.38480443796636}, {'phase_a': 'liquid', 'x_a': 0.3863133195589, 'phase_b': 'B32', 'x_b': 0.49025988424088}] |
| pure Al melting bracket | [880.0, 890.0] | [950.0, 960.0] | None | None | None | None | [1030.0, 1040.0] |
| B32 + liquid present up to | 850 K | 800 K | 810 K | 810 K | none | 910 K | 820 K |
| fcc solvus x_Li (fcc+B32 tangent) | 700 K: 0.140; 800 K: nan | 700 K: 0.225; 800 K: nan | 700 K: 0.194; 800 K: nan | 700 K: 0.168; 800 K: nan | 700 K: 0.250; 800 K: 0.250 | 700 K: 0.132; 800 K: 0.154 | 700 K: 0.209; 800 K: nan |
| Al3Li appears | never | never | never | never | never | never | never |
| same-phase segments (fit noise) | [{'phase': 'fcc', 'T': 700.0, 'x_a': 0.025241947403874, 'x_b': 0.11783408410735}, {'phase': 'fcc', 'T': 710.0, 'x_a': 0. | [] | [] | [] | [{'phase': 'fcc', 'T': 1010.0, 'x_a': 0.244375, 'x_b': 0.25}, {'phase': 'fcc', 'T': 1020.0, 'x_a': 0.243125, 'x_b': 0.25 | [] | [] |
| invariants | 760-770 K; 790-800 K; 850-860 K | 740-750 K; 800-810 K | 720-730 K; 810-820 K | 750-760 K; 810-820 K | 930-940 K; 1000-1010 K | 850-860 K; 910-920 K | 770-780 K; 820-830 K |
