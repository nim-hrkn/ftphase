"""Stage 03B (and 03A auxiliary route): calphy inputs and results.

calphy (S. Menon, Y. Lysogorskiy, J. Rogal, R. Drautz, Phys. Rev. Mater. 5,
103801 (2021); https://github.com/ICAMS/calphy, Academic Software Licence)
performs the non-equilibrium thermodynamic integration (Einstein crystal for
solids, Uhlenbeck-Ford model for liquids, eq. (F1)-(F2)) and reversible
scaling in temperature.  This module

* writes calphy 2.x input files for a composition series of structures
  (one ``calculations:`` block per structure, everything inside the block,
  Slurm ``queue`` block as used in ``calphy-examples/``),
* reads finished job folders with ``calphy.postprocessing.gather_results``
  and converts them to the :class:`ftphase.records.FreeEnergyTable` schema
  with the flags that matter: calphy solids are *classical* and carry *no*
  configurational entropy (``config_entropy='none'``); calphy liquids are
  classical and already contain the mixing statistics of the liquid
  (``config_entropy='liquid-ti'``), so no ideal term may be added later,
* optionally prepares the blocks for a GPU run through LAMMPS KOKKOS
  (``gpu=True``): calphy 2.3 passes ``md.cmdargs`` to the ``lmp`` binary and
  extra ``#SBATCH`` lines through ``queue.options``.  ML-PACE on the GPU
  (``pace/kk``) accepts only the ``product`` evaluation algorithm, and every
  calphy mode except the solid Frenkel-Ladd ``fe`` step installs
  ``pair_style hybrid/scaled``, whose KOKKOS variant exists in LAMMPS >= 30 Sep
  2026 only.  :func:`gpu_capability` reads ``lmp -h`` of the chosen binary and
  :func:`calculation_block` refuses GPU blocks the binary cannot run.
"""

from __future__ import annotations

import os
import re
import subprocess
from functools import lru_cache
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd
import yaml

from .records import FreeEnergyTable

DEFAULT_SLURM_QUEUE = {
    "scheduler": "slurm",
    "queuename": "debug",
    "cores": 4,
    "memory": "8GB",
    "walltime": "48:00:00",
    "commands": [],
}

#: LAMMPS command-line arguments for one GPU through KOKKOS (LAMMPS manual,
#: "Speed kokkos"): one MPI rank per GPU, suffix kk for every style that has a
#: KOKKOS variant, full neighbour lists are chosen by pace/kk itself.
GPU_CMDARGS = "-k on g {n_gpus} -sf kk -pk kokkos newton on neigh half"

#: calphy modes/reference phases that run only pair_style <style> (+ fix
#: ti/spring).  Everything else wraps the potential in hybrid/scaled.
_PLAIN_PAIR_RUNS = {("fe", "solid")}


def gpu_pair_style(pair_style: str) -> str:
    """Return ``pair_style`` as it must be written for a KOKKOS/GPU run.

    ``pace`` -> ``pace product``: ``pair_style pace/kk`` on a GPU aborts with
    "Must use 'product' algorithm" for the default recursive evaluator
    (LAMMPS src/KOKKOS/pair_pace_kokkos.cpp).  Other styles are returned
    unchanged; a style without a /kk variant simply runs on the host.
    """
    tok = pair_style.split()
    if tok and tok[0] == "pace" and not ({"product", "recursive"} & set(tok[1:])):
        return " ".join([tok[0], "product", *tok[1:]])
    return pair_style


@lru_cache(maxsize=8)
def lammps_styles(executable: str) -> Dict[str, List[str]]:
    """Parse ``<executable> -h`` into {'pair': [...], 'fix': [...], 'packages': [...], 'version': str}."""
    out = subprocess.run([executable, "-h"], capture_output=True, text=True, timeout=120).stdout
    res: Dict[str, List[str]] = {"pair": [], "fix": [], "compute": [], "packages": [], "version": []}
    m = re.search(r"Massively Parallel Simulator - (.*)", out)
    if m:
        res["version"] = [m.group(1).strip()]
    sec = None
    for line in out.splitlines():
        head = line.strip().rstrip(":")
        if head.startswith("* Pair styles"):
            sec = "pair"; continue
        if head.startswith("* Fix styles"):
            sec = "fix"; continue
        if head.startswith("* Compute styles"):
            sec = "compute"; continue
        if head.startswith("Installed packages"):
            sec = "packages"; continue
        if head.startswith("*") or head.startswith("List of"):
            sec = None; continue
        if sec and line.strip():
            res[sec].extend(line.split())
    return res


