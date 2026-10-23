"""Stage 05/07: the single free-energy table and its provenance fields.

Every free energy that enters the equilibrium step is a row with explicit
units, pressure, composition basis, reference state, method and the flag that
says whether a configurational term has already been included (workflow
section 8: "phase, composition, T, P, G, uncertainty, volume, model/version,
reference_state, method").  The schema is deliberately flat (one row per
(phase, composition, T)) so that it can be stored as TSV/parquet and converted
to calphy's ``PhaseDiagram.from_df`` layout or to pycalphad inputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

COLUMNS = [
    "phase",            # str, phase label
    "kind",             # 'solution' | 'point' (fixed composition) | 'limited' (solution valid only inside [x_min, x_max])
    "x",                # float, mole fraction of the reference element (atom basis, vacancies excluded)
    "T",                # K
    "P_GPa",            # GPa
    "G",                # eV/atom
    "G_err",            # eV/atom, 1 sigma (0 if unknown -> state it in 'method')
    "V",                # A^3/atom (nan if unknown)
    "model",            # potential / model identifier with version
    "reference_state",  # e.g. 'absolute MLIP energy', 'SER-like: pure fcc-A and bcc-B at same T,P'
    "method",           # free text: 'QHA vinet 7 volumes, phonopy 2x2x2, quantum', 'calphy ts Einstein, classical', ...
    "config_entropy",   # 'none' | 'ideal' | 'sublattice' | 'mc' | 'liquid-ti' (what is already inside G)
    "quantum",          # 'quantum' | 'classical' | 'classical+harmonic-correction' | 'n/a'
    "n_atoms",          # atoms in the simulated cell (int, 0 if n/a)
    "source",           # file / job / AiiDA pk that produced the row
]

_REQUIRED = ["phase", "kind", "x", "T", "P_GPa", "G"]
_DEFAULTS = {
    "G_err": 0.0, "V": np.nan, "model": "", "reference_state": "", "method": "",
    "config_entropy": "none", "quantum": "n/a", "n_atoms": 0, "source": "",
}


@dataclass
class FreeEnergyTable:
    """Thin wrapper around a pandas DataFrame with the COLUMNS schema."""

    df: pd.DataFrame
    meta: Dict = field(default_factory=dict)

    # -- construction ------------------------------------------------------
    @classmethod
    def from_rows(cls, rows: Iterable[Dict], meta: Optional[Dict] = None):
        df = pd.DataFrame(list(rows))
        return cls(cls._normalise(df), dict(meta or {}))

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, meta: Optional[Dict] = None):
        return cls(cls._normalise(df.copy()), dict(meta or {}))

    @staticmethod
    def _normalise(df: pd.DataFrame) -> pd.DataFrame:
        missing = [c for c in _REQUIRED if c not in df.columns]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        for c, v in _DEFAULTS.items():
            if c not in df.columns:
                df[c] = v
        df = df[COLUMNS].copy()
        df["x"] = df["x"].astype(float)
        df["T"] = df["T"].astype(float)
        df["P_GPa"] = df["P_GPa"].astype(float)
        df["G"] = df["G"].astype(float)
        df["G_err"] = df["G_err"].astype(float)
        bad = ~df["kind"].isin(["solution", "point", "limited"])
        if bad.any():
            raise ValueError(f"kind must be solution/point/limited, got {sorted(df.loc[bad, 'kind'].unique())}")
        if ((df["x"] < -1e-12) | (df["x"] > 1 + 1e-12)).any():
            raise ValueError("x outside [0,1]")
        return df.sort_values(["phase", "T", "x"]).reset_index(drop=True)

    # -- checks ------------------------------------------------------------
    def check(self, require_same_pressure: bool = True) -> List[str]:
        """Return a list of problems (empty = consistent)."""
        p = []
        if require_same_pressure and self.df["P_GPa"].nunique() > 1:
            p.append(f"mixed pressures: {sorted(self.df['P_GPa'].unique())}")
        rs = self.df["reference_state"].replace("", np.nan).dropna().unique()
        if len(rs) > 1:
            p.append(f"mixed reference states: {list(rs)}")
        if (self.df["reference_state"] == "").any():
            p.append("rows without reference_state")
        q = set(self.df["quantum"].unique()) - {"n/a"}
        if len(q) > 1:
            p.append(f"mixed quantum/classical treatment: {sorted(q)} (see ftphase.quantum)")
        for ph, g in self.df.groupby("phase"):
            if g["kind"].nunique() > 1:
                p.append(f"phase {ph} has mixed kinds {sorted(g['kind'].unique())}")
            if g["kind"].iloc[0] == "point" and g["x"].nunique() > 1:
                p.append(f"point phase {ph} has several compositions {sorted(g['x'].unique())}")
            if g["config_entropy"].nunique() > 1:
                p.append(f"phase {ph} mixes config_entropy flags {sorted(g['config_entropy'].unique())}")
        return p

    # -- io ----------------------------------------------------------------
    def to_tsv(self, path):
        self.df.to_csv(path, sep="\t", index=False)
        with open(str(path) + ".meta.json", "w") as f:
            json.dump(self.meta, f, indent=1, ensure_ascii=False, default=str)

    @classmethod
    def from_tsv(cls, path):
        df = pd.read_csv(path, sep="\t")
        meta = {}
        try:
            with open(str(path) + ".meta.json") as f:
                meta = json.load(f)
        except FileNotFoundError:
            pass
        return cls(cls._normalise(df), meta)

    def to_parquet(self, path):
        self.df.to_parquet(path, index=False)

    @classmethod
    def from_parquet(cls, path):
        return cls(cls._normalise(pd.read_parquet(path)))

    # -- helpers -----------------------------------------------------------
    def phases(self) -> List[str]:
        return list(dict.fromkeys(self.df["phase"]))

    def temperatures(self) -> np.ndarray:
        return np.sort(self.df["T"].unique())

    def subset(self, **eq) -> "FreeEnergyTable":
        m = np.ones(len(self.df), dtype=bool)
        for k, v in eq.items():
            m &= (self.df[k] == v).to_numpy()
        return FreeEnergyTable(self.df.loc[m].reset_index(drop=True), self.meta)

    def concat(self, other: "FreeEnergyTable") -> "FreeEnergyTable":
        return FreeEnergyTable(self._normalise(pd.concat([self.df, other.df], ignore_index=True)), {**self.meta, **other.meta})

    def __len__(self):
        return len(self.df)
