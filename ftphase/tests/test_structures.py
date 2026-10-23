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
