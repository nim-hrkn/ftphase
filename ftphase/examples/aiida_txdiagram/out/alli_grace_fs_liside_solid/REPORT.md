# GRACE-FS-OAM Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 11:57:00.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'bcc': 0.002, 'Al3Li': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002, 'Al2Li3': 0.002}

## Key numbers

* invariant reactions:
  * 310-320 K: ['Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+B32', 'Al4Li9+bcc'] -> ['Al3Li+B32', 'Al3Li+fcc', 'B32+bcc']
  * 330-340 K: ['Al3Li+B32', 'Al3Li+fcc', 'B32+bcc'] -> ['B32+bcc', 'B32+fcc']
  * 940-950 K: ['B32+bcc', 'B32+fcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.225)-B32(0.438); B32(0.562)-bcc(0.750)
* two-phase regions at 800 K: fcc(0.240)-B32(0.438); B32(0.562)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.250)-B32(0.438); B32(0.562)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562); B32(0.562)-bcc(0.750)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 950-1100 K (16 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30 samples)
* 700 K fcc+B32: x_a = 0.228 +/- 0.012, x_b = 0.438 +/- 0.000 (30/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30 samples)
* 800 K fcc+B32: x_a = 0.241 +/- 0.011, x_b = 0.438 +/- 0.000 (30/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30 samples)
* 900 K fcc+B32: x_a = 0.248 +/- 0.004, x_b = 0.438 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 0.001679047277181166, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00016760379618730437, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
