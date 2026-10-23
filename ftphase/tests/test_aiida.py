"""AiiDA plugin layer (ftphase.aiida): CalcJob input generation, parsers and the prepare calcfunction.

Runs on a temporary sqlite profile created by ``aiida.tools.pytest_fixtures`` (no daemon, no
broker, nothing is submitted).  The calphy parser is checked against a real calphy 2.3.0 output
of example 5 (``alli_ace_txdiagram/calphy_liquid``) when that folder is present.
"""

import glob
import json
import os

import numpy as np
import pytest

aiida = pytest.importorskip("aiida")
from aiida import orm  # noqa: E402
from aiida.common.folders import SandboxFolder  # noqa: E402
from aiida.common.links import LinkType  # noqa: E402
from aiida.engine.utils import instantiate_process  # noqa: E402
from aiida.manage import get_manager  # noqa: E402
from aiida.plugins import CalculationFactory, ParserFactory, WorkflowFactory  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LIQ_DIRS = sorted(glob.glob(os.path.join(ROOT, "ftphase/examples/alli_ace_txdiagram/calphy_liquid/lqd_x0.00-ts-*")))


def _s(v):
    """calphy accepts a string or a list for pair_style/pair_coeff/cmdargs: normalise for the asserts."""
    return " ".join(v) if isinstance(v, (list, tuple)) else str(v)


def _prepare(process_class, inputs, folder):
    runner = get_manager().get_runner()
    process = instantiate_process(runner, process_class, **inputs)
    return process.prepare_for_submission(folder), process


@pytest.fixture
def potential(tmp_path):
    p = tmp_path / "AlLi.yace"
    p.write_text("fake ace potential\n")
    return orm.SinglefileData(file=str(p))


@pytest.fixture
def fcc_al():
    from ase.build import bulk

    return orm.StructureData(ase=bulk("Al", "fcc", a=4.05, cubic=True))


def test_entry_points_resolve(aiida_profile):
    assert CalculationFactory("ftphase.qha").__name__ == "QhaCalculation"
    assert CalculationFactory("ftphase.calphy").__name__ == "CalphyCalculation"
    assert ParserFactory("ftphase.qha").__name__ == "QhaParser"
    assert ParserFactory("ftphase.calphy").__name__ == "CalphyParser"
    assert WorkflowFactory("ftphase.txdiagram").__name__ == "TxDiagramWorkChain"


