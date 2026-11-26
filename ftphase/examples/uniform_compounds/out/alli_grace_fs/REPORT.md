# alli_grace_fs: uniform compound procedure

Classification read from the hull: {'Al2Li3': 'range phase', 'Al3Li': 'range phase (lower bound: window edge)', 'Al4Li9': 'not stable', 'B32': 'range phase (lower bound: window edge)'}

## Width of each compound (x of the second element; '*' = at the edge of the window)

| T (K) | Al3Li | B32 | Al2Li3 | Al4Li9 |
|---|---|---|---|---|
| 300 | 0.167–0.287* | 0.446–0.504 | 0.559–0.681 | — |
| 400 | 0.167–0.285* | 0.406–0.529* | 0.603–0.681 | — |
| 500 | 0.167–0.279* | 0.406–0.536* | 0.602–0.681 | — |
| 600 | 0.167–0.305* | 0.406–0.530* | 0.596–0.681 | — |
| 700 | 0.167–0.314* | 0.406–0.476* | 0.519–0.681 | — |

Highest temperature on the hull: {'Al3Li': 700.0, 'B32': 700.0, 'Al2Li3': 700.0, 'Al4Li9': None}

## Inputs per compound

* Al3Li: {"n_sites": 144, "sizes": [32, 108, 144], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"32": 0.225, "108": 0.216, "144": 0.206}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "k_max_A_rich": 12, "w_A_on_B_at_T_eV": {"300": 0.4, "700": 0.43}, "cells_B_rich": "12/12", "k_max_B_rich": 12, "w_B_on_A_at_T_eV": {"300": 0.43, "700": 0.48}, "window": [0.167, 0.333], "lattice_phase_T": [300.0, 500.0, 700.0], "lattice_minus_perfect_at_x0_meV": [-6.3, -13.1, -22.4]}
* B32: {"n_sites": 128, "sizes": [16, 32, 128], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"16": 0.614, "32": 0.606, "128": 0.597}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "k_max_A_rich": 12, "w_A_on_B_at_T_eV": {"300": 0.27, "700": 0.14}, "cells_B_rich": "12/12", "k_max_B_rich": 12, "w_B_on_A_at_T_eV": {"300": -0.23, "700": -0.18}, "window": [0.406, 0.594]}
* Al2Li3: {"n_sites": 135, "sizes": [30, 60, 135], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"30": 0.353, "60": 0.34, "135": 0.339}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "k_max_A_rich": 12, "w_A_on_B_at_T_eV": {"300": -0.04, "700": -0.08}, "cells_B_rich": "11/12", "k_max_B_rich": 12, "w_B_on_A_at_T_eV": {"300": 0.07, "700": 0.01}, "window": [0.511, 0.689], "lattice_phase_T": [300.0, 500.0, 700.0], "lattice_minus_perfect_at_x0_meV": [-7.9, -10.3, -18.2]}
* Al4Li9: {"n_sites": 104, "sizes": [26, 52, 104], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"26": 0.188, "52": 0.14, "104": 0.124}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "k_max_A_rich": 12, "w_A_on_B_at_T_eV": {"300": 3.03, "700": 2.62}, "cells_B_rich": "12/12", "k_max_B_rich": 12, "w_B_on_A_at_T_eV": {"300": 0.55, "700": 1.52}, "window": [0.577, 0.808]}

Sides at the edge of the sampled window (to be extended with more defects per cell): {'Al2Li3': ['A_rich', 'B_rich'], 'Al3Li': ['A_rich', 'B_rich'], 'B32': ['A_rich']}
