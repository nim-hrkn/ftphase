# MACE-MPA-0 fp32 Al liquid 1100->700 K: ML-IAP unified vs pair_style mace (calphy ts, 256 atoms)

| | pair_style mace fp32 (pk 4356) | ML-IAP unified fp32 (this run) | diff (meV/atom) |
|---|---|---|---|
| free_energy at 1100 K (eV/atom) | -4.187605 | -4.187613 | -0.01 |
| work at 1100 K (eV/atom) | 4.070026 | 4.071203 | +1.18 |
| reference_system at 1100 K (eV/atom) | 0.909432 | 0.910534 | +1.10 |
| dissipation at 1100 K (eV/atom) | 0.000709 | 0.001060 | +0.35 |
| ts_dissipation at 1100 K (eV/atom) | 0.000979 | 0.001051 | +0.07 |
| error at 1100 K (eV/atom) | 0.000401 | 0.000202 | -0.20 |
| G(1100 K) (eV/atom) | -4.187605 ± 0.00000 | -4.187613 ± 0.00000 | -0.01 |
| G(1000 K) (eV/atom) | -4.110988 ± 0.00015 | -4.110843 ± 0.00006 | +0.15 |
| G(900 K) (eV/atom) | -4.037360 ± 0.00012 | -4.037227 ± 0.00010 | +0.13 |
| G(800 K) (eV/atom) | -3.967606 ± 0.00015 | -3.967502 ± 0.00010 | +0.10 |
| G(700 K) (eV/atom) | -3.901996 ± 0.00017 | -3.901848 ± 0.00008 | +0.15 |
| vol/atom at 1100 K (Å^3) pair_style mace fp32 | 19.4262 | | |
| vol/atom at 1100 K (Å^3) ML-IAP unified fp32 | 19.4139 | | |

| | pair_style mace fp32 (pk 4356) | ML-IAP unified fp32 (this run) |
|---|---|---|
| LAMMPS s/step (median of the logged 10000-step MLIP segments) | 0.1570 | 0.0852 |
| logged segments | 9 | 9 |
| calphy wall time (h, calphy.log first to last line) | 9.57 | 5.14 |

reference job dir: /home/kino/aiida_run/ftphase/b0/7b/edaa-1e7f-40d7-8e83-2df70be3b9bd/lqd_x0.00-ts-lqd_x0.00.data-liquid-1100-0
this run: /home/kino/kino/Claude/Projects/PhaseDiagram/ftphase/examples/calphy_mliap_mace/lqd_x0.00-ts-lqd_x0.00.data-liquid-1100-0
The pk 4356 job shared the GPU with other AiiDA jobs at times; its s/step is an upper bound.
