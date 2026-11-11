"""Stage 07: T–x phase diagram, invariant reactions, error sensitivity, records.

* :func:`scan` evaluates :func:`ftphase.equilibrium.equilibrium_at_T` on a
  temperature grid; the phases at each T are produced by a user callable
  ``builder(T) -> list[Phase]`` (see :mod:`ftphase.assemble` for builders from
  a :class:`ftphase.records.FreeEnergyTable`).
* :func:`invariants` finds temperatures where the set of coexisting pairs
  changes (eutectic / peritectic / congruent points are bracketed between two
  grid temperatures; refine the grid around them).
* :func:`sensitivity` is a Monte Carlo propagation of free-energy
  uncertainties: each sample shifts every phase by a random offset drawn from
  its ``G_err`` (and optionally a random slope), recomputes the diagram, and
  returns mean and standard deviation of every boundary.  This is the error
  propagation that none of the upstream examples performs (examples.md).
* :func:`phase_sets`, :func:`phase_label_accuracy`, :func:`stability_probability`
  (2026-11-12, after Zhang et al., Scripta Mater. 289 (2027) 117663): the phase
  set at every (T, x) grid point read off a regions table, the fraction of grid
  points where two diagrams have the same phase set, and - from the Monte Carlo
  samples of :func:`sensitivity`, which now also takes a systematic prior
  ``sigma_H`` / ``sigma_S`` (offset dH - T dS per phase) - the probability
  that each phase is present at a grid point or anywhere.
* :func:`plot_tx` draws per-temperature bands (not fill_between across
  temperatures, which joins disconnected regions; see examples.md pitfalls).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from .equilibrium import Phase, PhaseCurve, PointPhase, equilibrium_at_T, EquilibriumResult


def _pair_key(c):
    return tuple(sorted([c.phase_a, c.phase_b]))


def scan(builder: Callable[[float], Sequence[Phase]], temperatures, refine: bool = True, **kw) -> pd.DataFrame:
    """Two-phase regions on a temperature grid.

    Returns a DataFrame with columns T, phase_a, x_a, phase_b, x_b, g_a, g_b,
    refined, note (one row per coexistence segment).
    """
    rows = []
    for T in np.asarray(temperatures, dtype=float):
        res = equilibrium_at_T(builder(T), T=T, refine=refine, **kw)
        for c in res.coexistence:
            rows.append({"T": T, "phase_a": c.phase_a, "x_a": c.x_a, "phase_b": c.phase_b, "x_b": c.x_b, "g_a": c.g_a, "g_b": c.g_b, "refined": c.refined, "note": c.note})
    cols = ["T", "phase_a", "x_a", "phase_b", "x_b", "g_a", "g_b", "refined", "note"]
    return pd.DataFrame(rows, columns=cols)


def single_phase_scan(builder, temperatures, **kw) -> pd.DataFrame:
    rows = []
    for T in np.asarray(temperatures, dtype=float):
        res = equilibrium_at_T(builder(T), T=T, **kw)
        for ph, lo, hi in res.single_phase:
            rows.append({"T": T, "phase": ph, "x_lo": lo, "x_hi": hi})
    return pd.DataFrame(rows, columns=["T", "phase", "x_lo", "x_hi"])


def invariants(regions: pd.DataFrame) -> pd.DataFrame:
    """Temperatures where the set of coexisting phase pairs changes.

    Returns rows (T_low, T_high, pairs_below, pairs_above).  A eutectic
    L -> a + b appears as pairs_below={a+b}, pairs_above={a+L, L+b}.
    """
    Ts = np.sort(regions["T"].unique())
    out = []
    prev = None
    prevT = None
    for T in Ts:
        pairs = frozenset(_pair_key(r) for r in regions.loc[regions["T"] == T].itertuples())
        if prev is not None and pairs != prev:
            out.append({"T_low": prevT, "T_high": T, "pairs_below": sorted("+".join(p) for p in prev), "pairs_above": sorted("+".join(p) for p in pairs)})
        prev, prevT = pairs, T
    return pd.DataFrame(out, columns=["T_low", "T_high", "pairs_below", "pairs_above"])


@dataclass
class SensitivityResult:
    table: pd.DataFrame     # T, pair, x_a_mean, x_a_std, x_b_mean, x_b_std, n_found, n_samples
    samples: List[pd.DataFrame]


def sensitivity(
    builder_with_shifts: Callable[[float, Dict[str, float], Dict[str, float]], Sequence[Phase]],
    temperatures,
    sigma: Dict[str, float],
    n_samples: int = 50,
    slope_sigma: Optional[Dict[str, float]] = None,
    rng=None,
    sigma_H: Optional[Dict[str, float]] = None,
    sigma_S: Optional[Dict[str, float]] = None,
    **kw,
) -> SensitivityResult:
    """Monte Carlo propagation of per-phase free-energy uncertainties.

    ``builder_with_shifts(T, offsets, slopes)`` must return the phases with
    g_phase(x) -> g_phase(x) + offsets[phase] + slopes[phase] * (x - 0.5).
    ``sigma[phase]`` is the 1-sigma offset in eV/atom (e.g. calphy's
    free_energy_error or an estimate of the QHA systematic error);
    ``slope_sigma[phase]`` optionally randomises the composition dependence.
    ``sigma_H[phase]`` (eV/atom) and ``sigma_S[phase]`` (eV/atom/K) add a
    systematic prior: one dH and one dS per phase and sample, the offset at T
    being dH - T dS (e.g. the MLIP-vs-DFT level of Zhang et al. 2027,
    1.41 kJ/mol and 1.73 J/mol/K = :data:`ZHANG_SIGMA_H`, :data:`ZHANG_SIGMA_S`).
    A float is applied to every phase of ``sigma``.
    """
    rng = np.random.default_rng(rng)
    phases = list(sigma)
    slope_sigma = slope_sigma or {}
    sH = {p: float(sigma_H) for p in phases} if isinstance(sigma_H, (int, float)) else (sigma_H or {})
    sS = {p: float(sigma_S) for p in phases} if isinstance(sigma_S, (int, float)) else (sigma_S or {})
    samples = []
    for _ in range(n_samples):
        off = {p: rng.normal(0.0, sigma[p]) for p in phases}
        slo = {p: rng.normal(0.0, slope_sigma.get(p, 0.0)) for p in phases}
        dH = {p: rng.normal(0.0, sH.get(p, 0.0)) for p in phases}
        dS = {p: rng.normal(0.0, sS.get(p, 0.0)) for p in phases}
        samples.append(scan(lambda T, off=off, slo=slo, dH=dH, dS=dS: builder_with_shifts(T, {p: off[p] + dH[p] - T * dS[p] for p in off}, slo), temperatures, **kw))
    def _keyed(df_T):
        out = {}
        seen = {}
        for r in df_T.sort_values("x_a").itertuples():
            pair = (r.phase_a, r.phase_b)
            k = seen.get(pair, 0)
            seen[pair] = k + 1
            out[(r.phase_a, r.phase_b, k)] = (r.x_a, r.x_b)
        return out

    rows = []
    for T in np.asarray(temperatures, dtype=float):
        per_sample = [_keyed(s.loc[s["T"] == T]) for s in samples]
        keys = sorted({k for d in per_sample for k in d})
        for key in keys:
            vals = [d[key] for d in per_sample if key in d]
            xa = np.array([v[0] for v in vals]); xb = np.array([v[1] for v in vals])
            rows.append({"T": T, "pair": f"{key[0]}+{key[1]}" + (f"#{key[2]}" if key[2] else ""), "x_a_mean": xa.mean(), "x_a_std": xa.std(), "x_b_mean": xb.mean(), "x_b_std": xb.std(), "n_found": len(vals), "n_samples": n_samples})
    return SensitivityResult(pd.DataFrame(rows), samples)


#: MLIP-level free-energy uncertainty of Zhang et al., Scripta Mater. 289 (2027) 117663 (dH 1.41 kJ/mol, dS 1.73 J/mol/K per mole of atoms)
ZHANG_SIGMA_H = 1410.0 / 96485.33212       # eV/atom
ZHANG_SIGMA_S = 1.73 / 96485.33212         # eV/atom/K

UNKNOWN = "?"


def phase_sets(regions: pd.DataFrame, temperatures, xs, single: Optional[pd.DataFrame] = None, drop_same_phase: bool = True) -> np.ndarray:
    """Phase set at every (T, x) grid point from a two-phase-regions table (output of :func:`scan`).

    Inside a segment the set is {phase_a, phase_b}; between two segments (and outside the outermost ones) it is the single
    phase the neighbouring segment ends in.  A temperature without any segment is single phase over the whole range: its
    name is taken from ``single`` (output of :func:`single_phase_scan`) when given, otherwise the point is labelled
    {:data:`UNKNOWN`}.  Same-phase segments (fit noise, phase_a == phase_b) count as that single phase.  Returns an object
    array (n_T, n_x) of frozensets; temperatures are matched to the nearest table temperature.
    """
    temperatures = np.asarray(temperatures, dtype=float); xs = np.asarray(xs, dtype=float)
    out = np.empty((len(temperatures), len(xs)), dtype=object)
    Tt = np.sort(regions["T"].unique()) if len(regions) else np.array([])
    Ts_single = np.sort(single["T"].unique()) if single is not None and len(single) else np.array([])
    for i, T in enumerate(temperatures):
        segs = []
        if len(Tt):
            Tn = Tt[np.argmin(np.abs(Tt - T))]
            if abs(Tn - T) <= max(1e-6, 0.51 * (np.min(np.diff(Tt)) if len(Tt) > 1 else 1e-6)):
                r = regions.loc[regions["T"] == Tn]
                segs = sorted((min(q.x_a, q.x_b), max(q.x_a, q.x_b), q.phase_a if q.x_a <= q.x_b else q.phase_b, q.phase_b if q.x_a <= q.x_b else q.phase_a) for q in r.itertuples())
        sp = []
        if len(Ts_single):
            Tn = Ts_single[np.argmin(np.abs(Ts_single - T))]
            sp = [(q.x_lo, q.x_hi, q.phase) for q in single.loc[single["T"] == Tn].itertuples()]
        for j, x in enumerate(xs):
            val = None
            for lo, hi, pa, pb in segs:
                if lo - 1e-12 <= x <= hi + 1e-12:
                    val = frozenset([pa]) if (pa == pb and drop_same_phase) else frozenset([pa, pb]); break
            if val is None and segs:
                left = [sg for sg in segs if sg[1] < x]; right = [sg for sg in segs if sg[0] > x]
                val = frozenset([left[-1][3]]) if left else frozenset([right[0][2]])
            if val is None:
                hit = [ph for lo, hi, ph in sp if lo - 1e-9 <= x <= hi + 1e-9]
                val = frozenset(hit[:1]) if hit else frozenset([UNKNOWN])
            out[i, j] = val
    return out


def phase_label_accuracy(sets_a: np.ndarray, sets_b: np.ndarray, rename_a: Optional[Dict[str, str]] = None, rename_b: Optional[Dict[str, str]] = None,
                         mask: Optional[np.ndarray] = None, skip_unknown: bool = True) -> float:
    """Fraction of grid points where two phase-set arrays (from :func:`phase_sets`) agree: the phase-label classification
    accuracy of Hardcastle et al. / Zhu et al. used by Zhang et al. 2027.  ``rename_*`` map phase names to common labels
    (e.g. CALPHAD names to the run's names); points labelled :data:`UNKNOWN` in either array are left out unless
    ``skip_unknown`` is False; ``mask`` (same shape, True = use) restricts the comparison (e.g. to the run's T-x coverage)."""
    ra, rb = rename_a or {}, rename_b or {}
    n = ok = 0
    for idx in np.ndindex(sets_a.shape):
        if mask is not None and not mask[idx]:
            continue
        a = frozenset(ra.get(p, p) for p in sets_a[idx]); b = frozenset(rb.get(p, p) for p in sets_b[idx])
        if skip_unknown and (UNKNOWN in a or UNKNOWN in b):
            continue
        n += 1; ok += a == b
    return ok / n if n else float("nan")


@dataclass
class StabilityProbability:
    temperatures: np.ndarray
    xs: np.ndarray
    maps: Dict[str, np.ndarray]          # phase -> P(phase present at (T, x)), shape (n_T, n_x)
    anywhere: Dict[str, float]           # phase -> P(phase present somewhere on the grid)
    per_T: Dict[str, np.ndarray]         # phase -> P(phase present somewhere at T)
    agreement: Optional[np.ndarray]      # per sample: label accuracy against the reference sets (None without a reference)
    n_samples: int


def stability_probability(samples: Sequence[pd.DataFrame], temperatures, xs, reference: Optional[np.ndarray] = None, single: Optional[Sequence[pd.DataFrame]] = None) -> StabilityProbability:
    """Probability maps from Monte Carlo diagram samples (``SensitivityResult.samples``): for every phase the fraction of
    samples in which it belongs to the phase set at a grid point, at any composition of a temperature, and anywhere.
    A phase that never forms a two-phase segment at a temperature is invisible in a regions table (single-phase rows are
    {:data:`UNKNOWN`} unless ``single`` gives one single-phase table per sample).  ``reference`` (phase sets of the
    unperturbed diagram) adds each sample's label accuracy against it."""
    temperatures = np.asarray(temperatures, dtype=float); xs = np.asarray(xs, dtype=float)
    maps: Dict[str, np.ndarray] = {}; any_T: Dict[str, np.ndarray] = {}; anywhere: Dict[str, float] = {}; acc = []
    for k, reg in enumerate(samples):
        ps = phase_sets(reg, temperatures, xs, single=single[k] if single is not None else None)
        present: Dict[str, np.ndarray] = {}
        for idx in np.ndindex(ps.shape):
            for p in ps[idx]:
                if p != UNKNOWN:
                    present.setdefault(p, np.zeros(ps.shape, dtype=bool))[idx] = True
        for p, m in present.items():
            maps.setdefault(p, np.zeros(ps.shape)); maps[p] += m
            any_T.setdefault(p, np.zeros(len(temperatures))); any_T[p] += m.any(axis=1)
            anywhere[p] = anywhere.get(p, 0.0) + 1.0
        if reference is not None:
            acc.append(phase_label_accuracy(ps, reference))
    n = max(1, len(samples))
    return StabilityProbability(temperatures, xs, {p: m / n for p, m in maps.items()}, {p: v / n for p, v in anywhere.items()}, {p: v / n for p, v in any_T.items()},
                                np.array(acc) if reference is not None else None, len(samples))


def plot_stability(prob: StabilityProbability, phases: Optional[Sequence[str]] = None, ncols: int = 4, xlabel="x", ylabel="T (K)"):
    """One probability map per phase (P(phase present at (T, x)), 0..1); the title carries P(present anywhere)."""
    import matplotlib.pyplot as plt

    phases = list(phases or sorted(prob.maps, key=lambda p: -prob.anywhere[p]))
    ncols = min(ncols, len(phases)); nrows = (len(phases) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.2 * ncols, 2.7 * nrows), squeeze=False)
    T, x = prob.temperatures, prob.xs
    for ax, p in zip(axes.flat, phases):
        im = ax.imshow(prob.maps[p], origin="lower", aspect="auto", extent=(x[0], x[-1], T[0], T[-1]), vmin=0, vmax=1, cmap="viridis")
        ax.set_title(f"{p}: P(anywhere) = {prob.anywhere[p]:.2f}", fontsize=9); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    for ax in list(axes.flat)[len(phases):]:
        ax.axis("off")
    fig.colorbar(im, ax=axes, shrink=0.8, label="P(phase present)")
    return fig


def plot_tx(regions: pd.DataFrame, ax=None, colors: Optional[Dict[str, str]] = None, dT: Optional[float] = None, xlabel="x", ylabel="T (K)", alpha=0.6, show_points=True):
    """Draw two-phase regions as one band per temperature (no cross-T fill)."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4.5))
    Ts = np.sort(regions["T"].unique())
    if dT is None:
        dT = float(np.min(np.diff(Ts))) if len(Ts) > 1 else 1.0
    pairs = sorted({"+".join(_pair_key(r)) for r in regions.itertuples()})
    cmap = plt.get_cmap("tab10")
    colors = colors or {p: cmap(i % 10) for i, p in enumerate(pairs)}
    seen = set()
    for r in regions.itertuples():
        key = "+".join(_pair_key(r))
        lab = key if key not in seen else None
        seen.add(key)
        ax.fill_betweenx([r.T - dT / 2, r.T + dT / 2], r.x_a, r.x_b, color=colors[key], alpha=alpha, linewidth=0, label=lab)
        if show_points:
            ax.plot([r.x_a, r.x_b], [r.T, r.T], ".", color=colors[key], ms=2)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_xlim(0, 1)
    ax.legend(fontsize=8, loc="best")
    return ax


def write_records(path, regions: pd.DataFrame, meta: Dict):
    """TSV + JSON sidecar with everything needed to reproduce (workflow section 8)."""
    import json

    regions.to_csv(path, sep="\t", index=False)
    with open(str(path) + ".meta.json", "w") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False, default=str)