def gpu_capability(executable: str) -> Dict[str, object]:
    """What the LAMMPS binary can do on a GPU for calphy + ACE.

    Keys: ``kokkos`` (package present), ``pace_kk``, ``grace_fs_kk``, ``grace_1l_kk``,
    ``grace_2l_kk``, ``kk_pair_styles`` (every pair style with a ``/kk`` variant),
    ``hybrid_scaled_kk``, ``ufm``, ``ti_spring``, ``version``; ``plain_fe_solid`` /
    ``all_modes`` summarise which calphy runs may use ``gpu=True`` with ACE.
    """
    st = lammps_styles(str(executable))
    pair, fix = set(st["pair"]), set(st["fix"])
    cap = {
        "executable": str(executable),
        "version": st["version"][0] if st["version"] else "",
        "kokkos": "KOKKOS" in set(st["packages"]),
        "pace_kk": "pace/kk" in pair,
        "grace_fs_kk": "grace/fs/kk" in pair,
        "grace_1l_kk": "grace/1l/kk" in pair,
        "grace_2l_kk": "grace/2l/kk" in pair,
        "kk_pair_styles": sorted(x[:-3] for x in pair if x.endswith("/kk")),
        "hybrid_scaled_kk": "hybrid/scaled/kk" in pair,
        "ufm": "ufm" in pair,
        "ti_spring": "ti/spring" in fix,
    }
    cap["plain_fe_solid"] = bool(cap["kokkos"] and cap["pace_kk"] and cap["ti_spring"])
    cap["all_modes"] = bool(cap["plain_fe_solid"] and cap["hybrid_scaled_kk"] and cap["ufm"])
    return cap


def needs_hybrid_scaled(mode: str, reference_phase: str = "solid") -> bool:
    """True when calphy wraps the potential in ``pair_style hybrid/scaled`` for this run."""
    return (mode, reference_phase) not in _PLAIN_PAIR_RUNS


