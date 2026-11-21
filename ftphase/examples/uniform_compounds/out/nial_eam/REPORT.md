# nial_eam: uniform compound procedure

Classification read from the hull: {'B2': 'range phase', 'L12': 'range phase (lower bound: window edge)', 'Ni2Al3': 'not stable', 'NiAl3': 'not stable'}

## Width of each compound (x of the second element; '*' = at the edge of the window)

| T (K) | NiAl3 | Ni2Al3 | B2 | L12 |
|---|---|---|---|---|
| 960 | — | — | 0.483–0.599 | 0.738–0.891* |
| 1060 | — | — | 0.482–0.602 | 0.735–0.888 |
| 1160 | — | — | 0.482–0.604 | 0.733–0.874 |
| 1260 | — | — | 0.483–0.606 | 0.730–0.859 |
| 1360 | — | — | 0.485–0.607 | 0.728–0.843 |
| 1460 | — | — | 0.488–0.607 | 0.726–0.827 |
| 1560 | — | — | 0.489–0.603 | 0.731–0.813 |
| 1660 | — | — | 0.492–0.580 | — |
| 1760 | — | — | 0.497–0.548 | — |

Highest temperature on the hull: {'NiAl3': None, 'Ni2Al3': None, 'B2': 1800.0, 'L12': 1580.0}

## Inputs per compound

* NiAl3: {"n_sites": 128, "sizes": [32, 64, 128], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"32": 0.941, "64": 1.206, "128": 1.115}, "size_converged_0.02eV": false, "constitutional_defects": {"A_rich": "Va_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_Va_on_B_at_T_eV": {"1000": 5.77, "1800": 3.98}, "cells_B_rich": "12/12", "w_B_on_A_at_T_eV": {"1000": -2.79, "1800": -6.78}, "window": [0.172, 0.344]}
* Ni2Al3: {"n_sites": 135, "sizes": [40, 90, 135], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"40": 1.225, "90": 1.292, "135": 1.285}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "11/12", "w_A_on_B_at_T_eV": {"1000": -6.9, "1800": -5.87}, "cells_B_rich": "12/12", "w_B_on_A_at_T_eV": {"1000": 3.55, "1800": 3.16}, "window": [0.311, 0.489]}
* B2: {"n_sites": 250, "sizes": [54, 128, 250], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"54": 1.687, "128": 1.715, "250": 1.744}, "size_converged_0.02eV": false, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_at_T_eV": {"1000": 0.06, "1800": 3.0}, "cells_B_rich": "21/21", "w_B_on_A_at_T_eV": {"1000": 1.7, "1800": 0.41}, "window": [0.452, 0.65]}
* L12: {"n_sites": 256, "sizes": [32, 108, 256], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"32": 1.097, "108": 1.144, "256": 1.146}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_at_T_eV": {"1000": -0.21, "1800": 2.55}, "cells_B_rich": "21/21", "w_B_on_A_at_T_eV": {"1000": 0.81, "1800": 0.88}, "window": [0.703, 0.891]}
