# Menon et al. 2024, Al-Li phase diagram with EAM (pyiron/potential_publication, 04_phase_diagram)

Source notebooks: `01_running_calculations.ipynb` (how the Calphy jobs were set up) and `02_EAM_phase_diagram.ipynb`
(post-processing of the published dataset). Dataset: https://edmond.mpg.de/api/access/datafile/248316 (959 MB plain tar,
84 Calphy jobs + 1 pyiron TableJob, pyiron 2024, calphy 1.3.6), unpacked into `phase_diagram_eam/` with pyiron HEAD.

What had to change versus the 2024 notebook (see `plot_phase_diagram_eam.py`):
- the archive must be laid out as `AlLi_eam_archive/{export.csv, AlLi_eam/AlLi_phase_dia}` for pyiron's current `unpack`;
  `unpack` needs a sqlite database (`PYIRONSQLFILE`), the file-based mode (`PYIRONDISABLE=True`) cannot import;
- the table job is looked up by type instead of pk 2998;
- the EAM dataset has only fcc, b32 and liquid (no Al3Li), so that phase is skipped;
- calphy 2.3.0: `plot_phase_diagram(tangents, T, tangent_types, phases)`.

Outputs: `phase_diagram_eam.png`, `two_phase_regions_eam.tsv` (T, phase pair, x1, x2 for every lower-hull segment).
Note: for this EAM the liquid is below fcc already at 700 K for x_Li > ~0.16 (checked on the raw free energies), so the
diagram shows an fcc+liquid region down to 700 K and no fcc+b32 region. That is a property of the potential/dataset,
not of the post-processing; the paper's HDNNP/ACE datasets (separate downloads) give the physical diagram.
