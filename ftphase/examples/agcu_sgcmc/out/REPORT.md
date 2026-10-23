# Ag-Cu fcc miscibility gap from semi-grand-canonical MC (EAM, fix atom/swap + NPT MD), no free-energy fit

runs: [800.0, 900.0, 1000.0] K, up/down sweeps of dmu; points per sweep 36

| T (K) | x_alpha (tangent) | x_beta (tangent) | x_alpha (jump, up) | x_beta (jump, down) | dmu* (eV) | hysteresis dmu (eV) |
|---|---|---|---|---|---|---|
| 800 | 0.027 | 0.990 | 0.081 | 0.967 | -0.660 | +0.080 |
| 900 | 0.050 | 0.972 | 0.080 | 0.950 | -0.660 | +0.040 |
| 1000 | 0.126 | 0.914 | 0.186 | 0.845 | -0.650 | +0.020 |

## Comparison with the ideal + Redlich-Kister fit of the random-cell free energies (AiiDA run, example 9)

| T (K) | SGC x_alpha | RK x_alpha | SGC x_beta | RK x_beta |
|---|---|---|---|---|
| 800 | 0.027 | 0.042 | 0.990 | 0.987 |
| 900 | 0.050 | 0.045 | 0.972 | 0.978 |
| 1000 | 0.126 | 0.078 | 0.914 | 0.955 |
