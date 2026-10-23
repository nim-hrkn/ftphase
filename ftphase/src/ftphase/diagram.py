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
    **kw,
) -> SensitivityResult:
    """Monte Carlo propagation of per-phase free-energy uncertainties.

    ``builder_with_shifts(T, offsets, slopes)`` must return the phases with
    g_phase(x) -> g_phase(x) + offsets[phase] + slopes[phase] * (x - 0.5).
    ``sigma[phase]`` is the 1-sigma offset in eV/atom (e.g. calphy's
    free_energy_error or an estimate of the QHA systematic error);
    ``slope_sigma[phase]`` optionally randomises the composition dependence.
    """
    rng = np.random.default_rng(rng)
    phases = list(sigma)
    slope_sigma = slope_sigma or {}
    samples = []
    for _ in range(n_samples):
        off = {p: rng.normal(0.0, sigma[p]) for p in phases}
        slo = {p: rng.normal(0.0, slope_sigma.get(p, 0.0)) for p in phases}
        samples.append(scan(lambda T, off=off, slo=slo: builder_with_shifts(T, off, slo), temperatures, **kw))
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
