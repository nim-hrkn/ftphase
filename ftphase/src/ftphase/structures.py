"""Stage 02A: composition, sublattice and vacancy series; SQS.

* :func:`random_substitution` / :func:`composition_series` realise target
  compositions with integer atom counts on chosen sublattices (seeded), and
  return the *actual* composition and all metadata that workflow section 2
  asks to keep (cell, atom count, seed, counts per sublattice).
* :func:`vacancy_series` removes atoms (vacancies are modelled as missing
  atoms, never as a fictitious element handed to the MLIP) and records the
  site counts needed for eq. (E11)-(E12).
* :func:`sqs_icet` wraps icet's ``generate_sqs`` / ``generate_sqs_by_enumeration``
  (M. Ångqvist et al., Adv. Theory Simul. 2, 1900015 (2019); MPL-2.0):
  sublattices are given per site, vacancies as 'X', and the returned metadata
  contains the cluster-vector deviation from the random target, eq. (B4).
* :func:`sqs_sqsgenerator` wraps sqsgenerator (D. Gehringer, M. Friák,
  D. Holec, Comput. Phys. Commun. 286, 108664 (2023); MIT) when installed.

Both SQS routes return plain ASE Atoms, so the same downstream (phonopy,
calphy, LAMMPS data files) works for random and SQS cells.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from ase import Atoms


@dataclass
class SeriesMember:
    atoms: Atoms
    x_target: float
    x_actual: float
    counts: Dict[str, int]
    seed: Optional[int]
    sublattice_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    site_counts: Dict[str, int] = field(default_factory=dict)   # sites per sublattice incl. vacancies
    note: str = ""

    def site_fractions(self, vacancy: str = "Va") -> Tuple[List[Dict[str, float]], List[float]]:
        """(site_fractions, site_counts) per formula unit = per cell, for eq. (E10)."""
        sf, nc = [], []
        for sub, n_sites in self.site_counts.items():
            occ = dict(self.sublattice_counts.get(sub, {}))
            n_occ = sum(occ.values())
            d = {sp: c / n_sites for sp, c in occ.items()}
            if n_sites > n_occ:
                d[vacancy] = (n_sites - n_occ) / n_sites
            sf.append(d)
            nc.append(float(n_sites))
        return sf, nc


def _fraction(atoms: Atoms, element: str) -> float:
    syms = atoms.get_chemical_symbols()
    return syms.count(element) / len(syms)


def random_substitution(atoms: Atoms, indices: Sequence[int], new_species: str, n_new: int, seed: Optional[int] = None) -> Atoms:
    """Replace ``n_new`` randomly chosen atoms among ``indices`` by ``new_species``."""
    rng = np.random.default_rng(seed)
    idx = np.asarray(indices, dtype=int)
    if n_new > idx.size:
        raise ValueError(f"cannot place {n_new} atoms on {idx.size} sites")
    pick = rng.choice(idx, size=n_new, replace=False)
    out = atoms.copy()
    syms = out.get_chemical_symbols()
    for i in pick:
        syms[int(i)] = new_species
    out.set_chemical_symbols(syms)
    return out


def composition_series(
    base: Atoms,
    element_B: str,
    x_targets: Sequence[float],
    sublattice: Optional[Sequence[int]] = None,
    sublattice_name: str = "A",
    other_sublattices: Optional[Dict[str, Sequence[int]]] = None,
    seed: int = 0,
    n_configs: int = 1,
) -> List[SeriesMember]:
    """Random substitutional series on one sublattice.

    ``base`` is the supercell of the host (all sites of ``sublattice`` hold the
    host species).  For each target x (fraction of element_B among *all*
    atoms) the integer number of B atoms that comes closest is placed on
    ``sublattice`` (all sites by default).  ``n_configs`` independent
    configurations per composition use seeds seed, seed+1, ...
    """
    N = len(base)
    sub = np.arange(N) if sublattice is None else np.asarray(sublattice, dtype=int)
    others = other_sublattices or {}
    out = []
    k = 0
    for xt in x_targets:
        nB = int(round(xt * N))
        nB_existing = sum(1 for i in range(N) if base[i].symbol == element_B and i not in set(sub.tolist()))
        n_on_sub = nB - nB_existing
        if n_on_sub < 0 or n_on_sub > sub.size:
            raise ValueError(f"x={xt}: need {n_on_sub} {element_B} atoms on a sublattice of {sub.size} sites")
        for c in range(n_configs):
            s = seed + k
            k += 1
            a = random_substitution(base, sub, element_B, n_on_sub, seed=s)
            syms = a.get_chemical_symbols()
            counts = {e: syms.count(e) for e in sorted(set(syms))}
            subc = {sublattice_name: {e: sum(1 for i in sub if syms[i] == e) for e in set(syms[i] for i in sub)}}
            sitec = {sublattice_name: int(sub.size)}
            for name, ids in others.items():
                ids = np.asarray(ids, dtype=int)
                subc[name] = {e: sum(1 for i in ids if syms[i] == e) for e in set(syms[i] for i in ids)}
                sitec[name] = int(ids.size)
            out.append(SeriesMember(a, float(xt), _fraction(a, element_B), counts, s, subc, sitec, "random substitution"))
    return out


def vacancy_series(base: Atoms, sublattice: Sequence[int], n_vacancies: Sequence[int], sublattice_name: str = "A", other_sublattices: Optional[Dict[str, Sequence[int]]] = None, seed: int = 0, element_B: Optional[str] = None) -> List[SeriesMember]:
    """Remove n atoms from ``sublattice`` (vacancies as missing atoms).

    The returned SeriesMember keeps the *original* site counts so that
    site fractions include 'Va' and eq. (E11)-(E12) can be evaluated.
    """
    sub = np.asarray(sublattice, dtype=int)
    others = other_sublattices or {}
    out = []
    for k, nv in enumerate(n_vacancies):
        rng = np.random.default_rng(seed + k)
        rem = set(rng.choice(sub, size=int(nv), replace=False).tolist()) if nv > 0 else set()
        keep = [i for i in range(len(base)) if i not in rem]
        a = base[keep]
        syms_full = base.get_chemical_symbols()
        subc = {sublattice_name: {e: sum(1 for i in sub if i not in rem and syms_full[i] == e) for e in set(syms_full[i] for i in sub)}}
        sitec = {sublattice_name: int(sub.size)}
        for name, ids in others.items():
            ids = np.asarray(ids, dtype=int)
            subc[name] = {e: sum(1 for i in ids if syms_full[i] == e) for e in set(syms_full[i] for i in ids)}
            sitec[name] = int(ids.size)
        syms = a.get_chemical_symbols()
        counts = {e: syms.count(e) for e in sorted(set(syms))}
        xB = _fraction(a, element_B) if element_B else float("nan")
        out.append(SeriesMember(a, xB, xB, counts, seed + k, subc, sitec, f"{nv} vacancies on {sublattice_name}"))
    return out


def sqs_icet(
    primitive: Atoms,
    chemical_symbols: Sequence[Sequence[str]],
    cutoffs: Sequence[float],
    target_concentrations: Dict,
    max_size: int,
    method: str = "enumeration",
    n_steps: Optional[int] = None,
    include_smaller_cells: bool = True,
    seed: Optional[int] = None,
    supercells: Optional[Sequence[Atoms]] = None,
) -> Tuple[Atoms, Dict]:
    """Special quasirandom structure with icet.

    chemical_symbols : per site of ``primitive``, the allowed species, e.g.
        [['Al', 'Li']] for one sublattice or [['Al','Li'], ['Li','X']] for
        two (X = vacancy).
    target_concentrations : {'Al': 0.9, 'Li': 0.1} or, with several
        sublattices, {'A': {...}, 'B': {...}} using icet's sublattice letters.
    method : 'enumeration' (exhaustive up to max_size; recommended for small
        cells), 'anneal' (Monte Carlo over all cell shapes up to max_size,
        ``n_steps``) or 'supercells' (Monte Carlo in the given ``supercells``
        only, icet generate_sqs_from_supercells; the way to get e.g. one
        64-atom cell of fixed shape).
    Returns (atoms, metadata) with metadata['cluster_vector_deviation'] =
    |Gamma_SQS - Gamma_random| summed over orbits, eq. (B4).
    """
    from icet import ClusterSpace  # type: ignore
    from icet.tools.structure_generation import generate_sqs, generate_sqs_by_enumeration, generate_sqs_from_supercells  # type: ignore
    from icet.tools.structure_generation import _get_sqs_cluster_vector  # type: ignore

    cs = ClusterSpace(primitive, cutoffs=list(cutoffs), chemical_symbols=[list(s) for s in chemical_symbols])
    if method == "enumeration":
        sqs = generate_sqs_by_enumeration(cs, max_size=max_size, target_concentrations=target_concentrations, include_smaller_cells=include_smaller_cells)
    elif method == "anneal":
        kw = {}
        if n_steps is not None:
            kw["n_steps"] = n_steps
        if seed is not None:
            np.random.seed(seed)
        sqs = generate_sqs(cs, max_size=max_size, target_concentrations=target_concentrations, include_smaller_cells=include_smaller_cells, **kw)
    elif method == "supercells":
        if not supercells:
            raise ValueError("method='supercells' needs supercells=[Atoms, ...]")
        kw = {}
        if n_steps is not None:
            kw["n_steps"] = n_steps
        if seed is not None:
            np.random.seed(seed)
        sqs = generate_sqs_from_supercells(cs, supercells=list(supercells), target_concentrations=target_concentrations, **kw)
    else:
        raise ValueError("method must be 'enumeration', 'anneal' or 'supercells'")
    cv = cs.get_cluster_vector(sqs)
    try:
        target = _get_sqs_cluster_vector(cs, target_concentrations)
        dev = float(np.sum(np.abs(np.asarray(cv) - np.asarray(target))))
    except Exception:  # pragma: no cover - private API may change
        target, dev = None, float("nan")
    meta = {"generator": "icet", "method": method, "cutoffs": list(cutoffs), "max_size": max_size, "n_atoms": len(sqs), "target_concentrations": target_concentrations, "cluster_vector": np.asarray(cv).tolist(), "target_cluster_vector": None if target is None else np.asarray(target).tolist(), "cluster_vector_deviation": dev, "seed": seed, "cell": np.asarray(sqs.get_cell()).tolist(), "orbit_count": len(cs)}
    return sqs, meta


def sqs_sqsgenerator(atoms: Atoms, composition: Dict[str, int], shell_weights: Optional[Dict[int, float]] = None, iterations: int = 100000,
                     seed: Optional[int] = None, pair_weights=None, shell_radii=None) -> Tuple[Atoms, Dict]:
    """SQS with sqsgenerator 0.5 (``parse_config`` + ``optimize``) on the given supercell.

    Objective: weighted Warren-Cowley short-range-order parameters of the cross pairs over the
    first shells (defaults of sqsgenerator: 5 shells with weights 1, 1/2, ..., 1/5; same-species
    pairs have weight 0).  ``composition`` gives atom counts, e.g. {'Al': 28, 'Li': 4}.
    Returns (atoms, metadata) with the objective, the SRO parameters per shell and species pair,
    the shell radii/weights used and the number of degenerate best structures.  The C++ core is
    fast (10^5-10^6 iterations in well under a second for 32-64 atoms); seeds are not exposed by
    the 0.5 Python API, so ``seed`` is only recorded.
    """
    import sqsgenerator as sg  # type: ignore

    cfg = {"structure": {"lattice": atoms.get_cell()[:].tolist(), "coords": atoms.get_scaled_positions().tolist(), "species": atoms.get_chemical_symbols()},
           "composition": {k: int(v) for k, v in composition.items()}, "iterations": int(iterations)}
    if shell_weights:
        cfg["shell_weights"] = {int(k): float(v) for k, v in shell_weights.items()}
    if pair_weights is not None:
        cfg["pair_weights"] = pair_weights
    if shell_radii is not None:
        cfg["shell_radii"] = shell_radii
    conf = sg.parse_config(cfg)
    res = sg.optimize(conf)
    best = res.best()

    def _v(x):
        return x() if callable(x) else x

    out = sg.to_ase(_v(best.structure))
    sro = np.asarray(_v(best.sro), dtype=float)
    species = list(_v(best.species)) if hasattr(best, "species") else None
    meta = {"generator": f"sqsgenerator {getattr(sg, '__version__', '')}", "objective": float(_v(best.objective)), "iterations": int(iterations), "seed": seed,
            "sro": sro.tolist(), "species_order": [str(v) for v in species] if species else None,
            "shell_radii": [list(map(float, r)) for r in _v(conf.shell_radii)] if hasattr(conf, "shell_radii") else None,
            "shell_weights": [{int(k): float(v) for k, v in w.items()} for w in _v(conf.shell_weights)] if hasattr(conf, "shell_weights") else None,
            "n_best_structures": int(_v(res.num_results)) if hasattr(res, "num_results") else None, "n_atoms": len(out), "composition": dict(composition)}
    return out, meta


def write_lammps_data(atoms: Atoms, path, species_order: Sequence[str]):
    """LAMMPS data file with a fixed species order (calphy needs the same
    order as the input element list)."""
    from ase.io import write

    write(str(path), atoms, format="lammps-data", specorder=list(species_order), masses=True, atom_style="atomic")
    return str(path)
