# pyiron potentials-workshop-2022, phase_diagram/tutorial_2 (Al-Li, EAM) -- run here on 2026-10-21

Source: https://github.com/pyiron/potentials-workshop-2022 (`phase_diagram/`, `resources/lammps/potentials/`).
Environment: `../../env/pyiron` (pyiron_base / pyiron_atomistics GitHub HEAD, calphy 2.3.0, conda-forge LAMMPS).

Files
- `tutorial_2.ipynb`, `helpers.py`, `LiAl_poscar`, `img/`: upstream copies (helpers.py: path of AlLi_poscar made absolute).
- `AlLi_poscar`: created here. Upstream ships only `LiAl_poscar` (Li atoms first) but `helpers.create_structures`
  replaces atoms in the second half of the cell with Al, i.e. it assumes Al first / Li second. This file is
  `LiAl_poscar` with the two species blocks swapped.
- `resources/`: workshop potential files; `Al-atomicrex` and `LiAl-atomicrex` are the EAM used by the tutorial.
- `run_calculations.py`: the 18 Calphy jobs of the tutorial (pure Al fcc / liquid / Al-in-B32, and x_Li = 0.1..0.5 for
  fcc, liquid, B32), identical settings (4x4x4 fcc = 256 atoms, 432-atom B32 cell, 800-1000 K reversible scaling,
  5000 equilibration + 5000 switching steps). Jobs run 4 at a time with 4 MPI ranks each, each in its own cwd under
  `scratch/` because calphy writes `*-conf.data-*.data` into the current directory. `run_calculations.log`.
- `analyze_phase_diagram.py` -> `analysis/`: free energies at 800/900/1000 K (`free_energies.tsv`), the tutorial's
  analysis (ideal-mixing S_conf added to fcc and B32, cubic fits, liquid end-point normalisation, fsolve common
  tangents at 800/900/950 K: `free_energy_*K.png`, `common_tangents_tutorial.tsv`) and, added here, a T-x diagram from
  the lower convex hull of the three fitted curves at 5 K steps (`phase_diagram_Tx.png`, `two_phase_regions.tsv`).

Deviations forced by calphy 2.3.0
- `xp_alli` (Al atoms on the B32 lattice) melts at 800-1000 K and `x3_lqd` (liquid, x_Li = 0.4) solidifies; calphy 2
  aborts these (`MeltedError` / `SolidifiedError`), calphy 1.0.3 of the workshop did not check. Both were rerun with
  `tolerance.solid_fraction = 0` and `tolerance.liquid_fraction = 1` (`run_calculations.py --disable-phase-checks
  --only=xp_alli,x3_lqd`, `run_calculations_rerun.log`). Their free energies are those of a metastable/unstable state
  and only serve as end points of the tutorial's cubic fits, exactly as in the tutorial.

Results (this EAM, small cells, 5 ps switching; qualitative only, as the tutorial itself says)
- Common tangents (tutorial method): 800 K fcc-B32 x = 0.193 / 0.255; 900 K 0.191 / 0.246;
  950 K fcc-liquid 0.113 / 0.137 and B32-liquid 0.322 / 0.292.
- T-x diagram: fcc + B32 two-phase region x = 0.19-0.25 below ~863 K; eutectic at ~863 K, x ~ 0.22; fcc + liquid and
  B32 + liquid regions above. Experimental Al-Li eutectic: ~870 K, x_Li ~ 0.26. Pure Al: fcc/liquid crossing between
  900 and 1000 K (experiment 933 K).