def test_qha_calcjob_inputs(aiida_profile_clean, aiida_code_installed, potential, fcc_al, tmp_path):
    code = aiida_code_installed(filepath_executable="/bin/true", default_calc_job_plugin="ftphase.qha", label="ftphase-qha")
    params = {"pair_style": "pace", "pair_coeff": "* * {potential} Al Li", "atom_types": {"Al": 1, "Li": 2}, "supercell": [2, 2, 2], "mesh": 60.0,
              "scales": [0.97, 0.99, 1.01, 1.03, 1.05], "temperatures": [0.0, 500.0, 1000.0], "eos": "vinet", "imaginary": "drop",
              "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}, "pressure_GPa": 0.0}
    inputs = {"code": code, "structure": fcc_al, "potential": potential, "parameters": orm.Dict(dict=params),
              "metadata": {"options": {"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1, "num_cores_per_mpiproc": 4}, "withmpi": False}}}
    with SandboxFolder() as folder:
        calcinfo, _ = _prepare(CalculationFactory("ftphase.qha"), inputs, folder)
        names = folder.get_content_list()
        assert "input.json" in names and "structure.extxyz" in names
        inp = json.load(open(folder.get_abs_path("input.json")))
    assert inp["potential"] == "AlLi.yace" and inp["pair_style"] == "pace" and "{potential}" in inp["pair_coeff"]
    assert inp["atom_types"] == {"Al": 1, "Li": 2}
    assert inp["parameters"]["supercell"] == [2, 2, 2] and inp["parameters"]["temperatures"] == [0.0, 500.0, 1000.0]
    assert "pair_style" not in inp["parameters"]  # moved to the top level for the runner
    ci = calcinfo.codes_info[0]
    assert ci.cmdline_params == ["input.json"] and ci.stdout_name == "qha.out" and ci.withmpi is False
    assert (potential.uuid, "AlLi.yace", "AlLi.yace") in calcinfo.local_copy_list
    assert set(calcinfo.retrieve_list) >= {"qha_results.json", "qha_arrays.npz", "qha.err"}


def test_calphy_calcjob_inputs_gpu(aiida_profile_clean, aiida_code_installed, potential, fcc_al):
    import yaml

    code = aiida_code_installed(filepath_executable="/bin/true", default_calc_job_plugin="ftphase.calphy", label="calphy")
    params = {"name": "lqd_x0.00", "folder_prefix": "lqd_x0.00", "mode": "ts", "elements": ["Al", "Li"], "masses": [26.9815, 6.94], "pair_style": "pace",
              "pair_coeff": "* * {potential} Al Li", "temperature": [1100.0, 700.0], "pressure": 0.0, "reference_phase": "liquid",
              "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1, "gpu": True, "lammps_executable": "/opt/fake/lmp_gpu"}
    inputs = {"code": code, "structure": fcc_al, "potential": potential, "parameters": orm.Dict(dict=params),
              "metadata": {"options": {"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1}, "withmpi": False,
                                       "custom_scheduler_commands": "#SBATCH --gres=gpu:1"}}}
    with SandboxFolder() as folder:
        calcinfo, _ = _prepare(CalculationFactory("ftphase.calphy"), inputs, folder)
        names = folder.get_content_list()
        assert "input.yaml" in names and "lqd_x0.00.data" in names
        y = yaml.safe_load(open(folder.get_abs_path("input.yaml")))
        data_txt = open(folder.get_abs_path("lqd_x0.00.data")).read()
    assert "2 atom types" in data_txt  # both elements are LAMMPS types even for pure Al
    blk = y["calculations"][0]
    assert blk["mode"] == "ts" and blk["reference_phase"] == "liquid" and blk["temperature"] == [1100.0, 700.0]
    assert blk["lattice"].startswith("__WORKDIR__/") and "__WORKDIR__/AlLi.yace" in _s(blk["pair_coeff"])
    assert _s(blk["pair_style"]) == "pace product"  # KOKKOS GPU needs the product algorithm
    assert blk["queue"]["cores"] == 1 and blk["queue"]["scheduler"] == "local"
    assert "md" in blk and "cmdargs" in blk["md"] and "-k on g 1" in _s(blk["md"]["cmdargs"])
    assert blk["lammps_executable"] == "/opt/fake/lmp_gpu"
    ci = calcinfo.codes_info[0]
    assert ci.cmdline_params == ["-i", "input.yaml", "-k", "0"]
    assert "__WORKDIR__" in calcinfo.prepend_text and "$PWD" in calcinfo.prepend_text  # sed substitution on the node
    assert ("*/report.yaml", ".", 2) in calcinfo.retrieve_list and ("*/temperature_sweep.dat", ".", 2) in calcinfo.retrieve_list


def test_calphy_calcjob_inputs_cpu(aiida_profile_clean, aiida_code_installed, potential, fcc_al):
    import yaml

    code = aiida_code_installed(filepath_executable="/bin/true", default_calc_job_plugin="ftphase.calphy", label="calphy")
    params = {"name": "fcc_fe", "mode": "fe", "elements": ["Al", "Li"], "masses": [26.9815, 6.94], "pair_style": "pace", "pair_coeff": "* * {potential} Al Li",
              "temperature": 800.0, "reference_phase": "solid", "cores": 4}
    inputs = {"code": code, "structure": fcc_al, "potential": potential, "parameters": orm.Dict(dict=params),
              "metadata": {"options": {"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 4}, "withmpi": False}}}
    with SandboxFolder() as folder:
        _prepare(CalculationFactory("ftphase.calphy"), inputs, folder)
        blk = yaml.safe_load(open(folder.get_abs_path("input.yaml")))["calculations"][0]
    assert blk["mode"] == "fe" and blk["temperature"] == 800.0 and blk["queue"]["cores"] == 4
    assert _s(blk["pair_style"]) == "pace" and "cmdargs" not in blk.get("md", {})


def _calcjob_node(aiida_localhost, plugin, tree_dir):
    node = orm.CalcJobNode(computer=aiida_localhost, process_type=f"aiida.calculations:{plugin}")
    node.set_option("resources", {"num_machines": 1, "num_mpiprocs_per_machine": 1})
    node.set_option("max_wallclock_seconds", 1800)
    node.store()
    retrieved = orm.FolderData()
    retrieved.base.repository.put_object_from_tree(tree_dir)
    retrieved.base.links.add_incoming(node, link_type=LinkType.CREATE, link_label="retrieved")
    retrieved.store()
    return node


@pytest.mark.skipif(not LIQ_DIRS, reason="example 5 calphy_liquid output not present")
def test_calphy_parser_real_output(aiida_profile_clean, aiida_localhost, tmp_path):
    import shutil

    src = LIQ_DIRS[0]
    sub = tmp_path / "ret" / os.path.basename(src)
    sub.mkdir(parents=True)
    for fn in ("report.yaml", "temperature_sweep.dat", "metadata.yaml", "calphy.log"):
        if os.path.exists(os.path.join(src, fn)):
            shutil.copy(os.path.join(src, fn), sub / fn)
    (tmp_path / "ret" / "calphy.err").write_text("")
    node = _calcjob_node(aiida_localhost, "ftphase.calphy", str(tmp_path / "ret"))
    results, calcfunction = ParserFactory("ftphase.calphy").parse_from_node(node, store_provenance=False)
    assert calcfunction.exit_status == 0, calcfunction.exit_message
    rep = results["results"].get_dict()
    assert rep["calculation_folder"] == os.path.basename(src)
    assert rep["results"]["unit"] == "eV/atom" and rep["input"]["temperature"] == 1100  # report.yaml has no mode key; the parser uses the folder name
    assert abs(rep["results"]["free_energy"] - (-3.9175)) < 0.01  # fcc-Al-composition ACE liquid at 1100 K (example 5)
    sw = results["sweep"]
    T, G, err = sw.get_array("temperature"), sw.get_array("free_energy"), sw.get_array("error")
    assert T.shape == G.shape == err.shape and len(T) > 100
    assert T[0] == pytest.approx(1100.0) and T[-1] < 710.0  # sweep 1100 -> 700 K
    assert np.all(np.diff(G) > 0)  # G rises with T on a sweep down... stored in sweep order, F(T) decreases with T
    # sanity on the sign: free energy at 1100 K lower than at 700 K
    assert G[0] < G[-1]


def test_calphy_parser_missing_report(aiida_profile_clean, aiida_localhost, tmp_path):
    d = tmp_path / "ret" / "lqd_x0.10-ts-lqd.data-liquid-1100-0"
    d.mkdir(parents=True)
    (d / "calphy.log").write_text("... calphy.errors.MeltedError: The system melted ... \n")
    (tmp_path / "ret" / "calphy.err").write_text("Traceback ...\n")
    node = _calcjob_node(aiida_localhost, "ftphase.calphy", str(tmp_path / "ret"))
    _, calcfunction = ParserFactory("ftphase.calphy").parse_from_node(node, store_provenance=False)
    assert calcfunction.exit_status == 310  # ERROR_PHASE_CHANGED
    d2 = tmp_path / "ret2"
    d2.mkdir()
    (d2 / "calphy.err").write_text("killed\n")
    node = _calcjob_node(aiida_localhost, "ftphase.calphy", str(d2))
    _, calcfunction = ParserFactory("ftphase.calphy").parse_from_node(node, store_provenance=False)
    assert calcfunction.exit_status == 300  # ERROR_NO_REPORT


def test_qha_parser(aiida_profile_clean, aiida_localhost, tmp_path):
    d = tmp_path / "ret"
    d.mkdir()
    T = np.array([0.0, 500.0, 1000.0])
    np.savez(d / "qha_arrays.npz", T=T, G=np.array([-3.7, -3.9, -4.2]), V=np.array([16.5, 16.9, 17.6]), hw_eV=np.array([0.01, 0.02]), weights=np.array([1.0, 2.0]),
             volumes=np.array([60.0, 66.0, 72.0]), e0=np.array([-14.0, -14.8, -14.2]), f_vib=np.zeros((3, 3)))
    (d / "qha_results.json").write_text(json.dumps({"n_atoms": 4, "E0_eV_per_atom": -3.7, "units": {"G": "eV/atom"}}))
    (d / "qha.err").write_text("")
    node = _calcjob_node(aiida_localhost, "ftphase.qha", str(d))
    results, calcfunction = ParserFactory("ftphase.qha").parse_from_node(node, store_provenance=False)
    assert calcfunction.exit_status == 0, calcfunction.exit_message
    assert results["results"].get_dict()["n_atoms"] == 4
    assert np.allclose(results["arrays"].get_array("T"), T) and results["arrays"].get_array("hw_eV").shape == (2,)
    # missing npz -> exit 300 with the stderr tail in the log
    d2 = tmp_path / "ret2"
    d2.mkdir()
    (d2 / "qha.err").write_text("ValueError: need at least 4 volumes\n")
    node = _calcjob_node(aiida_localhost, "ftphase.qha", str(d2))
    _, calcfunction = ParserFactory("ftphase.qha").parse_from_node(node, store_provenance=False)
    assert calcfunction.exit_status == 300


@pytest.mark.slow
@pytest.mark.skipif(not os.path.exists(POT), reason="ACE Al-Li potential (pyiron workshop resources) not present")
def test_prepare_cells_calcfunction(aiida_profile_clean):
    """Stages 01/02 inside the daemon: relax + hull + fcc random series + antisite cells + liquid cells."""
    pytest.importorskip("lammps")
    from ase.build import bulk
    from ase.spacegroup import crystal

    from ftphase.aiida.functions import prepare_cells

    b32 = crystal(["Al", "Li"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=227, cellpar=[6.37, 6.37, 6.37, 90, 90, 90])
    spec = {"elements": ["Al", "Li"], "masses": [26.9815, 6.94], "x_element": "Li", "pair_style": "pace", "pair_coeff": "* * {potential} Al Li",
            "atom_types": {"Al": 1, "Li": 2}, "candidates": {"fcc-Al": 0.0, "bcc-Li": 1.0, "B32-AlLi": 0.5}, "known_ground_states": ["fcc-Al", "bcc-Li", "B32-AlLi"],
            "relax": {"fmax": 1e-2, "cell": True},
            "solids": [{"phase": "fcc", "kind": "solution", "base": "fcc-Al", "repeat": [1, 1, 1], "x": [0.0, 0.25], "n_configs": 1, "series": "random", "seed": 0, "supercell": [2, 2, 2], "mesh": 60.0},
                       {"phase": "B32", "kind": "limited", "base": "B32-AlLi", "antisites": True, "supercell": [1, 1, 1], "mesh": 60.0}],
            "liquids": {"base": "fcc-Al", "repeat": [2, 2, 2], "x": [0.0, 0.25], "seed": 100, "T_sweep": [1100.0, 700.0], "T_override": {"0.25": 800.0}, "n_repeats": 1, "mode": "ts"}}
    cands = {"fcc_Al": orm.StructureData(ase=bulk("Al", "fcc", a=4.05, cubic=True)), "bcc_Li": orm.StructureData(ase=bulk("Li", "bcc", a=3.49, cubic=True)), "B32_AlLi": orm.StructureData(ase=b32)}
    res = prepare_cells(orm.Dict(dict=spec), orm.SinglefileData(file=POT), **cands)
    hull = res["hull"].get_dict()
    assert {r["name"] for r in hull["hull"] if r.get("on_hull", True)} >= {"fcc-Al", "bcc-Li"}
    assert all(r["status"] == "on hull" for r in hull["ground_state_check"])
    sol = res["solid_params"].get_dict()
    assert [m["phase"] for m in sol.values()] == ["fcc", "fcc", "B32", "B32", "B32"]
    assert sorted(round(m["x"], 4) for m in sol.values() if m["phase"] == "B32") == [0.4375, 0.5, 0.5625]  # 16-atom B32: +/- one antisite
    assert sol["s01_fcc"]["x"] == 0.25 and sol["s01_fcc"]["counts"] == {"Al": 3, "Li": 1}
    liq = res["liquid_params"].get_dict()
    assert set(liq) == {"lqd_x0_00", "lqd_x0_25"}
    assert liq["lqd_x0_00"]["temperature"] == [1100.0, 700.0] and liq["lqd_x0_25"]["temperature"] == [1100.0, 800.0]
    assert liq["lqd_x0_25"]["n_atoms"] == 32 and abs(liq["lqd_x0_25"]["x_actual"] - 0.25) < 1e-9
    for k in list(sol) + list(liq):
        assert isinstance(res[("solid_" if k in sol else "liquid_") + k], orm.StructureData)