def calculation_block(
    name: str,
    mode: str,
    elements: Sequence[str],
    masses: Sequence[float],
    lattice_file: str,
    pair_style: str,
    pair_coeff: str,
    temperature,
    pressure: float = 0.0,
    reference_phase: str = "solid",
    n_equilibration_steps: int = 10000,
    n_switching_steps=25000,
    n_iterations: int = 1,
    queue: Optional[Dict] = None,
    folder_prefix: Optional[str] = None,
    extra: Optional[Dict] = None,
    phase_checks: bool = True,
    solid_fraction: float = 0.7,
    liquid_fraction: float = 0.05,
    gpu: bool = False,
    n_gpus: int = 1,
    lammps_executable: Optional[str] = None,
    gpu_cmdargs: str = GPU_CMDARGS,
    check_executable: bool = True,
) -> Dict:
    """One calphy ``calculations`` entry (calphy >= 2.2 keys).

    ``gpu=True`` turns the block into a LAMMPS KOKKOS run: ``md.cmdargs`` =
    ``gpu_cmdargs`` (one GPU by default), ``queue.cores`` = ``n_gpus`` (one MPI
    rank per GPU), ``#SBATCH --gres=gpu:n`` through ``queue.options``, and the
    pair style rewritten by :func:`gpu_pair_style` (``pace`` -> ``pace
    product``).  ``lammps_executable`` is written into the block (calphy key of
    the same name; default is ``lmp`` on PATH).  When it is given and
    ``check_executable`` is true, :func:`gpu_capability` must confirm that the
    binary provides ``pace/kk`` and, for every run other than the solid
    Frenkel-Ladd ``fe`` step, ``hybrid/scaled/kk``; otherwise ValueError.
    A GPU run that silently falls back to a host style would still give the
    right numbers, but a binary without ``hybrid/scaled/kk`` aborts at run
    time ("Must use pair_style hybrid/scaled/kk with Kokkos"), so the check
    is done when the input is written.

    ``phase_checks``: calphy 2.3 ships with melt/solidification detection
    switched OFF (tolerance.solid_fraction=0, liquid_fraction=1); pyiron's
    Calphy job switches it on.  Here it is ON by default (a solid that melts
    or a liquid that freezes during equilibration aborts the run instead of
    reporting a free energy of the wrong phase).  Set ``phase_checks=False``
    deliberately for metastable end points and record it.
    """
    blk = {
        "mode": mode,
        "element": list(elements),
        "mass": [float(m) for m in masses],
        "lattice": str(lattice_file),
        "reference_phase": reference_phase,
        "temperature": temperature if isinstance(temperature, (int, float)) else [float(t) for t in temperature],
        "pressure": pressure,
        "pair_style": pair_style,
        "pair_coeff": pair_coeff,
        "n_equilibration_steps": int(n_equilibration_steps),
        "n_switching_steps": int(n_switching_steps) if np.isscalar(n_switching_steps) else [int(v) for v in n_switching_steps],  # calphy: int or [fe, ts sweep]
        "n_iterations": int(n_iterations),
    }
    if phase_checks:
        blk["tolerance"] = {"solid_fraction": float(solid_fraction), "liquid_fraction": float(liquid_fraction)}
    else:
        blk["tolerance"] = {"solid_fraction": 0.0, "liquid_fraction": 1.0}
    if folder_prefix:
        blk["folder_prefix"] = folder_prefix
    q = dict(queue) if queue else None
    if gpu:
        if n_gpus < 1:
            raise ValueError("n_gpus must be >= 1 for gpu=True")
        blk["pair_style"] = gpu_pair_style(pair_style)
        blk["md"] = {"cmdargs": gpu_cmdargs.format(n_gpus=int(n_gpus))}
        if q is None:
            q = {"scheduler": "local", "cores": int(n_gpus)}
        q["cores"] = int(n_gpus)
        if q.get("scheduler") == "slurm":
            opts = dict(q.get("options") or {})
            opts.setdefault("gres", f"gpu:{int(n_gpus)}")
            q["options"] = opts
        if lammps_executable and check_executable:
            cap = gpu_capability(lammps_executable)
            base = pair_style.split()[0]
            uses_pace = base in ("pace", "pace/extrapolation")
            problems = []
            if not cap["kokkos"]:
                problems.append("no KOKKOS package")
            if uses_pace and not cap["pace_kk"]:
                problems.append("no pair_style pace/kk")
            elif not uses_pace and base not in cap["kk_pair_styles"] and base != "hybrid/scaled":
                problems.append(f"no pair_style {base}/kk (GRACE: build env/lammps-gpu-grace, 22Jul2025_update6 + grace.patch)")
            if needs_hybrid_scaled(mode, reference_phase) and not cap["hybrid_scaled_kk"]:
                problems.append(f"no pair_style hybrid/scaled/kk (needed by mode {mode!r}, reference_phase {reference_phase!r}; LAMMPS >= 30 Sep 2026)")
            if problems:
                raise ValueError(f"{lammps_executable} ({cap['version']}) cannot run block {name!r} on the GPU: " + "; ".join(problems))
    if lammps_executable:
        blk["lammps_executable"] = str(lammps_executable)
    if q:
        blk["queue"] = q
    if extra:
        blk.update(extra)
    return blk


def write_series_input(path, blocks: Sequence[Dict]):
    with open(path, "w") as f:
        yaml.safe_dump({"calculations": list(blocks)}, f, sort_keys=False)
    return str(path)


CONDA_SH_CANDIDATES = ("/home/kino/miniforge3/etc/profile.d/conda.sh", "/home/kino/miniconda3/etc/profile.d/conda.sh",
                       os.path.expanduser("~/miniforge3/etc/profile.d/conda.sh"), os.path.expanduser("~/miniconda3/etc/profile.d/conda.sh"),
                       os.path.expanduser("~/mambaforge/etc/profile.d/conda.sh"), "/opt/conda/etc/profile.d/conda.sh")


