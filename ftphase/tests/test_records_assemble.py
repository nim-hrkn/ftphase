import numpy as np
import pandas as pd
import pytest

from ftphase.units import KB_EV
from ftphase.records import FreeEnergyTable, COLUMNS
from ftphase.assemble import relative_to_pure, add_configurational_term, interpolate_T, builder_from_table, to_calphy_dataframe, to_calphy_phase_diagram
from ftphase.configurational import b32_antisite_site_fractions, ideal_entropy
from ftphase.diagram import scan


def make_table():
    rows = []
    for T in (600.0, 800.0, 1000.0):
        for x in (0.0, 0.25, 0.5, 0.75, 1.0):
            rows.append({"phase": "fcc", "kind": "solution", "x": x, "T": T, "P_GPa": 0.0, "G": -3.0 - 1e-3 * T + 0.1 * x * (1 - x), "G_err": 0.001, "reference_state": "abs", "quantum": "classical"})
        rows.append({"phase": "AB", "kind": "point", "x": 0.5, "T": T, "P_GPa": 0.0, "G": -3.02 - 1e-3 * T, "G_err": 0.002, "reference_state": "abs", "quantum": "classical"})
    return FreeEnergyTable.from_rows(rows, {"origin": "test"})


def test_schema_and_checks(tmp_path):
    t = make_table()
    assert list(t.df.columns) == COLUMNS
    assert t.check() == []
    t.to_tsv(tmp_path / "t.tsv")
    t2 = FreeEnergyTable.from_tsv(tmp_path / "t.tsv")
    assert len(t2) == len(t) and t2.meta["origin"] == "test"
    # inconsistent reference state is reported
    df = t.df.copy(); df.loc[0, "reference_state"] = "other"
    assert any("reference" in p for p in FreeEnergyTable.from_dataframe(df).check())
    with pytest.raises(ValueError):
        FreeEnergyTable.from_rows([{"phase": "a", "kind": "weird", "x": 0.1, "T": 1.0, "P_GPa": 0, "G": 0}])


def test_relative_to_pure_and_config_term():
    t = make_table()
    r = relative_to_pure(t, "fcc", "fcc")
    d = r.df
    assert np.allclose(d[(d.phase == "fcc") & (d.x == 0)]["G"], 0.0)
    assert np.allclose(d[(d.phase == "fcc") & (d.x == 1)]["G"], 0.0)
    assert np.allclose(d[(d.phase == "fcc") & (d.x == 0.5)]["G"], 0.025)
    # ideal term, eq. (E2)
    c = add_configurational_term(r, "fcc", "ideal")
    g = c.df[(c.df.phase == "fcc") & (c.df.x == 0.5) & (c.df["T"] == 1000.0)]["G"].iloc[0]
    assert abs(g - (0.025 - 1000.0 * ideal_entropy(0.5))) < 1e-12
    with pytest.raises(ValueError):
        add_configurational_term(c, "fcc", "ideal")  # no double counting
    # sublattice term on the point phase is zero at stoichiometry
    s = add_configurational_term(r, "AB", "sublattice", site_model=b32_antisite_site_fractions)
    assert np.allclose(s.df[s.df.phase == "AB"]["G"], r.df[r.df.phase == "AB"]["G"])


def test_interpolate_and_builder_and_scan():
    t = make_table()
    ti = interpolate_T(t, [600.0, 700.0, 900.0, 1000.0, 1100.0])
    assert set(ti.temperatures()) == {600.0, 700.0, 900.0, 1000.0}  # 1100 K is outside -> dropped
    b = builder_from_table(ti, fit="spline")
    phases = b(700.0)
    names = sorted(p.name for p in phases)
    assert names == ["AB", "fcc"]
    reg = scan(b, [700.0, 900.0])
    assert {"AB"} <= set(reg["phase_a"]) | set(reg["phase_b"])


def test_calphy_bridge():
    pytest.importorskip("calphy")
    t = make_table()
    cdf = to_calphy_dataframe(t)
    assert set(cdf.columns) >= {"phase", "composition", "temperature", "free_energy"}
    assert len(cdf) == 6  # 5 fcc compositions + 1 point
    pdg = to_calphy_phase_diagram(t, reference_element="B")
    assert pdg.phases == ["AB", "fcc"] or set(pdg.phases) == {"AB", "fcc"}
    assert pdg.composition_intervals["AB"] == (0.5, 0.5)


def test_builder_single_composition_becomes_point():
    import numpy as np
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import builder_from_table
    from ftphase.equilibrium import PointPhase, PhaseCurve
    rows = []
    for x in (0.0, 0.5, 1.0):
        rows.append({"phase": "liq", "kind": "solution", "x": x, "T": 1000.0, "P_GPa": 0.0, "G": -1.0 + 0.1 * x, "G_err": 0.0, "V": np.nan, "model": "m", "reference_state": "r",
                     "method": "mm", "config_entropy": "liquid-ti", "quantum": "classical", "n_atoms": 1, "source": "s"})
    rows.append({"phase": "B2", "kind": "limited", "x": 0.46, "T": 1000.0, "P_GPa": 0.0, "G": -1.2, "G_err": 0.0, "V": np.nan, "model": "m", "reference_state": "r",
                 "method": "mm", "config_entropy": "sublattice", "quantum": "classical", "n_atoms": 1, "source": "s"})
    b = builder_from_table(FreeEnergyTable.from_rows(rows, {}), fit="poly", poly_order=2)
    ph = {p.name: p for p in b(1000.0)}
    assert isinstance(ph["B2"], PointPhase) and isinstance(ph["liq"], PhaseCurve)
