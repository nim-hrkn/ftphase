import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture(scope="session")
def project_root():
    return ROOT


@pytest.fixture(scope="session")
def workshop_tsv():
    p = os.path.join(ROOT, "pyiron-examples", "workshop2022-phase-diagram", "analysis", "free_energies.tsv")
    if not os.path.exists(p):
        pytest.skip("workshop free_energies.tsv not present")
    return p


@pytest.fixture(scope="session")
def calphy_example_dir():
    p = os.path.join(ROOT, "calphy-examples")
    if not os.path.isdir(p):
        pytest.skip("calphy-examples not present")
    return p


@pytest.fixture(scope="session")
def anphon_thermo():
    p = os.path.expanduser("~/kino/Claude/Projects/ALAMODE/alamode_test/PbTe_mattersim/PbTe_NA0.thermo")
    if not os.path.exists(p):
        pytest.skip("anphon thermo file not present")
    return p


# AiiDA test fixtures (temporary sqlite profile, no broker); only when aiida-core is installed.
try:
    import aiida  # noqa: F401

    pytest_plugins = ["aiida.tools.pytest_fixtures"]
except ImportError:  # pragma: no cover
    pass
