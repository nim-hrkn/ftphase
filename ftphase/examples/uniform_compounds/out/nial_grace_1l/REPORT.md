# nial_grace_1l: uniform compound procedure

Classification read from the hull: {'B2': 'range phase', 'L12': 'range phase', 'Ni2Al3': 'line compound', 'NiAl3': 'line compound'}

## Width of each compound (x of the second element; '*' = at the edge of the window)

| T (K) | NiAl3 | Ni2Al3 | B2 | L12 |
|---|---|---|---|---|
| 960 | 0.249–0.250 | 0.399–0.400 | 0.474–0.586 | 0.727–0.773 |
| 1060 | 0.249–0.250 | 0.396–0.400 | 0.467–0.594 | 0.727–0.777 |
| 1160 | — | 0.396–0.399 | 0.459–0.600 | 0.728–0.778 |
| 1260 | — | 0.397–0.399 | 0.451–0.605 | 0.729–0.771 |
| 1360 | — | 0.399–0.399 | 0.454–0.604 | 0.722–0.769 |
| 1460 | — | — | 0.456–0.606 | 0.722–0.765 |
| 1560 | — | — | 0.458–0.608 | 0.722–0.762 |
| 1660 | — | — | 0.463–0.603 | — |
| 1760 | — | — | 0.496–0.597 | — |

Highest temperature on the hull: {'NiAl3': 1100.0, 'Ni2Al3': 1360.0, 'B2': 1820.0, 'L12': 1580.0}

## Inputs per compound

* NiAl3: {"n_sites": 128, "sizes": [32, 64, 128], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"32": 1.734, "64": 1.628, "128": 1.747}, "size_converged_0.02eV": false, "constitutional_defects": {"A_rich": "Va_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "k_max_A_rich": 12, "w_Va_on_B_at_T_eV": {"1000": 0.69, "1800": 26.46}, "cells_B_rich": "12/12", "k_max_B_rich": 12, "w_B_on_A_at_T_eV": {"1000": 4.87, "1800": 30.36}, "window": [0.172, 0.344]}
* Ni2Al3: {"n_sites": 135, "sizes": [40, 135], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"40": 2.353, "135": 2.35}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "10/12", "k_max_A_rich": 12, "w_A_on_B_at_T_eV": {"1000": 0.07, "1800": -0.63}, "cells_B_rich": "12/12", "k_max_B_rich": 12, "w_B_on_A_at_T_eV": {"1000": 0.46, "1800": 0.23}, "window": [0.311, 0.489]}
* B2: {"n_sites": 250, "sizes": [54, 128, 250], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"54": 1.958, "128": 1.949, "250": 2.092}, "size_converged_0.02eV": false, "constitutional_defects": {"A_rich": "Va_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "21/21", "k_max_A_rich": 40, "w_Va_on_B_at_T_eV": {"1000": 0.21, "1800": -5.33}, "cells_B_rich": "21/21", "k_max_B_rich": 40, "w_B_on_A_at_T_eV": {"1000": 0.44, "1800": -12.0}, "window": [0.405, 0.65]}
* L12: {"n_sites": 256, "sizes": [32, 108, 256], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"32": 1.141, "108": 1.157, "256": 1.165}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "18/18", "k_max_A_rich": 30, "w_A_on_B_at_T_eV": {"1000": 2.2, "1800": 1.53}, "cells_B_rich": "18/18", "k_max_B_rich": 30, "w_B_on_A_at_T_eV": {"1000": -0.68, "1800": -0.56}, "window": [0.633, 0.867]}

Sides at the edge of the sampled window (to be extended with more defects per cell): {}
