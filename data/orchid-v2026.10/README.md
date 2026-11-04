# ORCHID v2026.10 (Zenodo deposits, downloaded 2026-11-03)

Paper: Arróyave, Saal, Shin, "ORCHID: Connecting Finite-Temperature Thermodynamic
Evidence to Computational Materials Discovery", arXiv:2610.41164 (local copy
`papers/2610.41164v1.pdf`). Licence CC BY 4.0 (quotes from papers remain under the
publishers' copyright). Umbrella record 10.5281/zenodo.23736065.

Downloaded for the stage-07 comparison (`07_invariants.tsv`, `07_two_phase_regions.tsv`)
of the ftphase runs (Al-Li, Al-Ni, Ag-Cu, Cu-Zr). Everything except this README is
gitignored; re-download with the URLs below and check `zip/MD5SUMS` and each
`MANIFEST.sha256` (all passed on 2026-11-03).

| Folder | Zenodo DOI | zip | md5 | Use |
|---|---|---|---|---|
| `literature/` | 10.5281/zenodo.23735569 | orchid-literature-v2026.10.zip (46.0 MB) | 97dbd208b0b507e89a343a614e2cc800 | literature values; invariant reactions for `07_invariants.tsv` |
| `assessed-phase-assemblages/` | 10.5281/zenodo.23735996 | orchid-assessed-phase-assemblages-v2026.10.zip (12.8 MB) | ad21faf2cec12dcf2d08e8d3d94da0e7 | (T, x, phases) interior points of Okamoto handbook diagrams for `07_two_phase_regions.tsv` |
| `phase-registry/` | 10.5281/zenodo.23735970 | orchid-phase-registry-v2026.10.zip (11.2 MB) | d241fa9ddfb4470fa65efc1779a54e49 | phase ids / model-phase names used by the other two |

Download URL pattern: `https://zenodo.org/api/records/<record>/files/<zip>/content`
(records 23735569, 23735996, 23735970).

## Where the data is

- Literature values per system: `literature/orchid-literature-v2026.10/literature/systems/<SYS>.json`
  (`AL-LI`, `AL-NI`, `AG-CU`, `CU-ZR`; key `records`). Schema in `literature/SCHEMA.md`.
  Invariant records: `property == "INVARIANT_TEMPERATURE"`, `temperature_K`, `reaction.printed`,
  `phases[].model_phase` (e.g. `LIQUID`, `FCC_A1`, `BCC_4SL` for AlLi B32), `phase_compositions`
  (mole fraction), `evidence_class` (experimental / model / DFT / unspecified),
  `flags.extraction_accepted`, `flags.espei_ready`, `flags.plausibility` (pycalphad check against a
  named TDB), `uncertainty`, `locator` (DOI / page / table / row).
  Counts (all classes): Al-Li 31 invariant records (12 experimental), Al-Ni 110 (49), Ag-Cu 9 (4),
  Cu-Zr 239 (150).
- Assessed assemblages: `assessed-phase-assemblages/.../assessed-phase-assemblages/records.jsonl.gz`
  (also `.csv`, `.parquet`), one record per phase field: `system`, `T_K`, `x` (`x_component`),
  `assemblage[].canonical_name` / `phase_id`, `coordinate_uncertainty`, citations.
  Points: Al-Li 14, Al-Ni 17, Ag-Cu 6, Cu-Zr 28 (the 28 used in the paper's one-shot score).
  `espei-zpf*/` hold the same points as ESPEI ZPF datasets.
