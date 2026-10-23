import os
import numpy as np
import pytest
from ase.build import bulk

from ftphase.structures import composition_series, vacancy_series, sqs_icet, write_lammps_data
from ftphase.configurational import sublattice_entropy, exact_entropy
from ftphase.validate import hull_0K, compare_ground_states, formation_energies, eos_scan, relax, melting_check_inputs
from ftphase.calphy_io import calculation_block, write_series_input, slurm_queue, read_calphy_results


def test_composition_series_integer_counts_and_seed():
    base = bulk("Al", "fcc", a=4.05, cubic=True).repeat((2, 2, 2))  # 32 atoms
    s = composition_series(base, "Li", [0.1, 0.25], seed=3, n_configs=2)
    assert len(s) == 4
    assert s[0].counts == {"Al": 29, "Li": 3} and abs(s[0].x_actual - 3 / 32) < 1e-12
    assert s[2].counts == {"Al": 24, "Li": 8}
    # same seed -> same structure; different seed -> different positions (almost surely)
    s_again = composition_series(base, "Li", [0.1], seed=3)
    assert s_again[0].atoms.get_chemical_symbols() == s[0].atoms.get_chemical_symbols()
    assert s[0].atoms.get_chemical_symbols() != s[1].atoms.get_chemical_symbols()
    sf, nc = s[0].site_fractions()
    assert abs(sf[0]["Li"] - 3 / 32) < 1e-12 and nc == [32.0]


def test_vacancy_series_site_fractions():
    base = bulk("Al", "fcc", a=4.05, cubic=True).repeat((2, 2, 2))
    v = vacancy_series(base, list(range(32)), [0, 2], seed=1)
    assert len(v[1].atoms) == 30
    sf, nc = v[1].site_fractions()
    assert abs(sf[0]["Va"] - 2 / 32) < 1e-12 and abs(sf[0]["Al"] - 30 / 32) < 1e-12
    assert sublattice_entropy(sf, nc, basis="site") > 0


@pytest.mark.slow
def test_sqs_icet_small_fcc():
    pytest.importorskip("icet")
    prim = bulk("Al", "fcc", a=4.05)
    sqs, meta = sqs_icet(prim, [["Al", "Li"]], cutoffs=[6.0], target_concentrations={"Al": 0.75, "Li": 0.25}, max_size=8, method="enumeration")
    assert len(sqs) in (4, 8) and sqs.get_chemical_symbols().count("Li") / len(sqs) == 0.25
    assert np.isfinite(meta["cluster_vector_deviation"]) and meta["n_atoms"] == len(sqs)


def test_write_lammps_data(tmp_path):
    a = bulk("Al", "fcc", a=4.05, cubic=True)
    a[0].symbol = "Li"
    p = write_lammps_data(a, tmp_path / "x.data", ["Al", "Li"])
    txt = open(p).read()
    assert "2 atom types" in txt and "Masses" in txt


def test_hull_0K_and_known_ground_states():
    names = ["A", "A2B", "AB", "AB3", "B"]
    x = [0.0, 1 / 3, 0.5, 0.75, 1.0]
    e = [-3.0, -3.3, -3.4, -2.6, -2.0]
    h = hull_0K(names, x, e)
    on = set(h[h.on_hull]["name"])
    assert on == {"A", "A2B", "AB", "B"}  # AB3 (e_form -0.35) lies above the AB-B chord
    ef = formation_energies(x, e)
    assert abs(ef[2] - (-3.4 - (-2.5))) < 1e-12
    rep = compare_ground_states(h, ["AB", "AB3", "XYZ"])
    st = dict(zip(rep["name"], rep["status"]))
    assert st["AB"] == "on hull" and st["AB3"] == "above hull" and st["XYZ"] == "not computed"
    try:
        from ftphase.validate import hull_0K_pymatgen
        eah = hull_0K_pymatgen(names, ("Cu", "Au"), x, e)
        assert np.allclose(eah, h.set_index("name").loc[names, "e_above_hull"].to_numpy(), atol=1e-8)
    except ImportError:
        pass


