"""AiiDA plugin layer of ftphase: the T-x diagram workflow (stages 01-07) as a WorkChain.

Entry points (``pyproject.toml``):

* ``ftphase.qha``      CalcJob  stage 03A, phonopy QHA of one solid cell (``ftphase-qha-run``)
* ``ftphase.calphy``   CalcJob  stage 03B, one calphy calculation (``calphy_kernel``)
* ``ftphase.txdiagram`` WorkChain  01/02 (calcfunction ``prepare_cells``) -> 03A/03B CalcJobs in
  parallel -> 04-07 (calcfunction ``assemble_diagram``) -> REPORT.md, png, tables

The daemon that runs the WorkChain must have ``ftphase`` and its dependencies importable
(``env/ftphase`` holds aiida-core, ase, phonopy, icet, calphy, lammps); the CalcJobs run through
Slurm with codes that activate the same environment.  See ``examples/aiida_txdiagram/README.md``.
"""