def conda_sh(explicit: Optional[str] = None) -> str:
    """Path of conda.sh for the ``queue.commands`` activation line: ``explicit``, then $CONDA_SH,
    then the first existing candidate (miniforge3 on mygarden5, miniconda3 on mygardenx1)."""
    for c in ([explicit] if explicit else []) + [os.environ.get("CONDA_SH")] + list(CONDA_SH_CANDIDATES):
        if c and os.path.exists(c):
            return c
    return CONDA_SH_CANDIDATES[0]


def slurm_queue(env_prefix: str, cores: int = 4, memory: str = "8GB", queuename: str = "debug", conda_sh_path: Optional[str] = None) -> Dict:
    """calphy ``queue`` block for a Slurm host.  The activation line uses :func:`conda_sh`, so the
    same input generator works on mygarden5 (miniforge3) and mygardenx1 (miniconda3)."""
    q = dict(DEFAULT_SLURM_QUEUE)
    q.update({"cores": cores, "memory": memory, "queuename": queuename, "commands": [f"source {conda_sh(conda_sh_path)} && conda activate {env_prefix}"]})
    return q


def read_calphy_results(folder, reference_element: str, phase_names: Optional[Dict[str, str]] = None, model: str = "", source_prefix: str = "") -> FreeEnergyTable:
    """Collect calphy job folders under ``folder`` into a FreeEnergyTable.

    Uses ``calphy.postprocessing.gather_results(folder, reduce_composition=True,
    extract_phase_prefix=True)``.  ``phase_names`` maps calphy's phase prefix
    (from the folder name, e.g. 'fcc', 'lqd') to the names used downstream.
    Reversible-scaling (ts) jobs contribute one row per temperature point;
    fe jobs one row.
    """
    from calphy.postprocessing import gather_results  # type: ignore

    df = gather_results(str(folder), reduce_composition=True, extract_phase_prefix=True)
    if "status" in df:
        df = df[df["status"].astype(str) == "True"]
    rows = []
    for r in df.itertuples():
        comp = getattr(r, "composition", None)
        if isinstance(comp, dict):
            x = float(comp.get(reference_element, 0.0))
        else:
            try:
                x = float(comp)
            except (TypeError, ValueError):
                x = np.nan
        ph = str(getattr(r, "phase_name", "") or "")
        if not ph:
            # calphy's prefix extraction does not recognise our 'folder_prefix-mode-...' names;
            # fall back to the text before the first '-' of the calculation folder
            ph = str(r.calculation).split("-")[0]
        ph = phase_names.get(ph, ph) if phase_names else ph
        liquid = str(getattr(r, "reference_phase", "")) == "liquid"
        T = np.atleast_1d(np.asarray(r.temperature, dtype=float))
        G = np.atleast_1d(np.asarray(r.free_energy, dtype=float))
        err = np.atleast_1d(np.asarray(getattr(r, "free_energy_error", 0.0), dtype=float))
        if err.size != G.size:
            err = np.full_like(G, float(err.ravel()[0]) if err.size else 0.0)
        for t, g, e in zip(T, G, err):
            rows.append({
                "phase": ph, "kind": "solution", "x": x, "T": float(t), "P_GPa": float(r.pressure) / 10000.0 if hasattr(r, "pressure") else 0.0,
                "G": float(g), "G_err": float(e), "V": np.nan, "model": model,
                "reference_state": "absolute potential energy (calphy)",
                "method": f"calphy {r.calculation_mode}, reference {'UFM' if liquid else 'Einstein crystal'}",
                "config_entropy": "liquid-ti" if liquid else "none", "quantum": "classical", "n_atoms": 0,
                "source": source_prefix + str(r.calculation),
            })
    return FreeEnergyTable.from_rows(rows, {"reader": "ftphase.calphy_io.read_calphy_results", "folder": str(folder)})


def read_report(report_yaml) -> Dict:
    """Parse a single calphy report.yaml (fe mode)."""
    with open(report_yaml) as f:
        return yaml.safe_load(f)