def test_eos_and_relax_with_emt():
    from ase.calculators.emt import EMT
    a = bulk("Al", "fcc", a=4.05)
    r = relax(a, EMT(), fmax=1e-4)
    assert r.converged and not r.transformed
    fit, V, E = eos_scan(r.atoms, EMT(), scales=(0.96, 0.98, 1.0, 1.02, 1.04))
    assert abs(fit.V0 - r.volume_per_atom) / r.volume_per_atom < 0.01
    assert 20 < fit.B0_GPa < 120  # EMT Al ~ 40 GPa; sanity range


def test_calphy_input_roundtrip(tmp_path, monkeypatch):
    import yaml
    monkeypatch.chdir(tmp_path)  # calphy's parser writes *.data copies into the cwd
    q = slurm_queue("/x/env/calphy")
    a = bulk("Al", "fcc", a=4.05, cubic=True); a[0].symbol = "Li"
    data = write_lammps_data(a, tmp_path / "fcc_x0.1.data", ["Al", "Li"])
    blk = calculation_block("fcc_x0.1", "ts", ["Al", "Li"], [26.98, 6.94], data, "pace", "* * AlLi.yace Al Li", [600, 1000], queue=q, folder_prefix="fcc_x0.1")
    p = write_series_input(tmp_path / "in.yaml", [blk])
    d = yaml.safe_load(open(p))
    assert d["calculations"][0]["mode"] == "ts" and d["calculations"][0]["queue"]["scheduler"] == "slurm"
    assert d["calculations"][0]["tolerance"] == {"solid_fraction": 0.7, "liquid_fraction": 0.05}
    blk2 = calculation_block("m", "fe", ["Al"], [26.98], data, "pace", "* * x.yace Al", 800, phase_checks=False)
    assert blk2["tolerance"] == {"solid_fraction": 0.0, "liquid_fraction": 1.0}
    # calphy's own validating parser accepts it
    calphy = pytest.importorskip("calphy")
    from calphy.input import read_inputfile
    calcs = read_inputfile(p)
    assert calcs[0].mode == "ts" and calcs[0].element == ["Al", "Li"]
    melting_check_inputs(tmp_path / "melt.yaml", "Cu", 63.546, "FCC", 3.61, "eam", "* * Cu_u3.eam", 1300.0)
    assert read_inputfile(str(tmp_path / "melt.yaml"))[0].mode == "melting_temperature"


def test_calphy_gpu_block(tmp_path, monkeypatch):
    import yaml
    from ftphase.calphy_io import gpu_pair_style, needs_hybrid_scaled, GPU_CMDARGS
    monkeypatch.chdir(tmp_path)
    assert gpu_pair_style("pace") == "pace product"
    assert gpu_pair_style("pace product") == "pace product"
    assert gpu_pair_style("pace recursive") == "pace recursive"
    assert gpu_pair_style("eam/alloy") == "eam/alloy"
    assert needs_hybrid_scaled("fe", "solid") is False
    assert needs_hybrid_scaled("fe", "liquid") and needs_hybrid_scaled("ts", "solid")
    a = bulk("Al", "fcc", a=4.05, cubic=True)
    data = write_lammps_data(a, tmp_path / "fcc.data", ["Al", "Li"])
    q = slurm_queue("/x/env", cores=4)
    blk = calculation_block("g", "ts", ["Al", "Li"], [26.98, 6.94], data, "pace", "* * x.yace Al Li", [600, 1000],
                            queue=q, gpu=True, lammps_executable="/x/bin/lmp_gpu", check_executable=False)
    assert blk["pair_style"] == "pace product"
    assert blk["md"] == {"cmdargs": GPU_CMDARGS.format(n_gpus=1)}
    assert blk["queue"]["cores"] == 1 and blk["queue"]["options"] == {"gres": "gpu:1"}
    assert blk["lammps_executable"] == "/x/bin/lmp_gpu"
    assert q["cores"] == 4 and "options" not in q  # caller's queue dict untouched
    blk2 = calculation_block("c", "fe", ["Al"], [26.98], data, "pace", "* * x.yace Al", 800, queue=q)
    assert "md" not in blk2 and blk2["pair_style"] == "pace" and blk2["queue"]["cores"] == 4
    # two GPUs -> two ranks, gres gpu:2
    blk3 = calculation_block("g2", "fe", ["Al"], [26.98], data, "pace", "* * x.yace Al", 800, queue=q, gpu=True, n_gpus=2)
    assert blk3["queue"]["cores"] == 2 and blk3["queue"]["options"]["gres"] == "gpu:2" and "-k on g 2" in blk3["md"]["cmdargs"]
    # calphy's validating parser accepts md.cmdargs, queue.options and lammps_executable
    pytest.importorskip("calphy")
    from calphy.input import read_inputfile
    p = write_series_input(tmp_path / "gpu.yaml", [blk, blk3])
    calcs = read_inputfile(p)
    assert calcs[0].md.cmdargs == GPU_CMDARGS.format(n_gpus=1) and calcs[0].queue.options == {"gres": "gpu:1"}
    assert calcs[0].lammps_executable == "/x/bin/lmp_gpu" and calcs[0].pair_style == ["pace product"]


