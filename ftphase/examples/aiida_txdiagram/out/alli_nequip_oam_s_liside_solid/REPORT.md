# NequIP-OAM-S 0.1 Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 07:39:07.  Classical level, 0.0 GPa, model NequIP-OAM-S 0.1 (ML-IAP, OpenEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'bcc': 0.002, 'Al3Li': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002, 'Al2Li3': 0.002}

## Key numbers

* invariant reactions:
  * 460-470 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc', 'bcc+bcc']
  * 540-550 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc', 'bcc+bcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'bcc+bcc']
  * 650-660 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'bcc+bcc'] -> ['B32+bcc', 'B32+fcc', 'bcc+bcc']
  * 670-680 K: ['B32+bcc', 'B32+fcc', 'bcc+bcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc', 'bcc+bcc']
  * 900-910 K: ['B32+B32', 'B32+bcc', 'B32+fcc', 'bcc+bcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc', 'bcc+bcc', 'fcc+fcc']
  * 950-960 K: ['B32+B32', 'B32+bcc', 'B32+fcc', 'bcc+bcc', 'fcc+fcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc', 'fcc+fcc']
* two-phase regions at 700 K: fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562); B32(0.562)-bcc(0.750); bcc(0.750)-bcc(0.931)
* two-phase regions at 800 K: fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562); B32(0.562)-bcc(0.750); bcc(0.750)-bcc(0.938)
* two-phase regions at 900 K: fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562); B32(0.562)-bcc(0.750); bcc(0.750)-bcc(0.796)
* two-phase regions at 1000 K: fcc(0.062)-fcc(0.126); fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562); B32(0.562)-bcc(0.750)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 680-1100 K (43 temperatures)
* bcc+bcc x = 0.750-0.780 at T = 880-880 K (1 temperatures)
* bcc+bcc x = 0.750-0.790 at T = 890-890 K (1 temperatures)
* bcc+bcc x = 0.750-0.800 at T = 900-910 K (2 temperatures)
* bcc+bcc x = 0.750-0.810 at T = 920-920 K (1 temperatures)
* bcc+bcc x = 0.750-0.820 at T = 930-930 K (1 temperatures)
* bcc+bcc x = 0.750-0.830 at T = 940-950 K (2 temperatures)
* bcc+bcc x = 0.750-0.920 at T = 650-660 K (2 temperatures)
* bcc+bcc x = 0.750-0.930 at T = 670-730 K (7 temperatures)
* bcc+bcc x = 0.750-0.940 at T = 530-870 K (26 temperatures)
* bcc+bcc x = 0.750-1.000 at T = 470-520 K (6 temperatures)
* fcc+fcc x = 0.060-0.110 at T = 910-940 K (4 temperatures)
* fcc+fcc x = 0.060-0.120 at T = 950-990 K (5 temperatures)
* fcc+fcc x = 0.060-0.130 at T = 1000-1080 K (8 temperatures)
* fcc+fcc x = 0.060-0.140 at T = 1050-1100 K (3 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (11/30 samples)
* 700 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (11/30 samples)
* 700 K B32+B32: x_a = 0.438 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 700 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (19/30 samples)
* 700 K bcc+bcc: x_a = 0.750 +/- 0.000, x_b = 0.931 +/- 0.000 (30/30 samples)
* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.438 +/- 0.000 (30/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (1/30 samples)
* 800 K B32+Al2Li3: x_a = 0.466 +/- 0.000, x_b = 0.600 +/- 0.000 (1/30 samples)
* 800 K B32+B32: x_a = 0.438 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (29/30 samples)
* 800 K bcc+bcc: x_a = 0.750 +/- 0.000, x_b = 0.938 +/- 0.000 (30/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.438 +/- 0.000 (30/30 samples)
* 900 K B32+B32: x_a = 0.438 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30 samples)
* 900 K bcc+bcc: x_a = 0.750 +/- 0.000, x_b = 0.796 +/- 0.000 (30/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.438 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 2.9900541119693473e-15, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00014019655460986477, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
