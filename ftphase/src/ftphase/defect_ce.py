"""Configurational free energy of the defects of ONE compound: cluster expansion on the compound's own lattice + Monte Carlo.

Option of the uniform compound procedure (:mod:`ftphase.compounds`) for the cases where the point-defect model (random,
non-interacting or polynomial interaction) is not enough because the anti-sites attract or avoid each other.  Only anti-sites:
both sublattices are open to both species; vacancies are not in the lattice model.

The whole chain in one call: :func:`run` (you supply ``compute(atoms)`` = the free energies of one cell with your calculator).
The steps it performs (each is a function here; a file-based driver is ``examples/uniform_compounds/defect_ce_mc.py``)::

    plan      = training_plan(supercell, A, B)                 # which cells to compute: every inequivalent site and pair
    ...compute G_cell(T) of every cell with your calculator (QHA), relax it...
    check     = structure_check(ideal, relaxed, perfect_cell)  # did the cell stay in the parent structure?
    fit       = fit_expansion(cells, values, (A, B))           # cut-offs / method chosen by validation, rank checked
    new_cells = harvest(fit.expansion(T), supercell, ...)      # where the Monte Carlo runs to: compute, add, refit, repeat
    scan      = sgc_scan(fit.expansion(T), big_supercell, ...) # two branches from the stoichiometric plateau
    x, dG     = branch_free_energy(scan, x0, x_range)          # G(x) - G(x0) = integral of (mu_B - mu_A) dx

Rules that the data taught (ACE Al-Li, 2026-11-19..23):

* A cell that leaves the parent structure on relaxation is another phase, not this compound with defects (B32 with >= 6 Al
  anti-sites per 128 sites shears into a tetragonal cell): :func:`structure_check`.
* The training set must contain, for every kind of pair inside the cut-off, a cell with BOTH sites exchanged; otherwise the
  pair term is a linear combination of the point terms and the fit is not determined (Al4Li9, 7 inequivalent sites):
  :func:`training_plan` samples every inequivalent site, :func:`fit_expansion` refuses rank-deficient candidates.
* A small validation error inside the trained configurations says nothing about the states the Monte Carlo visits: harvest
  them, compute them and refit until nothing new is found (:func:`harvest`).
* An expansion whose validation error exceeds ~1 meV/atom, or a Monte Carlo branch that leaves the compound at once, is not
  used; the point-defect line is kept (:func:`branch_free_energy` returns an empty curve in the second case).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

__all__ = ["training_plan", "structure_check", "ExpansionFit", "fit_expansion", "plateau", "sgc_scan", "harvest", "branch_free_energy", "DefectCEResult", "run"]

DEFAULT_CUTOFFS = tuple([[c2] for c2 in (4.0, 5.0, 6.5, 7.5)] + [[c2, c3] for c2 in (5.0, 6.5, 7.5) for c3 in (4.0, 5.0) if c3 <= c2])


def _equivalent_atoms(atoms, symprec=1e-3):
    import spglib
    ds = spglib.get_symmetry_dataset((atoms.cell[:], atoms.get_scaled_positions(), atoms.numbers), symprec=symprec)
    return np.asarray(ds.equivalent_atoms if hasattr(ds, "equivalent_atoms") else ds["equivalent_atoms"])


def training_plan(supercell, A, B, rpair=4.0, rshell=7.5, n_random=(3, 4, 6, 8, 12, 16), n_conf=3, mixed=((2, 2), (4, 4), (4, 2), (2, 4), (8, 2), (2, 8)),
                  blocks=None, seed=7, symprec=1e-3):
    """Training cells on ``supercell`` (the perfect compound, elements ``A`` and ``B``), as ``[(tag, sites_A_to_B, sites_B_to_A)]``.

    perfect; one anti-site on every symmetry-inequivalent site; anti-site pairs by distance out to ``rshell`` around the first
    site of each element (same kind and mixed) and every kind of pair (site class, site class, distance) within ``rpair`` around
    every inequivalent site; regular arrays (one anti-site per block of ``blocks`` = repeats of the original cell, if given);
    ``n_conf`` random sets of ``n_random`` anti-sites on either side; mixed random sets.  Tags are stable, so a plan can be
    extended and recomputed incrementally."""
    sym = np.array(supercell.get_chemical_symbols()); iA = np.where(sym == A)[0]; iB = np.where(sym == B)[0]; rng = np.random.default_rng(seed)
    D = supercell.get_all_distances(mic=True); a0, b0 = int(iA[0]), int(iB[0])
    plan = [("perfect", [], []), ("single_B_on_A", [a0], []), ("single_A_on_B", [], [b0])]

    def shells(i0, pool):
        d = np.round(D[i0, pool], 2)
        return [(float(r), int(pool[np.where(d == r)[0][0]])) for r in sorted(set(d[(d > 0.1) & (d < rshell)]))]

    plan += [(f"pair_BA_BA_{r:.2f}", [a0, j], []) for r, j in shells(a0, iA)]
    plan += [(f"pair_AB_AB_{r:.2f}", [], [b0, j]) for r, j in shells(b0, iB)]
    plan += [(f"pair_BA_AB_{r:.2f}", [a0], [j]) for r, j in shells(a0, iB)]
    cls = _equivalent_atoms(supercell, symprec); seen = set(); kind = lambda i: "BA" if sym[i] == A else "AB"
    for i0 in sorted(set(int(c) for c in cls)):
        if i0 not in (a0, b0):
            plan.append((f"single_{kind(i0)}_s{i0}", [i0] if sym[i0] == A else [], [i0] if sym[i0] == B else []))
        d = np.round(D[i0], 2)
        for j in (int(j) for j in np.argsort(d)):
            key = (min(cls[i0], cls[j]), max(cls[i0], cls[j]), float(d[j]))
            if j == i0 or d[j] > rpair or key in seen:
                continue
            seen.add(key); la = [k for k in (i0, j) if sym[k] == A]; lb = [k for k in (i0, j) if sym[k] == B]
            if not any(set(la) == set(q[1]) and set(lb) == set(q[2]) for q in plan):
                plan.append((f"pairs_{kind(i0)}_{kind(j)}_s{i0}_{j}_{d[j]:.2f}", la, lb))
    if blocks is not None:
        frac = supercell.get_scaled_positions()
        for tag, pool in (("B_on_A", iA), ("A_on_B", iB)):
            first = {}
            for i, b in zip(pool, map(tuple, np.floor(frac[pool] * np.array(blocks) + 1e-6).astype(int))):
                first.setdefault(b, int(i))
            s_ = sorted(first.values()); plan.append((f"regular_{tag}_{len(s_)}", s_ if tag == "B_on_A" else [], s_ if tag == "A_on_B" else []))
    for k in n_random:
        for c in range(n_conf):
            if k <= len(iA):
                plan.append((f"rand_B_on_A_k{k}_c{c}", [int(v) for v in rng.choice(iA, k, replace=False)], []))
            if k <= len(iB):
                plan.append((f"rand_A_on_B_k{k}_c{c}", [], [int(v) for v in rng.choice(iB, k, replace=False)]))
    for ka, kb in mixed:
        for c in range(2):
            if ka <= len(iA) and kb <= len(iB):
                plan.append((f"mixed_{ka}_{kb}_c{c}", [int(v) for v in rng.choice(iA, ka, replace=False)], [int(v) for v in rng.choice(iB, kb, replace=False)]))
    return plan


def structure_check(ideal, relaxed, perfect_cell, strain_max=0.02):
    """Did a relaxed training cell stay in the parent structure?

    ``ideal`` = the cell on the ideal lattice sites, ``relaxed`` = the same cell after relaxing positions and cell,
    ``perfect_cell`` = cell matrix of the relaxed perfect compound in the same supercell.  Returns the largest deviatoric
    (shape) strain of the cell, the rms displacement from the ideal sites (in the relaxed cell) and ``left_parent``
    (shape strain above ``strain_max``).  A volume change alone is not a change of structure."""
    F = np.linalg.solve(np.asarray(perfect_cell), relaxed.cell[:]).T; U = 0.5 * (F.T @ F - np.eye(3))
    ev = np.linalg.eigvalsh(U - np.trace(U) / 3 * np.eye(3)); d = relaxed.get_scaled_positions() - ideal.get_scaled_positions(); d -= np.round(d)
    disp = np.linalg.norm(d @ relaxed.cell[:], axis=1); s = float(np.abs(ev).max())
    return {"strain_max": s, "disp_rms_A": float(np.sqrt(np.mean(disp ** 2))), "left_parent": bool(s > strain_max)}


@dataclass
class ExpansionFit:
    """Result of :func:`fit_expansion`.  ``parameters[k]`` belongs to column ``k`` of ``values``; ``rmse_cv`` (eV/site) likewise."""
    cluster_space: object
    parameters: np.ndarray
    cutoffs: list
    method: str
    rmse_cv: np.ndarray
    rmse_train: np.ndarray
    n_single_cell_parameters: int | None
    x_range: tuple
    candidates: list = field(default_factory=list)

    def expansion(self, k=0):
        from icet import ClusterExpansion
        return ClusterExpansion(self.cluster_space, np.atleast_2d(self.parameters)[k])

    def usable(self, k=0, limit=1e-3):
        """Validation error of column ``k`` below ``limit`` (eV/site; default 1 meV)?"""
        return bool(np.atleast_1d(self.rmse_cv)[k] < limit)


def _loo(A, y):
    """Leave-one-out rmse of an ordinary least-squares fit from the hat matrix, over the rows with leverage < 0.99, and the
    number of rows with leverage ~ 1 (each of those alone fixes a parameter and cannot be validated)."""
    H = A @ np.linalg.pinv(A); lev = np.diag(H); r = y - H @ y; ok = lev < 0.99
    return (float(np.sqrt(np.mean((r[ok] / (1 - lev[ok])) ** 2))) if ok.any() else np.inf), int((~ok).sum())


def fit_expansion(cells, values, species, cutoffs=DEFAULT_CUTOFFS, methods=("least-squares", "ardr"), select=None, symprec=1e-3, position_tolerance=1e-2,
                  n_splits=10, seed=1, verbose=False):
    """Cluster expansion of ``values`` (per SITE; shape (n_cells,) or (n_cells, n_columns), e.g. one column per temperature of
    the cell free energies) on the lattice of ``cells`` (ASE atoms on ideal lattice sites, the first one the perfect compound).

    Nothing is chosen by hand: every cut-off set in ``cutoffs`` and every method is validated on column ``select`` (default: the
    middle one) and the best is used for all columns.  Candidates whose design matrix is rank-deficient are refused (the
    training set does not determine them).  Least squares is validated by leave-one-out (a k-fold split explodes when one cell
    alone fixes a parameter; the number of such cells is reported); other trainstation methods by k-fold.
    Raises ``ValueError`` if no candidate is determined by the training set."""
    import spglib
    from ase import Atoms
    from icet import ClusterSpace, StructureContainer
    from trainstation import CrossValidationEstimator
    A_, B_ = species; Y = np.asarray(values, dtype=float); Y = Y[:, None] if Y.ndim == 1 else Y; ks = Y.shape[1] // 2 if select is None else select; at0 = cells[0]
    lat, pos, num = spglib.standardize_cell((at0.cell[:], at0.get_scaled_positions(), at0.numbers), to_primitive=True, no_idealize=True, symprec=symprec)   # no idealisation: the sites must coincide with the training cells
    prim = Atoms(numbers=num, cell=lat, scaled_positions=pos, pbc=True); xs = [float(np.mean(np.array(c.get_chemical_symbols()) == B_)) for c in cells]
    best = None; cands = []

    def design(cs):
        sc = StructureContainer(cs)
        for c in cells:
            sc.add_structure(c, properties={"g": 0.0})
        return sc.get_fit_data(key="g")[0]

    for cut in cutoffs:
        try:
            cs = ClusterSpace(prim, cutoffs=list(cut), chemical_symbols=[[A_, B_]] * len(prim), symprec=symprec, position_tolerance=position_tolerance)
        except Exception:
            continue
        M = design(cs); rk = int(np.linalg.matrix_rank(M, tol=1e-8))
        if rk < M.shape[1]:
            cands.append({"cutoffs": list(cut), "n_parameters": len(cs), "rank": rk, "skipped": "rank deficient"})
        else:
            for fm in methods:
                if fm == "least-squares":
                    if len(cs) > 0.5 * len(cells):
                        continue
                    rcv, nsingle = _loo(M, Y[:, ks])
                else:
                    cv = CrossValidationEstimator((M, Y[:, ks]), fit_method=fm, validation_method="k-fold", n_splits=min(n_splits, len(cells)), seed=seed); cv.validate()
                    rcv, nsingle = float(cv.rmse_validation), None
                cands.append({"cutoffs": list(cut), "method": fm, "n_parameters": len(cs), "rmse_cv": rcv, "n_single_cell_parameters": nsingle})
                if best is None or rcv < best[0]:
                    best = (rcv, list(cut), fm, cs, M, nsingle)
        if verbose:
            print(cands[-1], flush=True)
    if best is None:
        raise ValueError("no candidate cluster space is determined by the training set (all rank deficient): add training cells; candidates: %r" % cands)
    _, cut, fm, cs, M, nsingle = best; P, rcv, rtr = [], [], []
    for k in range(Y.shape[1]):
        if fm == "least-squares":
            p = np.linalg.pinv(M) @ Y[:, k]; rc = _loo(M, Y[:, k])[0]
        else:
            cv = CrossValidationEstimator((M, Y[:, k]), fit_method=fm, validation_method="k-fold", n_splits=min(n_splits, len(cells)), seed=seed); cv.validate(); cv.train()
            p = cv.parameters; rc = float(cv.rmse_validation)
        P.append(p); rcv.append(rc); rtr.append(float(np.sqrt(np.mean((M @ p - Y[:, k]) ** 2))))
    return ExpansionFit(cs, np.array(P), cut, fm, np.array(rcv), np.array(rtr), nsingle, (min(xs), max(xs)), cands)


def plateau(g_single_B_on_A, g_single_A_on_B):
    """Centre and half width of the chemical-potential window (mu_B - mu_A) in which the stoichiometric compound sits, from the raw
    free energies of ONE anti-site of each kind (cell with the anti-site minus perfect cell, same number of sites)."""
    return 0.5 * (g_single_B_on_A - g_single_A_on_B), 0.5 * (g_single_B_on_A + g_single_A_on_B)


def _species(supercell):
    s = list(dict.fromkeys(supercell.get_chemical_symbols()))
    if len(s) != 2:
        raise ValueError("the perfect compound must contain exactly two elements")
    return s


def sgc_scan(expansion, supercell, temperature, mid, half, species=None, x_range=None, n_steps=46, extent=1.15, n_eq=30, n_av=60, max_exchanged=0.25, seed=0):
    """Semi-grand-canonical Monte Carlo from the ordered compound: two branches of mu_B - mu_A = mid +- dm, dm = 0 .. extent * half.

    Each branch stops when more than ``max_exchanged`` of the sites differ from the ordered compound or the composition leaves
    ``x_range`` (the trained compositions) by more than 0.01.  Returns a DataFrame (branch, dmu, x, E_per_site,
    antisite_fraction, x_std); ``n_eq`` / ``n_av`` are sweeps (trial steps per site)."""
    import pandas as pd
    from mchammer.calculators import ClusterExpansionCalculator
    from mchammer.ensembles import SemiGrandCanonicalEnsemble
    A, B = species or _species(supercell); n = len(supercell); ref = np.array(supercell.get_chemical_symbols()); rows = []
    for sign in (+1, -1):
        s = supercell.copy(); calc = ClusterExpansionCalculator(s, expansion)
        for dm in np.linspace(0.0, extent * half, n_steps + 1)[1:]:
            dmu = mid + sign * dm
            ens = SemiGrandCanonicalEnsemble(s, calculator=calc, temperature=float(temperature), chemical_potentials={A: 0.0, B: float(dmu)},
                                             random_seed=seed + int(1000 * dm) + (1 if sign > 0 else 2), ensemble_data_write_interval=n)
            ens.run((n_eq + n_av) * n); d = ens.data_container.data; d = d[d["mctrial"] > n_eq * n]; s = ens.structure
            xb = float(d[f"{B}_count"].mean()) / n; anti = float(np.mean(np.array(s.get_chemical_symbols()) != ref))
            rows.append({"branch": "B_rich" if sign > 0 else "A_rich", "dmu": float(dmu), "x": xb, "E_per_site": float(d["potential"].mean()) / n, "antisite_fraction": anti,
                         "x_std": float(d[f"{B}_count"].std()) / n})
            if anti > max_exchanged or (x_range is not None and (xb < x_range[0] - 0.01 or xb > x_range[1] + 0.01)):
                break
    return pd.DataFrame(rows)


def harvest(expansion, supercell, temperature, mid, half, species=None, thresholds=(0.02, 0.04, 0.07, 0.11, 0.16, 0.25, 0.4, 0.6), known=(), n_steps=46, extent=1.15,
            chunks=30, sweeps=3, seed=0):
    """Where does the Monte Carlo go when it leaves the trained configurations?

    The scan of :func:`sgc_scan` in the (small) training supercell; the configuration is returned each time the fraction of
    exchanged sites passes one of ``thresholds``.  Compute these cells with the real calculator, check them
    (:func:`structure_check`) and add them to the training set: if the expansion had put them too low the refit removes the
    spurious state, if they really are low they belong to this lattice.  Repeat until nothing new comes back.
    Returns ASE atoms with ``info`` = {branch, antisite_fraction, predicted (per site)}; configurations in ``known`` are skipped."""
    from mchammer.calculators import ClusterExpansionCalculator
    from mchammer.ensembles import SemiGrandCanonicalEnsemble
    A, B = species or _species(supercell); n = len(supercell); ref = np.array(supercell.get_chemical_symbols()); have = {tuple(k.get_chemical_symbols()) for k in known}; out = []
    for sign in (+1, -1):
        s = supercell.copy(); calc = ClusterExpansionCalculator(s, expansion); todo = list(thresholds)
        for dm in np.linspace(0.0, extent * half, n_steps + 1)[1:]:
            for c in range(chunks):
                ens = SemiGrandCanonicalEnsemble(s, calculator=calc, temperature=float(temperature), chemical_potentials={A: 0.0, B: float(mid + sign * dm)},
                                                 random_seed=seed + int(1000 * dm) + 7 * c + (1 if sign > 0 else 2))
                ens.run(sweeps * n); s = ens.structure; anti = float(np.mean(np.array(s.get_chemical_symbols()) != ref))
                while todo and anti >= todo[0]:
                    todo.pop(0)
                    if tuple(s.get_chemical_symbols()) not in have:
                        h = s.copy(); h.calc = None; h.info = {"branch": "B" if sign > 0 else "A", "antisite_fraction": anti, "predicted": float(expansion.predict(h))}
                        out.append(h); have.add(tuple(s.get_chemical_symbols()))
            if not todo:
                break
    return out


def branch_free_energy(scan, x0, x_range=None, max_exchanged=0.25, jump=0.02, min_span=0.02, min_points=4):
    """G(x) - G(x0) per site of the compound from a :func:`sgc_scan`: dG/dx = mu_B - mu_A integrated along each branch.

    Each branch is followed in the order of the scan and ends where the composition jumps by more than ``jump`` (another state),
    leaves ``x_range`` or the exchanged fraction passes ``max_exchanged``.  A branch that starts slightly off ``x0`` (thermal
    anti-sites) is anchored by its first chemical potential.  Returns ``(x, dG)`` sorted in x, or two empty arrays when the
    curve has fewer than ``min_points`` points or spans less than ``min_span`` in composition (the expansion let the Monte Carlo
    leave the compound at once: keep the point-defect line)."""
    X, G = [], []
    for br, q in scan.groupby("branch"):
        q = q.sort_values("dmu", ascending=(br == "B_rich")).reset_index(drop=True); stop = len(q)
        for k in range(1, len(q)):
            if abs(q.x[k] - q.x[k - 1]) > jump or (x_range is not None and not (x_range[0] <= q.x[k] <= x_range[1])):
                stop = k; break
        q = q.iloc[:stop]; q = q[q.antisite_fraction.cummax() < max_exchanged]
        if len(q) == 0:
            continue
        x = q.x.to_numpy(); m = q.dmu.to_numpy(); g = np.concatenate([[0.0], np.cumsum(0.5 * (m[1:] + m[:-1]) * np.diff(x))]) + m[0] * (x[0] - x0)
        X.append(x); G.append(g)
    if not X:
        return np.array([]), np.array([])
    x = np.concatenate(X); g = np.concatenate(G); o = np.argsort(x); x, g = x[o], g[o]; _, u = np.unique(x, return_index=True); x, g = x[u], g[u]
    if len(x) < min_points or x.max() - x.min() < min_span:
        return np.array([]), np.array([])
    return x, g


@dataclass
class DefectCEResult:
    """Result of :func:`run`.  ``curves[T] = (x, dG)``: G(x) - G(x0) per site of the compound (empty arrays when not usable);
    ``usable[T]``: validation error below the limit AND the Monte Carlo followed the compound; ``cells``: tag -> record of every
    computed cell (pass it back as ``cache`` to resume); ``history``: one entry per harvest iteration."""
    fit: ExpansionFit
    temperatures: np.ndarray
    scans: dict
    curves: dict
    usable: dict
    x0: float
    cells: dict
    excluded: dict
    history: list

    def values(self, T, xs, g0=0.0):
        """G per site at compositions ``xs`` (nan outside the curve): ``g0`` (the perfect compound) + the Monte Carlo difference."""
        x, g = self.curves[float(T)]; xs = np.asarray(xs, dtype=float)
        if x.size == 0:
            return np.full(xs.shape, np.nan)
        return np.where((xs >= x.min()) & (xs <= x.max()), g0 + np.interp(xs, x, g), np.nan)


def run(supercell, species, compute, temperatures, mc_supercell=None, blocks=None, rpair=4.0, strain_max=0.02, cv_limit=1e-3, max_iterations=4, cutoffs=DEFAULT_CUTOFFS,
        methods=("least-squares", "ardr"), plan_kwargs=None, scan_kwargs=None, harvest_kwargs=None, curve_kwargs=None, cache=None, verbose=False):
    """Defect-configuration free energy of one compound in one call: plan -> compute -> check -> fit -> (harvest -> compute -> check -> fit)* ->
    Monte Carlo -> G(x) - G(x0).  Use it for a compound that the point-defect model puts on (or within a few meV/atom of) the hull; when
    several compounds are treated, replace all of them before taking the hull again.

    ``supercell``     the perfect compound (training cell, two elements ``species`` = (A, B); x = fraction of B)
    ``compute(atoms)`` your calculator: returns ``{"values": free energy of the CELL at each of ``temperatures`` (eV), "relaxed": the
                      relaxed atoms (optional; needed for the structure check), "ok": False to reject the cell (e.g. imaginary modes)}``;
                      called once per cell on the ideal lattice sites
    ``mc_supercell``  cell of the production Monte Carlo (default: 2x2x2 of ``supercell``)
    ``cv_limit``      largest validation error (eV/site) of an expansion that is used
    ``max_iterations`` harvest iterations (0 = none); stops early when the Monte Carlo finds nothing new
    ``cache``         ``result.cells`` of an earlier call: those cells are not computed again

    Raises ``ValueError`` when no cluster space is determined by the cells (see :func:`fit_expansion`)."""
    A, B = species; T = np.atleast_1d(np.asarray(temperatures, dtype=float)); n = len(supercell); cells = dict(cache or {}); structs = {}; say = print if verbose else (lambda *a, **k: None)

    def build(la, lb):
        at = supercell.copy()
        for i in la:
            at[i].symbol = B
        for i in lb:
            at[i].symbol = A
        return at

    def do(tag, at):
        structs[tag] = at
        if tag in cells:
            return
        r = compute(at.copy()); rec = {"x": float(np.mean(np.array(at.get_chemical_symbols()) == B)), "ok": bool(r.get("ok", True)), "values": [float(v) for v in np.atleast_1d(r["values"])]}
        if r.get("relaxed") is not None:
            rec["_relaxed_cell"] = np.asarray(r["relaxed"].cell[:]).tolist(); rec["_relaxed"] = r["relaxed"]
        cells[tag] = rec; say("computed", tag, "x = %.4f" % rec["x"])

    def check_all():
        ref = cells["perfect"].get("_relaxed")
        for tag, rec in cells.items():
            if ref is not None and rec.get("_relaxed") is not None and "left_parent" not in rec and tag in structs:
                rec.update(structure_check(structs[tag], rec["_relaxed"], ref.cell[:], strain_max))

    def fit_now():
        use = [t for t in structs if cells[t]["ok"] and not cells[t].get("left_parent", False)]
        f = fit_expansion([structs[t] for t in use], np.array([cells[t]["values"] for t in use]) / n, species, cutoffs=cutoffs, methods=methods, verbose=verbose)
        return f, use

    for tag, la, lb in training_plan(supercell, A, B, rpair=rpair, blocks=blocks, **(plan_kwargs or {})):
        do(tag, build(la, lb))
    for tag in [t for t in cells if t.startswith("harvest_") and t not in structs and "_symbols" in cells[t]]:     # harvested cells of a cached run
        at = supercell.copy(); at.set_chemical_symbols(cells[tag]["_symbols"]); structs[tag] = at
    check_all(); fit, use = fit_now(); history = []
    g1 = lambda tag, k: cells[tag]["values"][k] - cells["perfect"]["values"][k]
    win = lambda k: plateau(g1("single_B_on_A", k), g1("single_A_on_B", k))
    for it in range(1, max_iterations + 1):
        new = []
        for k in sorted({0, len(T) - 1}):
            mid, half = win(k)
            new += harvest(fit.expansion(k), supercell, T[k], mid, half, species=species, known=list(structs.values()) + new, **(harvest_kwargs or {}))
        if not new:
            history.append({"iteration": it, "harvested": 0}); break
        for j, h in enumerate(new):
            tag = f"harvest_i{it}_{j}"; pred = h.info["predicted"]; at = h.copy(); at.info = {}
            do(tag, at); cells[tag]["_symbols"] = at.get_chemical_symbols(); cells[tag]["exchanged"] = h.info["antisite_fraction"]; cells[tag]["predicted_per_site"] = pred
        check_all(); fit, use = fit_now()
        history.append({"iteration": it, "harvested": len(new), "left_parent": int(sum(bool(cells[f"harvest_i{it}_{j}"].get("left_parent")) for j in range(len(new)))),
                        "rmse_cv": [float(v) for v in fit.rmse_cv]}); say("harvest iteration", history[-1])
    big = mc_supercell if mc_supercell is not None else supercell.repeat((2, 2, 2)); x0 = float(np.mean(np.array(supercell.get_chemical_symbols()) == B)); scans, curves, usable = {}, {}, {}
    for k, Tk in enumerate(T):
        mid, half = win(k); scans[float(Tk)] = sgc_scan(fit.expansion(k), big, Tk, mid, half, species=species, x_range=fit.x_range, **(scan_kwargs or {}))
        x, g = branch_free_energy(scans[float(Tk)], x0, x_range=fit.x_range, **(curve_kwargs or {}))
        ok = fit.usable(k, cv_limit) and x.size > 0; curves[float(Tk)] = (x, g) if ok else (np.array([]), np.array([])); usable[float(Tk)] = bool(ok)
    excluded = {"left_parent": sorted(t for t, r in cells.items() if r.get("left_parent")), "rejected": sorted(t for t, r in cells.items() if not r["ok"])}
    for r in cells.values():
        r.pop("_relaxed", None)
    return DefectCEResult(fit, T, scans, curves, usable, x0, cells, excluded, history)
