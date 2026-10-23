"""ftphase: finite-temperature phase diagrams from MLIP free energies.

The package implements the workflow stages of ``docs/obsolete_workflow.html`` that no
upstream example (calphy, pycalphad, pyiron) covers, as thin layers on top of
public code:

* stage 01 (:mod:`ftphase.validate`) 0 K convex hull, EOS, comparison with known
  ground states;
* stage 02A (:mod:`ftphase.structures`) composition / sublattice / vacancy
  series and SQS via icet (Ångqvist et al. 2019);
* stage 03A (:mod:`ftphase.qha`) phonon free energies via phonopy (Togo 2023)
  or ALAMODE ``.thermo`` files, Vinet / Birch–Murnaghan QHA, eq. (D1)-(D2);
* stage 04A (:mod:`ftphase.configurational`) ideal, multi-sublattice and
  density-of-states configurational free energies, eq. (E1), (E9)-(E13);
* stage 04B (:mod:`ftphase.quantum`) classical-to-quantum harmonic correction;
* stage 03B (:mod:`ftphase.calphy_io`) calphy input generation and result
  reading (Menon et al. 2021);
* stage 05 (:mod:`ftphase.assemble`) one free-energy table with explicit units,
  reference states and flags; export to calphy's ``PhaseDiagram`` / TDB;
* stage 06 (:mod:`ftphase.equilibrium`) multi-phase lower convex hull with
  point phases and limited-range phases, common tangents, eq. (H1)-(H5);
* stage 07 (:mod:`ftphase.diagram`) T–x diagram, invariant reactions, Monte
  Carlo error sensitivity.

Equation labels refer to ``docs/obsolete_workflow.html`` of the PhaseDiagram project.
"""

from . import units  # noqa: F401
from .records import FreeEnergyTable, COLUMNS  # noqa: F401
from .equilibrium import PhaseCurve, PointPhase, lower_hull, equilibrium_at_T  # noqa: F401

__version__ = "0.1.0"
