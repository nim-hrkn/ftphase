# alli_grace_fs: uniform compound procedure

Classification read from the hull: {'Al2Li3': 'range phase (lower bound: window edge)', 'Al3Li': 'range phase', 'Al4Li9': 'range phase', 'B32': 'range phase (lower bound: window edge)'}

## Width of each compound (x of the second element; '*' = at the edge of the window)

| T (K) | Al3Li | B32 | Al2Li3 | Al4Li9 |
|---|---|---|---|---|
| 300 | 0.219–0.242 | 0.406–0.583* | 0.689–0.689* | 0.741–0.752 |
| 400 | — | 0.406–0.594* | 0.689–0.689* | — |
| 500 | — | 0.406–0.594* | — | 0.692–0.698 |
| 600 | — | 0.406–0.588* | — | 0.684–0.696 |
| 700 | — | 0.406–0.562* | — | 0.670–0.703 |

Highest temperature on the hull: {'Al3Li': 340.0, 'B32': 700.0, 'Al2Li3': 440.0, 'Al4Li9': 700.0}

## Inputs per compound

* Al3Li: {"n_sites": 144, "sizes": [32, 108, 144], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"32": 0.225, "108": 0.216, "144": 0.206}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_at_T_eV": {"300": 0.4, "700": 0.43}, "cells_B_rich": "12/12", "w_B_on_A_at_T_eV": {"300": 0.43, "700": 0.48}, "window": [0.167, 0.333]}
* B32: {"n_sites": 128, "sizes": [16, 32, 128], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"16": 0.614, "32": 0.606, "128": 0.597}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_at_T_eV": {"300": 0.27, "700": 0.14}, "cells_B_rich": "12/12", "w_B_on_A_at_T_eV": {"300": -0.23, "700": -0.18}, "window": [0.406, 0.594]}
* Al2Li3: {"n_sites": 135, "sizes": [30, 60, 135], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"30": 0.353, "60": 0.34, "135": 0.339}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_at_T_eV": {"300": -0.04, "700": -0.08}, "cells_B_rich": "11/12", "w_B_on_A_at_T_eV": {"300": 0.07, "700": 0.01}, "window": [0.511, 0.689]}
* Al4Li9: {"n_sites": 104, "sizes": [26, 52, 104], "defects_ok": ["A_on_B", "B_on_A", "Va_on_A", "Va_on_B"], "defects_failed": [], "antisite_pair_by_size_eV": {"26": 0.188, "52": 0.14, "104": 0.124}, "size_converged_0.02eV": true, "constitutional_defects": {"A_rich": "A_on_B", "B_rich": "B_on_A"}, "cells_A_rich": "12/12", "w_A_on_B_at_T_eV": {"300": 3.03, "700": 2.62}, "cells_B_rich": "12/12", "w_B_on_A_at_T_eV": {"300": 0.55, "700": 1.52}, "window": [0.577, 0.808]}
