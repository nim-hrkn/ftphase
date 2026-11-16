import pytest
import numpy as np


def test_sqs_sqsgenerator_counts_and_metadata():
    pytest.importorskip("sqsgenerator")
    from ase.build import bulk

    from ftphase.structures import sqs_sqsgenerator

    base = bulk("Al", "fcc", a=4.05, cubic=True).repeat((2, 2, 2))
    sqs, meta = sqs_sqsgenerator(base, {"Al": 28, "Li": 4}, iterations=20000)
    assert sqs.get_chemical_symbols().count("Li") == 4 and len(sqs) == 32
    assert np.isfinite(meta["objective"]) and meta["n_atoms"] == 32
    assert meta["shell_radii"] is not None and len(meta["sro"]) >= 1
    # the cross-pair Warren-Cowley parameter of the first shell is close to zero for an SQS
    sro = np.asarray(meta["sro"]); assert sro.ndim == 3 and abs(sro[0, 0, 1]) < 0.2


def test_sqs_icet_is_reproducible_with_a_seed():
    """The seed must reach icet's annealing (random_seed): the same seed gives the same occupation, so that different potentials
    can share one SQS; before 2026-11-16 only numpy's global seed was set and every call returned another configuration."""
    pytest.importorskip("icet")
    from ase.build import bulk
    from ftphase.structures import sqs_icet
    prim = bulk("Al", "fcc", a=4.05); sc = prim.repeat((2, 2, 4))
    occ = []
    for _ in range(2):
        at, _meta = sqs_icet(prim, [["Al", "Li"]], [5.0], {"Al": 0.75, "Li": 0.25}, len(sc), method="supercells", n_steps=500, seed=3, supercells=[sc.copy()])
        f = np.round(sc.cell.scaled_positions(at.get_positions()) * 4).astype(int) % 4
        occ.append("".join(np.array(at.get_chemical_symbols())[np.lexsort((f[:, 2], f[:, 1], f[:, 0]))]))
    assert occ[0] == occ[1] and occ[0].count("Li") == 4