def test_calphy_gpu_capability_check(tmp_path, monkeypatch):
    """A binary without hybrid/scaled/kk may run the solid fe step but not ts/liquid on the GPU."""
    import ftphase.calphy_io as cio
    fake = {"executable": "fake", "version": "x", "kokkos": True, "pace_kk": True, "hybrid_scaled_kk": False,
            "ufm": True, "ti_spring": True, "plain_fe_solid": True, "all_modes": False}
    monkeypatch.setattr(cio, "gpu_capability", lambda exe: dict(fake))
    monkeypatch.chdir(tmp_path)
    a = bulk("Al", "fcc", a=4.05, cubic=True)
    data = write_lammps_data(a, tmp_path / "fcc.data", ["Al"])
    ok = cio.calculation_block("s", "fe", ["Al"], [26.98], data, "pace", "* * x.yace Al", 800, gpu=True, lammps_executable="fake")
    assert ok["md"]["cmdargs"].startswith("-k on g 1")
    with pytest.raises(ValueError, match="hybrid/scaled/kk"):
        cio.calculation_block("l", "fe", ["Al"], [26.98], data, "pace", "* * x.yace Al", 800, reference_phase="liquid", gpu=True, lammps_executable="fake")
    with pytest.raises(ValueError, match="hybrid/scaled/kk"):
        cio.calculation_block("t", "ts", ["Al"], [26.98], data, "pace", "* * x.yace Al", [800, 1000], gpu=True, lammps_executable="fake")
    fake["pace_kk"] = False
    with pytest.raises(ValueError, match="pace/kk"):
        cio.calculation_block("s", "fe", ["Al"], [26.98], data, "pace", "* * x.yace Al", 800, gpu=True, lammps_executable="fake")


@pytest.mark.slow
def test_calphy_gpu_capability_real_binary():
    """Parses the installed conda-forge LAMMPS: KOKKOS + pace/kk present, hybrid/scaled/kk absent (22 Jul 2025)."""
    import shutil
    from ftphase.calphy_io import gpu_capability
    exe = shutil.which("lmp_mpi") or shutil.which("lmp")
    if exe is None:
        pytest.skip("no LAMMPS binary on PATH")
    cap = gpu_capability(exe)
    assert isinstance(cap["kokkos"], bool) and cap["version"]
    assert cap["plain_fe_solid"] == (cap["kokkos"] and cap["pace_kk"] and cap["ti_spring"])
    assert cap["all_modes"] == (cap["plain_fe_solid"] and cap["hybrid_scaled_kk"] and cap["ufm"])


def test_read_calphy_results(calphy_example_dir):
    pytest.importorskip("calphy")
    d = os.path.join(calphy_example_dir, "example_03")
    if not os.path.isdir(d):
        pytest.skip("example_03 not present")
    t = read_calphy_results(d, reference_element="Cu", model="Cu_u3.eam")
    assert len(t) > 0
    assert all(p for p in t.phases())  # phase names never empty
    assert set(t.df["quantum"]) == {"classical"}
    assert set(t.df["config_entropy"]) <= {"none", "liquid-ti"}
    assert t.df["T"].min() >= 1100 and t.df["T"].max() <= 1500
