# calphy upstream examples (local run copy)

Copied from https://github.com/ICAMS/calphy (commit 67caa5b, 2026-10-09) `examples/`.
Changes from upstream: all `queue` blocks use `scheduler: slurm` (partition debug, 8GB, 48 h) and activate `../env/calphy`;
the upstream recorded outputs of example_13 were moved to `example_13/recorded/`.
`example_01/input-mp.yaml` needs a Materials Project API key and is not run.
example_01/input.yaml was run with scheduler local (run_all.log, status.tsv); everything else via sbatch (submit_slurm.log, jobs 22478-22512 on 2026-10-21).
Licence: Academic Software Licence (non-commercial), see upstream LICENSE.
