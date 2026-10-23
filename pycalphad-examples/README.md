# pycalphad upstream examples (local run copy)

Copied from https://github.com/pycalphad/pycalphad tag 0.11.2 (2026-06-05) `examples/` (flat layout of that tag).
Environment: `../env/pycalphad` (conda-forge deps + pip pycalphad 0.11.2; conda-forge only has 0.10.1).
Executed copies with outputs are written to `executed/`; per-notebook status in `status.tsv`, log in `run_all.log`.
Run order follows upstream docs: phase diagrams -> computing properties -> high throughput -> metastability/reference states.

Run of 2026-10-21: all 17 notebooks executed without error (second pass with the inline matplotlib backend; the first pass used MPLBACKEND=Agg and produced no figures). The 50 embedded figures are also exported as PNG in `figures/<notebook>_<n>.png`.
