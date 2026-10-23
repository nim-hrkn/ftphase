"""Stage 05: put all phases on one footing and build the per-T phase list.

* :func:`relative_to_pure` rewrites G of every row relative to the chosen pure
  element reference phases at the same T and P, eq. (G1); the reference_state
  column is updated accordingly.
* :func:`add_configurational_term` adds -T s_conf (ideal or sublattice) to the
  rows of one phase and sets the ``config_entropy`` flag; it refuses to add a
  term twice or to a phase whose free energy already contains configurational
  statistics (liquid TI, MC).
* :func:`interpolate_T` brings all phases to a common temperature grid.
* :func:`builder_from_table` returns the ``builder(T)`` used by
  :mod:`ftphase.diagram`: solution rows become :class:`PhaseCurve` objects,
  point rows :class:`PointPhase`, limited rows curves restricted to the
  sampled composition interval.
* :func:`to_calphy_dataframe` / :func:`to_calphy_phase_diagram` export the
  table to calphy's ``PhaseDiagram.from_df`` so that calphy's CALPHAD-surface
  fit and ``to_tdb`` (calphy >= 2.3, calphy/phase_diagram.py) can be used,
  and :func:`check_with_pycalphad` recomputes the diagram from that TDB.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from .configurational import ideal_entropy, sublattice_entropy
from .equilibrium import Phase, PhaseCurve, PointPhase
from .records import FreeEnergyTable


# ---------------------------------------------------------------------------
def relative_to_pure(table: FreeEnergyTable, ref_A: str, ref_B: str, label: Optional[str] = None) -> FreeEnergyTable:
    """G -> G - [(1-x) g_A^ref(T) + x g_B^ref(T)], eq. (G1).

    ref_A / ref_B are phase names whose rows at x=0 / x=1 define the
    reference (e.g. 'fcc' and 'bcc').  Interpolated linearly in T.
    """
    df = table.df.copy()
    gA = df[(df.phase == ref_A) & (np.isclose(df.x, 0.0))].sort_values("T")
    gB = df[(df.phase == ref_B) & (np.isclose(df.x, 1.0))].sort_values("T")
    if gA.empty or gB.empty:
        raise ValueError("reference rows (x=0 in ref_A, x=1 in ref_B) not found")
    fA = lambda T: np.interp(T, gA["T"].to_numpy(), gA["G"].to_numpy())
    fB = lambda T: np.interp(T, gB["T"].to_numpy(), gB["G"].to_numpy())
    df["G"] = df["G"] - ((1 - df["x"]) * fA(df["T"]) + df["x"] * fB(df["T"]))
    df["reference_state"] = label or f"pure {ref_A}(x=0) and {ref_B}(x=1) at same T,P"
    out = FreeEnergyTable.from_dataframe(df, table.meta)
    out.meta["reference"] = {"A": ref_A, "B": ref_B}
    return out


def add_configurational_term(table: FreeEnergyTable, phase: str, model: str = "ideal", site_model: Optional[Callable[[float], tuple]] = None) -> FreeEnergyTable:
    """Add -T s_conf to one phase.

    model='ideal'      : eq. (E1) on the overall composition (random solution)
    model='sublattice' : eq. (E10)-(E12); ``site_model(x)`` must return
                         (site_fractions, site_counts) for composition x,
                         e.g. ftphase.configurational.b32_antisite_site_fractions.
    """
    df = table.df.copy()
    m = df.phase == phase
    if not m.any():
        raise ValueError(f"phase {phase} not in table")
    flags = set(df.loc[m, "config_entropy"].unique())
    if flags != {"none"}:
        raise ValueError(f"phase {phase} already carries configurational statistics: {flags}")
    if model == "ideal":
        s = np.array([ideal_entropy(x) for x in df.loc[m, "x"]])
    elif model == "sublattice":
        if site_model is None:
            raise ValueError("site_model required")
        s = np.array([sublattice_entropy(*site_model(x), basis="atom") for x in df.loc[m, "x"]])
    else:
        raise ValueError("model must be 'ideal' or 'sublattice'")
    df.loc[m, "G"] = df.loc[m, "G"] - df.loc[m, "T"] * s
    df.loc[m, "config_entropy"] = model
    return FreeEnergyTable.from_dataframe(df, table.meta)


def interpolate_T(table: FreeEnergyTable, temperatures, kind: str = "linear") -> FreeEnergyTable:
    """Interpolate every (phase, x) series onto ``temperatures``.

    Rows outside a series' own T range are dropped (no extrapolation).
    """
    from scipy.interpolate import interp1d

    Ts = np.asarray(temperatures, dtype=float)
    rows = []
    for (ph, x), g in table.df.groupby(["phase", "x"]):
        g = g.sort_values("T")
        if len(g) == 1:
            sel = Ts[np.isclose(Ts, g["T"].iloc[0])]
            for T in sel:
                r = g.iloc[0].to_dict(); r["T"] = T; rows.append(r)
            continue
        f = interp1d(g["T"], g["G"], kind=kind if len(g) > 3 or kind == "linear" else "linear")
        fe = interp1d(g["T"], g["G_err"], kind="linear")
        fv = interp1d(g["T"], g["V"].fillna(np.nan), kind="linear") if g["V"].notna().all() else None
        inside = Ts[(Ts >= g["T"].min() - 1e-9) & (Ts <= g["T"].max() + 1e-9)]
        for T in inside:
            Tc = float(np.clip(T, g["T"].min(), g["T"].max()))
            r = g.iloc[0].to_dict()
            r["T"], r["G"], r["G_err"] = T, float(f(Tc)), float(fe(Tc))
            r["V"] = float(fv(Tc)) if fv is not None else np.nan
            rows.append(r)
    return FreeEnergyTable.from_rows(rows, table.meta)


_WS_CACHE: Dict[tuple, tuple] = {}


def _ws_curve_cached(ph: str, T: float, g: pd.DataFrame, model, n_sample: int):
    """Dense (x, G) of the Wagner-Schottky model for phase ``ph`` at ``T`` (cached per table rows).

    ``model`` = ("wagner_schottky", (a, b)[, options]); options may give ``x_range`` (default: the
    sampled range widened by 0.02 on each side, inside (0, 1)) and ``n_sites``.  The rows carry
    ``config_entropy`` 'none' (raw cell free energies); the configurational term is produced here.
    """
    from .configurational import defect_energies_from_cells, wagner_schottky_curve

    opts = model[2] if len(model) > 2 else {}
    key = (ph, round(float(T), 6), tuple(np.round(g["x"].to_numpy(), 8)), tuple(np.round(g["G"].to_numpy(), 10)))
    if key in _WS_CACHE:
        return _WS_CACHE[key]
    # rows must be raw cell energies: undo an analytic sublattice term if one was added
    G = g["G"].to_numpy().copy()
    if "config_entropy" in g and (g["config_entropy"] == "sublattice").any():
        raise ValueError(f"{ph}: Wagner-Schottky model needs raw cell rows (config_entropy 'none'); do not add_configurational_term for this phase")
    e, g0, n_sites, rows = defect_energies_from_cells(g["x"].to_numpy(), G, g["n_atoms"].to_numpy(), model[1], n_sites=opts.get("n_sites"))
    xs = g["x"].to_numpy()
    lo, hi = opts.get("x_range", (max(1e-3, xs.min()), min(1 - 1e-3, xs.max())))     # the sampled range (no extrapolation) unless x_range is given
    xg = np.linspace(lo, hi, int(opts.get("n_grid", 201)))
    gg = wagner_schottky_curve(xg, T, model[1], e, g0_atom=g0)
    _WS_CACHE[key] = (xg, gg)
    return xg, gg


def builder_from_table(table: FreeEnergyTable, fit: str = "spline", poly_order: int = 4, n_sample: int = 401, fits: Optional[Dict[str, str]] = None, T_tol: float = 1e-6, use_err_weights: bool = False, ideal_excess_fit: bool = True, poly_orders: Optional[Dict[str, int]] = None, entropy_models: Optional[Dict[str, tuple]] = None) -> Callable[[float], List[Phase]]:
    """Return builder(T) producing Phase objects from the rows at temperature T.

    ``fits`` may override the fit type per phase, e.g. {'liquid': 'rk'};
    ``poly_orders`` the polynomial order per phase (a liquid sampled over the
    whole range needs a higher order than a solid solution sampled near x=0).
    ``entropy_models``: {phase: (site_model, stoich_x)} for ordered phases whose
    rows carry config_entropy 'sublattice': the analytic -T s_conf(x) of that
    site model is separated from the fit (PhaseCurve.from_points entropy_fn) and
    the 'poly' fit is done per branch around stoich_x.
    ``ideal_excess_fit``: for 'poly'/'smooth' fits of a phase whose rows carry
    config_entropy 'ideal' or 'liquid-ti', fit only the excess over the
    analytic ideal-mixing term (PhaseCurve.from_points(ideal_T=T)); a plain
    polynomial through G that contains k_B T x ln x cannot reproduce the end
    point slope and invents miscibility gaps from sampling noise.
    """
    fits = fits or {}
    poly_orders = poly_orders or {}
    entropy_models = entropy_models or {}
    df = table.df

    def builder(T: float, offsets: Optional[Dict[str, float]] = None, slopes: Optional[Dict[str, float]] = None) -> List[Phase]:
        offsets = offsets or {}
        slopes = slopes or {}
        sub = df[np.abs(df["T"] - T) <= T_tol]
        if sub.empty:
            raise ValueError(f"no rows at T={T}; call interpolate_T first")
        phases: List[Phase] = []
        for ph, g in sub.groupby("phase", sort=False):
            kind = g["kind"].iloc[0]
            off = offsets.get(ph, 0.0)
            slo = slopes.get(ph, 0.0)
            if kind == "point" or g["x"].nunique() < 2:
                # a solution/limited phase sampled at a single composition at this T (e.g. one cell whose T range
                # extends beyond the others') is a point at that T, not a curve
                x0 = float(g["x"].iloc[0])
                phases.append(PointPhase(ph, x0, float(g["G"].iloc[0]) + off + slo * (x0 - 0.5)))
            else:
                w = (1.0 / np.maximum(g["G_err"].to_numpy(), 1e-6)) if use_err_weights else None
                ideal_T = T if (ideal_excess_fit and set(g["config_entropy"]) <= {"ideal", "liquid-ti"}) else None
                fit_ph = fits.get(ph, fit)
                xs = g["x"].to_numpy()
                if fit_ph == "rk" and not (np.isclose(xs.min(), 0.0) and np.isclose(xs.max(), 1.0)):
                    fit_ph = "poly"        # Redlich-Kister needs both pure ends; at this T the phase is sampled on a sub-range
                ent_fn = ent_T = branch = None
                if ph in entropy_models and str(entropy_models[ph][0]) == "wagner_schottky":
                    # thermal-defect (Wagner-Schottky) model: effective defect free energies from the sampled
                    # cells at this T, G(x) from the minimisation on a dense grid, spline through it
                    xg, gg = _ws_curve_cached(ph, T, g, entropy_models[ph], n_sample)
                    pc = PhaseCurve.from_points(ph, xg, gg + off + slo * (xg - 0.5), fit="spline", n_sample=n_sample, limited=(kind == "limited"))
                    phases.append(pc)
                    continue
                if ph in entropy_models and set(g["config_entropy"]) == {"sublattice"}:
                    site_model, branch = entropy_models[ph]
                    ent_fn = (lambda v, sm=site_model: sublattice_entropy(*sm(v), basis="atom"))
                    ent_T = T
                pc = PhaseCurve.from_points(ph, xs, g["G"].to_numpy() + off + slo * (xs - 0.5), fit=fit_ph, poly_order=poly_orders.get(ph, poly_order), n_sample=n_sample, limited=(kind == "limited"), weights=w, ideal_T=ideal_T, entropy_fn=ent_fn, entropy_T=ent_T, branch_x=branch)
                phases.append(pc)
        return phases

    return builder


def fit_residuals(builder, T: float, threshold: float = 0.005) -> pd.DataFrame:
    """RMSE of each solution-phase fit at temperature T; rows above
    ``threshold`` (eV/atom) are flagged.  Large residuals mean the composition
    grid is too coarse or the fit form is wrong (workflow section 8: check the
    fit error's effect on the boundaries)."""
    rows = []
    for p in builder(T):
        if isinstance(p, PhaseCurve):
            rows.append({"T": T, "phase": p.name, "rmse_eV": p.rmse, "flag": p.rmse > threshold})
    return pd.DataFrame(rows, columns=["T", "phase", "rmse_eV", "flag"])


# ---------------------------------------------------------------------------
# calphy / pycalphad bridges
# ---------------------------------------------------------------------------
def to_calphy_dataframe(table: FreeEnergyTable) -> pd.DataFrame:
    """Layout expected by calphy.phase_diagram.PhaseDiagram.from_df:
    one row per (phase, composition) with array columns temperature and
    free_energy (eV/atom)."""
    rows = []
    for (ph, x), g in table.df.groupby(["phase", "x"]):
        g = g.sort_values("T")
        rows.append({"phase": ph, "composition": float(x), "temperature": g["T"].to_numpy(), "free_energy": g["G"].to_numpy(), "error": g["G_err"].to_numpy()})
    return pd.DataFrame(rows)


def to_calphy_phase_diagram(table: FreeEnergyTable, reference_element: str, composition_intervals: Optional[Dict] = None):
    """calphy.phase_diagram.PhaseDiagram built from the table (needs calphy>=2.3)."""
    from calphy.phase_diagram import PhaseDiagram  # type: ignore

    intervals = dict(composition_intervals or {})
    for ph, g in table.df.groupby("phase"):
        if ph not in intervals and g["kind"].iloc[0] in ("limited", "point"):
            intervals[ph] = (float(g["x"].min()), float(g["x"].max()))
    return PhaseDiagram.from_df(to_calphy_dataframe(table), reference_element, composition_intervals=intervals)


def check_with_pycalphad(tdb_path, elements: Sequence[str], temperatures, x_grid=None, phases=None):
    """Equilibrium phase sets from a TDB with pycalphad (Otis & Liu 2017).

    Returns a DataFrame (T, x, phases) for a quick comparison with ftphase's
    own hull; use pycalphad's binplot for the full diagram.
    """
    from pycalphad import Database, equilibrium, variables as v  # type: ignore

    db = Database(str(tdb_path))
    comps = [e.upper() for e in elements] + ["VA"]
    phases = phases or list(db.phases.keys())
    x_grid = np.linspace(0.01, 0.99, 25) if x_grid is None else np.asarray(x_grid)
    rows = []
    B = elements[1].upper()
    for T in np.asarray(temperatures, dtype=float):
        for x in x_grid:
            eq = equilibrium(db, comps, phases, {v.X(B): float(x), v.T: float(T), v.P: 101325, v.N: 1}, verbose=False)
            ph = sorted({str(p) for p in np.array(eq.Phase.values).ravel() if p})
            rows.append({"T": T, "x": float(x), "phases": "+".join(ph)})
    return pd.DataFrame(rows)
