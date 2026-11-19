# nial_eam: uniform compound procedure

Classification read from the hull: {'B2': 'range phase', 'L12': 'range phase (lower bound: window edge)', 'Ni2Al3': 'not stable', 'NiAl3': 'not stable'}

## Width of each compound (x of the second element; '*' = at the edge of the window)

| T (K) | NiAl3 | Ni2Al3 | B2 | L12 |
|---|---|---|---|---|
| 960 | — | — | 0.480–0.598 | 0.740–0.870* |
| 1060 | — | — | 0.479–0.601 | 0.737–0.870* |
| 1160 | — | — | 0.479–0.604 | 0.734–0.870* |
| 1260 | — | — | 0.480–0.606 | 0.731–0.859 |
| 1360 | — | — | 0.482–0.607 | 0.728–0.845 |
| 1460 | — | — | 0.486–0.608 | 0.726–0.829 |
| 1560 | — | — | 0.488–0.599 | 0.733–0.815 |
| 1660 | — | — | 0.491–0.569 | — |
| 1760 | — | — | 0.496–0.535 | — |

Highest temperature on the hull: {'NiAl3': None, 'Ni2Al3': None, 'B2': 1800.0, 'L12': 1580.0}

## Inputs per compound

* NiAl3: {"n_sites": 128, "sizes": [32, 64, 128], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_1200K_by_size_eV": {"32": 0.941, "64": 1.206, "128": 1.115}, "size_converged_0.02eV": false, "constitutional_defects": {"A_rich": "Va_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_Va_on_B_1000_1400_1800_eV": [2.03, 1.31, 1.72], "cells_B_rich": "12/12", "w_B_on_A_1000_1400_1800_eV": [-4.35, -5.36, -3.76], "half_width": 0.094}
* Ni2Al3: {"n_sites": 135, "sizes": [40, 90, 135], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_1200K_by_size_eV": {"40": 1.225, "90": 1.292, "135": 1.285}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "11/12", "w_A_on_B_1000_1400_1800_eV": [-1.66, -1.04, -0.3], "cells_B_rich": "12/12", "w_B_on_A_1000_1400_1800_eV": [1.76, 1.98, 1.93], "half_width": 0.089}
* B2: {"n_sites": 250, "sizes": [54, 128, 250], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_1200K_by_size_eV": {"54": 1.687, "128": 1.715, "250": 1.744}, "size_converged_0.02eV": false, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_1000_1400_1800_eV": [-0.58, -0.23, 0.82], "cells_B_rich": "21/21", "w_B_on_A_1000_1400_1800_eV": [2.06, 2.14, 1.86], "half_width": 0.12}
* L12: {"n_sites": 256, "sizes": [32, 108, 256], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_1200K_by_size_eV": {"32": 1.097, "108": 1.144, "256": 1.146}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_1000_1400_1800_eV": [1.69, 2.11, 2.62], "cells_B_rich": "21/21", "w_B_on_A_1000_1400_1800_eV": [0.77, 0.78, 0.73], "half_width": 0.12}
