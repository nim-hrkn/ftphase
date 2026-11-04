#!/usr/bin/env python
"""Compare the stage-07 outputs of the ftphase WorkChain runs with ORCHID v2026.10.

Two comparisons, both in the spirit of Arróyave, Saal & Shin, arXiv:2610.41164:

* ``07_two_phase_regions.tsv`` vs ORCHID-Assemblages (10.5281/zenodo.23735996):
  for every assessed-diagram field point (T, x, phases) of the system that lies
  inside the run's T grid and composition coverage, the stable assemblage of the
  run is read off the tie-lines at the nearest grid temperature and compared with
  the observed one.  Score = prevalence-weighted phase recall
  S = sum_p n_p R_p / sum_p n_p (paper, section 4.2), plus precision and the
  fraction of exact field matches.
* ``07_invariants.tsv`` vs the ORCHID-Values invariant-reaction records
  (10.5281/zenodo.23735569): our invariants are identified by the set of phases
  whose two-phase pairs change across the bracket; literature records with the
  same phase set are collected (experimental / model class kept apart) and
  dT = T_run - median(T_experimental) is reported.

Usage::

    env/ftphase/bin/python -I ftphase/examples/aiida_txdiagram/orchid_compare.py \
        [--data data/orchid-v2026.10] [--out out/orchid_compare] [run_dir ...]

Without run directories every ``out/*/07_two_phase_regions.tsv`` except smoke
runs is used.  Writes ``REPORT.md``, ``assemblage_points.tsv`` and
``invariants.tsv`` into ``--out``.
"""
from __future__ import annotations

import argparse
import ast
import csv
import glob
import gzip
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# run-name prefix -> (ORCHID system, x component used by our tables)
SYSTEMS = {
    "alli": ("AL-LI", "Li"),
    "nial": ("AL-NI", "Ni"),
    "agcu": ("AG-CU", "Cu"),
    "cuzr": ("CU-ZR", "Zr"),
}

# ORCHID phase names (TDB model phases and printed labels) -> our phase names.
# "fcc?" is resolved by composition / companions for Al-Ni (two fcc terminals).
PHASE_MAP = {
    "AL-LI": {
        "FCC_A1": "fcc", "A1_FCC": "fcc", "(Al)": "fcc", "fcc(Al)": "fcc", "(αAl)": "fcc",
        "BCC_4SL": "B32", "AlLi": "B32", "ALLI": "B32", "AlLi (B32)": "B32",
        "LIQUID": "liquid", "L": "liquid", "Liquid": "liquid",
        "AL2LI3": "Al2Li3", "Al2Li3": "Al2Li3",
        "AL4LI9": "Al4Li9", "Al4Li9": "Al4Li9", "αAl4Li9": "Al4Li9", "βAl4Li9": "Al4Li9",
        "BCC_A2": "bccLi", "A2_BCC": "bccLi", "(Li)": "bccLi", "(βLi)": "bccLi", "bcc(Li)": "bccLi",
        "ALLI2": "AlLi2", "AlLi2": "AlLi2",
        "AL3LI": "Al3Li", "Al3Li": "Al3Li",
    },
    "AL-NI": {
        "FCC_A1": "fcc?", "A1_FCC": "fcc?", "fcc": "fcc?", "γ": "fccNi", "(Ni)": "fccNi", "(Al)": "fccAl",
        "L12_FCC": "L12", "ALNI3_L12": "L12", "FCC_4SL": "L12", "AlNi3": "L12", "ALNI3": "L12",
        "γ'": "L12", "y'": "L12", "Ni3Al": "L12", "L12": "L12",
        "B2_BCC": "B2", "BCC_B2": "B2", "BCC_A2": "B2", "A2_BCC": "B2", "bcc": "B2", "B2": "B2",
        "AlNi": "B2", "NiAl": "B2",
        "AL3NI_D011": "NiAl3", "AL3NI": "NiAl3", "Al3Ni": "NiAl3", "NiAl3": "NiAl3",
        "AL3NI2_D513": "Ni2Al3", "AL3NI2": "Ni2Al3", "Al3Ni2": "Ni2Al3", "Ni2Al3": "Ni2Al3",
        "AL3NI5": "Al3Ni5", "Al3Ni5": "Al3Ni5", "Ni5Al3": "Al3Ni5",
        "AL4NI3": "Al4Ni3", "Al4Ni3": "Al4Ni3",
        "LIQUID": "liquid", "L": "liquid", "Liquid": "liquid",
    },
    "AG-CU": {
        "FCC_A1": "fcc", "A1_FCC": "fcc", "(Ag)": "fcc", "(Cu)": "fcc", "fcc": "fcc",
        "LIQUID": "liquid", "L": "liquid", "Liquid": "liquid",
    },
    "CU-ZR": {
        "FCC_A1": "fccCu", "(Cu)": "fccCu", "BCC_A2": "bccZr", "(βZr)": "bccZr", "HCP_A3": "hcpZr",
        "(αZr)": "hcpZr", "LIQUID": "liquid", "L": "liquid",
        "CUZR_B2": "B2", "CuZr": "B2", "CUZR2": "CuZr2", "CUZR2_HT": "CuZr2", "αCuZr2": "CuZr2",
        "βCuZr2": "CuZr2", "CU10ZR7": "Cu10Zr7", "CU8ZR3": "Cu8Zr3", "CU51ZR14": "Cu51Zr14",
        "Cu51Zr14": "Cu51Zr14", "CU5ZR_C15B": "Cu5Zr", "CU9ZR2_C15B": "Cu5Zr", "CU24ZR13": "Cu24Zr13",
        "CU2ZR": "Cu2Zr", "CU5ZR8": "Cu5Zr8", "Cu5Zr8": "Cu5Zr8",
    },
}

# Phases that NiAl3-side fcc companions imply (Al-Ni only).
AL_SIDE = {"NiAl3", "Ni2Al3"}
NI_SIDE = {"L12", "Al3Ni5"}


# --------------------------------------------------------------------------- ORCHID
def load_assemblages(data_root, system):
    path = os.path.join(
        data_root, "assessed-phase-assemblages", "orchid-assessed-phase-assemblages-v2026.10",
        "assessed-phase-assemblages", "records.jsonl.gz")
    out = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("system") == system:
                out.append(rec)
    return out


def load_literature(data_root, system):
    path = os.path.join(
        data_root, "literature", "orchid-literature-v2026.10", "literature", "systems",
        system + ".json")
    if not os.path.exists(path):
        return []
    return json.load(open(path))["records"]


def map_phase(system, label, model_phase=None, x_phase=None, companions=()):
    """Return (our_name, represented_literally). Unknown names are kept as '?label'."""
    table = PHASE_MAP[system]
    name = None
    for key in (model_phase, label):
        if key is not None and key in table:
            name = table[key]
            break
    if name is None:
        return "?" + str(label if label is not None else model_phase)
    if name == "fcc?":
        if x_phase is not None:
            return "fccNi" if x_phase > 0.5 else "fccAl"
        comp = set(companions)
        if comp & AL_SIDE:
            return "fccAl"
        if comp & NI_SIDE:
            return "fccNi"
        return "fcc?"
    return name


def observed_assemblage(system, rec):
    names = []
    for ph in rec["assemblage"]:
        names.append(map_phase(system, ph.get("label"), ph.get("canonical_name"),
                               companions=[p.get("label") for p in rec["assemblage"]]))
    # resolve remaining fcc? by the point's composition
    names = [("fccNi" if rec["x"] > 0.5 else "fccAl") if n == "fcc?" else n for n in names]
    return sorted(names)


def multiset_key(names):
    """Hashable multiset of phase names (duplicates kept, e.g. Ag-Cu fcc+fcc+liquid)."""
    return tuple(sorted(names))


def literature_invariants(system, records, xcomp):
    """Group accepted INVARIANT_TEMPERATURE (and two-phase TRANSITION_TEMPERATURE =
    congruent melting) records by the multiset of mapped phase names."""
    groups = defaultdict(list)
    elems = system.split("-")
    other = [e for e in elems if e.upper() != xcomp.upper()]
    for r in records:
        if r.get("property") not in ("INVARIANT_TEMPERATURE", "TRANSITION_TEMPERATURE"):
            continue
        if not r.get("flags", {}).get("extraction_accepted", False):
            continue
        phases = r.get("phases") or []
        if len(phases) < 2:
            continue
        comps = {}
        for pc in r.get("phase_compositions") or []:
            try:
                comp = pc["composition"]
                key = list(comp.keys())[0]
                x = float(comp[key])
                if key.upper() != xcomp.upper():
                    if other and key.upper() == other[0].upper():
                        x = 1.0 - x
                    else:
                        continue
                comps[pc["phase"]] = x
            except Exception:
                pass
        labels = [p.get("label") for p in phases]
        mapped = [map_phase(system, p.get("label"), p.get("model_phase"), comps.get(p.get("label")), labels)
                  for p in phases]
        # unresolved fcc? in Al-Ni: use companions of the mapped set
        if "fcc?" in mapped:
            others = set(mapped) - {"fcc?"}
            side = "fccAl" if others & AL_SIDE else ("fccNi" if others & NI_SIDE else "fcc?")
            mapped = [side if m == "fcc?" else m for m in mapped]
        key = multiset_key(mapped)
        T = r.get("temperature_K")
        if T is None and r.get("unit") == "K":
            T = r.get("value")
        if T is None:
            continue
        groups[key].append({
            "T": float(T),
            "class": r.get("evidence_class"),
            "property": r.get("property"),
            "plaus": (r.get("flags", {}).get("plausibility") or {}).get("result"),
            "reaction": (r.get("reaction") or {}).get("printed"),
            "paper": r.get("paper"),
            "cited": "; ".join(c.get("reference", "") for c in r.get("cited_sources") or []),
            "comps": comps,
            "labels": labels,
            "id": r.get("id"),
        })
    return groups


def unary_melting(data_root, element):
    """Accepted TRANSITION_TEMPERATURE records of the unary system that name a liquid phase."""
    recs = load_literature(data_root, element.upper())
    out = []
    for r in recs:
        if r.get("property") != "TRANSITION_TEMPERATURE" or not r.get("flags", {}).get("extraction_accepted"):
            continue
        labels = [str(p.get("label", "")) for p in r.get("phases") or []]
        if len(labels) < 2 or not any(l == "L" or "(l)" in l.lower() or "liq" in l.lower() for l in labels):
            continue
        out.append((float(r.get("temperature_K") or r.get("value")), r.get("evidence_class"), r.get("paper")))
    return out


# --------------------------------------------------------------------------- our runs
def load_run(run_dir):
    rows = list(csv.DictReader(open(os.path.join(run_dir, "07_two_phase_regions.tsv")), delimiter="\t"))
    byT = defaultdict(list)
    for r in rows:
        byT[float(r["T"])].append((float(r["x_a"]), r["phase_a"], float(r["x_b"]), r["phase_b"]))
    for T in byT:
        byT[T].sort()
    inv = []
    p = os.path.join(run_dir, "07_invariants.tsv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p), delimiter="\t"):
            inv.append({
                "T_low": float(r["T_low"]), "T_high": float(r["T_high"]),
                "below": set(ast.literal_eval(r["pairs_below"])),
                "above": set(ast.literal_eval(r["pairs_above"])),
            })
    phases = sorted({r["phase_a"] for r in rows} | {r["phase_b"] for r in rows})
    xs = [float(r["x_a"]) for r in rows] + [float(r["x_b"]) for r in rows]
    summary = {}
    sp = os.path.join(run_dir, "summary.json")
    if os.path.exists(sp):
        summary = json.load(open(sp))
    Ts = sorted(byT)
    grid = summary.get("T_grid")
    if grid and len(grid) == 3:
        Tmin, Tmax, n = float(grid[0]), float(grid[1]), int(grid[2])
        step = (Tmax - Tmin) / (n - 1) if n > 1 else 10.0
    else:
        Tmin, Tmax = (Ts[0], Ts[-1]) if Ts else (0.0, 0.0)
        step = Ts[1] - Ts[0] if len(Ts) > 1 else 10.0
    return {"byT": byT, "inv": inv, "phases": phases, "xmin": min(xs), "xmax": max(xs), "summary": summary,
            "Tmin": Tmin, "Tmax": Tmax, "step": step}


def run_coverage(run):
    """Composition range the run's hull covers. Runs that stop near x=0.5 (Al-Li AiiDA runs)
    are detected from their largest tie-line end point."""
    xmax = run["xmax"]
    if xmax < 0.6:
        return 0.0, xmax + 0.01
    return 0.0, 1.0


def predicted_assemblage(run, T, x, tol_line=0.005):
    Ts = sorted(run["byT"])
    step = run["step"]
    if T < run["Tmin"] - step / 2 or T > run["Tmax"] + step / 2:
        return None, "outside_T"
    xlo, xhi = run_coverage(run)
    if x < xlo or x > xhi:
        return None, "outside_x"
    if T > Ts[-1] + step / 2:
        # inside the grid but above the last tie-line: everything is liquid there
        return ["liquid"], f"T>{Ts[-1]:.0f} (no tie-lines left)"
    Tg = min(Ts, key=lambda t: abs(t - T))
    lines = run["byT"][Tg]
    for xa, pa, xb, pb in lines:
        if abs(xa - xb) < 1e-9:
            continue
        if xa - tol_line <= x <= xb + tol_line:
            if abs(x - xa) <= tol_line and pa != pb:
                return sorted([pa]), f"T_grid={Tg:.0f}"
            if abs(x - xb) <= tol_line and pa != pb:
                return sorted([pb]), f"T_grid={Tg:.0f}"
            return sorted([pa, pb]), f"T_grid={Tg:.0f}"
    # single-phase: between tie-lines
    prev_b, next_a = None, None
    for xa, pa, xb, pb in lines:
        if xb < x:
            prev_b = pb
        if xa > x and next_a is None:
            next_a = pa
    if prev_b is None and next_a is None:
        return None, "no_tie_lines"
    if prev_b is None:
        return [next_a], f"T_grid={Tg:.0f}"
    if next_a is None or next_a == prev_b:
        return [prev_b], f"T_grid={Tg:.0f}"
    return [prev_b], f"T_grid={Tg:.0f};ambiguous({prev_b}|{next_a})"


def invariant_phase_set(inv):
    """Multiset of phases taking part in the change across the bracket.

    A pair "p+p" (two regions of the same phase, e.g. the Ag-Cu fcc miscibility gap)
    counts phase p twice, so the Ag-Cu eutectic becomes (fcc, fcc, liquid).  Returns
    (multiset tuple, changed pairs, kind) with kind in
    artefact (one phase only: a same-phase segment appears or vanishes),
    melting (solid+liquid where the solid is absent above the bracket),
    liquid_reaches (solid+liquid with the solid still present above: the liquid
    first touches that solid, no reaction identified), reaction (3+ phases).
    """
    changed = inv["below"] ^ inv["above"]
    mult = Counter()
    for pair in changed:
        a, b = pair.split("+")
        if a == b:
            mult[a] = max(mult[a], 2)
        else:
            mult[a] = max(mult[a], 1)
            mult[b] = max(mult[b], 1)
    names = list(mult.elements())
    phases_above = set()
    for pair in inv["above"]:
        phases_above.update(pair.split("+"))
    if len(set(names)) == 1:
        kind = "artefact"
    elif len(names) == 2 and "liquid" in names:
        solid = [n for n in names if n != "liquid"][0]
        kind = "melting" if solid not in phases_above else "liquid_reaches"
    elif len(names) >= 3:
        kind = "reaction"
    else:
        kind = "other"
    return multiset_key(names), changed, kind


def invariant_compositions(run, inv, phases, changed):
    comps = defaultdict(list)
    for T in (inv["T_low"], inv["T_high"]):
        for xa, pa, xb, pb in run["byT"].get(T, []):
            pair = "+".join(sorted([pa, pb]))
            pair2 = pa + "+" + pb
            if pair in changed or pair2 in changed or (pb + "+" + pa) in changed:
                comps[pa].append(xa)
                comps[pb].append(xb)
    return {p: statistics.mean(v) for p, v in comps.items() if v}


# --------------------------------------------------------------------------- scoring
def score_points(rows):
    """rows: list of dicts with observed (list) and predicted (list or None)."""
    ev = [r for r in rows if r["predicted"] is not None]
    n_obs = Counter()
    hit = Counter()
    n_pred = 0
    n_pred_ok = 0
    exact = 0
    for r in ev:
        obs = Counter(r["observed"])
        pred = Counter(r["predicted"])
        if obs == pred:
            exact += 1
        for p, n in obs.items():
            n_obs[p] += n
            hit[p] += min(n, pred.get(p, 0))
        for p, n in pred.items():
            n_pred += n
            n_pred_ok += min(n, obs.get(p, 0))
    tot = sum(n_obs.values())
    S = sum(hit.values()) / tot if tot else float("nan")
    P = n_pred_ok / n_pred if n_pred else float("nan")
    return {"n_points": len(rows), "n_evaluable": len(ev), "exact": exact, "recall_S": S,
            "precision": P, "per_phase": {p: (hit[p], n_obs[p]) for p in sorted(n_obs)}}


# --------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="*", help="run output directories (default: out/* without smoke)")
    ap.add_argument("--data", default=os.path.join(ROOT, "data", "orchid-v2026.10"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "orchid_compare"))
    ap.add_argument("--include-smoke", action="store_true")
    args = ap.parse_args(argv)

    runs = args.runs
    if not runs:
        runs = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(HERE, "out", "*", "07_two_phase_regions.tsv")))
        if not args.include_smoke:
            runs = [r for r in runs if "smoke" not in os.path.basename(r)]
    os.makedirs(args.out, exist_ok=True)

    cache = {}
    point_rows, inv_rows, report = [], [], []
    report.append("# ORCHID v2026.10 との比較（stage 07 の出力）\n")
    report.append("データ: ORCHID-Assemblages 10.5281/zenodo.23735996（評価状態図の相領域内部点）、"
                  "ORCHID-Values 10.5281/zenodo.23735569（文献の不変反応温度）。"
                  "論文 arXiv:2610.41164 の §4.2 と同じ prevalence-weighted phase recall "
                  "S = Σ n_p R_p / Σ n_p を各 run の T 格子と組成範囲に入る点だけで計算した。"
                  "exact は相集合（多重集合）が完全一致した点の数。precision は予測した相のうち観測された相の割合。"
                  "不変反応は、括弧 [T_low, T_high] の前後で変わる二相対に含まれる相の多重集合で同定し"
                  "（同相対 p+p は p を 2 回数える: Ag-Cu の共晶は fcc+fcc+liquid）、"
                  "kind = reaction（3 相以上）と melting（固相+液相で、その固相が括弧の上で消える = 合致溶融）だけを、"
                  "同じ多重集合を持つ ORCHID の記録（INVARIANT_TEMPERATURE と 2 相の TRANSITION_TEMPERATURE、extraction_accepted）と照合した。"
                  "dT_exp = T_run − median(experimental)。model は評価（CALPHAD）由来の値で参考。"
                  "partial は、文献の相集合が我々の相集合に加えてモデルに無い相を含む場合（組成範囲や相の欠落による切り詰め）。"
                  "x_run は括弧の上下の二相対端点の平均、x_lit は文献の印刷組成の中央値。\n")
    per_system = defaultdict(list)

    for run_dir in runs:
        name = os.path.basename(run_dir.rstrip("/"))
        prefix = name.split("_")[0]
        if prefix not in SYSTEMS:
            print(f"skip {name}: unknown system prefix", file=sys.stderr)
            continue
        system, xcomp = SYSTEMS[prefix]
        try:
            run = load_run(run_dir)
        except Exception as exc:  # empty files etc.
            print(f"skip {name}: {exc}", file=sys.stderr)
            continue
        if not run["byT"]:
            print(f"skip {name}: no tie-lines", file=sys.stderr)
            continue
        if system not in cache:
            elem_a = system.split("-")[0] if system.split("-")[0].upper() != xcomp.upper() else system.split("-")[1]
            cache[system] = (load_assemblages(args.data, system),
                             literature_invariants(system, load_literature(args.data, system), xcomp),
                             unary_melting(args.data, elem_a), elem_a)
        asm, litinv, melt_lit, elem_a = cache[system]
        vocab = set(run["phases"])

        # ---- assemblage points
        rows = []
        for rec in sorted(asm, key=lambda r: (r["T_K"], r["x"])):
            if rec.get("x_component") != xcomp:
                x = 1.0 - rec["x"]
            else:
                x = rec["x"]
            obs = observed_assemblage(system, rec)
            pred, note = predicted_assemblage(run, rec["T_K"], x)
            unrep = sorted(p for p in obs if p not in vocab)
            rows.append({"run": name, "system": system, "id": rec["id"], "T_K": rec["T_K"], "x": x,
                         "observed": obs, "predicted": pred, "note": note,
                         "unrepresented": unrep, "confidence": rec.get("confidence"),
                         "field_label": rec.get("assemblage_label")})
        sc = score_points(rows)
        rows_rep = [dict(r, predicted=(r["predicted"] if not r["unrepresented"] else None)) for r in rows]
        sc_rep = score_points(rows_rep)
        point_rows.extend(rows)

        # ---- invariants
        inv_out = []
        matched_keys = set()
        for inv in run["inv"]:
            pset, changed, kind = invariant_phase_set(inv)
            comps = invariant_compositions(run, inv, pset, changed)
            T_run = 0.5 * (inv["T_low"] + inv["T_high"])
            lit = None
            status = {"artefact": "same-phase segment appears/vanishes (fit noise), not compared",
                      "liquid_reaches": "liquid first touches this solid here (no reaction identified), not compared",
                      "other": "not compared"}.get(kind, "no literature record with this phase set")
            Texp = Tmod = None
            nexp = nmod = 0
            exp = []
            if kind in ("melting", "reaction"):
                lit = litinv.get(pset)
                if lit is not None:
                    matched_keys.add(pset)
                    status = "matched"
                elif kind == "reaction":
                    # partial: the literature multiset contains ours plus phases we do not represent
                    cnt = Counter(pset)
                    for key, recs in litinv.items():
                        kc = Counter(key)
                        extra = kc - cnt
                        if cnt <= kc and extra and all(p not in vocab for p in extra):
                            lit = recs
                            status = "partial: literature set also has " + ",".join(sorted(extra.elements()))
                            matched_keys.add(key)
                            break
            if lit:
                exp = [r["T"] for r in lit if r["class"] == "experimental"]
                mod = [r["T"] for r in lit if r["class"] == "model"]
                nexp, nmod = len(exp), len(mod)
                Texp = statistics.median(exp) if exp else None
                Tmod = statistics.median(mod) if mod else None
            inv_out.append({"run": name, "system": system, "T_low": inv["T_low"], "T_high": inv["T_high"],
                            "T_run": T_run, "kind": kind, "phases": "+".join(pset),
                            "x_run": {p: round(v, 3) for p, v in comps.items()},
                            "n_exp": nexp, "T_exp_median": Texp, "T_exp_range": (min(exp), max(exp)) if exp else None,
                            "n_model": nmod, "T_model_median": Tmod,
                            "dT_exp": (T_run - Texp) if Texp is not None else None,
                            "status": status,
                            "x_lit": _lit_comps(lit) if lit else None})
        inv_rows.extend(inv_out)
        # literature invariants we did not produce
        Ts = sorted(run["byT"])
        missed = []
        for key, recs in litinv.items():
            if key in matched_keys:
                continue
            exp = [r["T"] for r in recs if r["class"] == "experimental"]
            mod = [r["T"] for r in recs if r["class"] == "model"]
            Tl = statistics.median(exp) if exp else (statistics.median(mod) if mod else None)
            if Tl is None:
                continue
            represented = all(p in vocab for p in key)
            in_T = run["Tmin"] <= Tl <= run["Tmax"]
            missed.append((key, Tl, len(exp), len(mod), represented, in_T))

        # ---- pure-element melting
        melt = run["summary"].get("pure_A_melting_bracket_K")

        # ---- report section
        melt_txt = ""
        if melt and melt[0] >= run["Tmax"]:
            melt_txt = f"; 純 {elem_a} は格子上限 {run['Tmax']:.0f} K まで融けない"
            if melt_lit:
                melt_txt += f" (ORCHID unary {elem_a}: {statistics.median(T for T, _, _ in melt_lit):.1f} K)"
        elif melt:
            melt_txt = f"; 純 {elem_a} の融点括弧 {melt[0]:.0f}–{melt[1]:.0f} K"
            if melt_lit:
                vals = ", ".join(f"{T:.1f} ({cls[:4]})" for T, cls, _ in melt_lit)
                melt_txt += f" vs ORCHID unary {elem_a}: {vals}; dT = {0.5*(melt[0]+melt[1]) - statistics.median(T for T, _, _ in melt_lit):+.0f} K"
            else:
                melt_txt += f" (ORCHID unary {elem_a} に融点記録なし)"
        sec = [f"## {name}  ({system}, x = x_{xcomp})\n",
               f"相: {', '.join(run['phases'])}; T 格子 {run['Tmin']:.0f}–{run['Tmax']:.0f} K"
               f"（二相対は {Ts[0]:.0f}–{Ts[-1]:.0f} K）; 組成範囲 "
               f"{run_coverage(run)[0]:.2f}–{run_coverage(run)[1]:.2f}" + melt_txt + "\n",
               "### 相領域の内部点（ORCHID-Assemblages）\n",
               f"点 {sc['n_points']}、評価可能 {sc['n_evaluable']}（T 格子と組成範囲の内側）、exact {sc['exact']}、"
               f"S = {sc['recall_S']:.2f}、precision = {sc['precision']:.2f}"
               + (f"; 我々の相語彙にある相だけ: 評価可能 {sc_rep['n_evaluable']}, exact {sc_rep['exact']}, S = {sc_rep['recall_S']:.2f}"
                  if sc_rep["n_evaluable"] != sc["n_evaluable"] else "") + "\n",
               "| T_K | x | observed | predicted | note |", "|---|---|---|---|---|"]
        for r in rows:
            pred = "+".join(r["predicted"]) if r["predicted"] else "-"
            flag = ""
            if r["predicted"] is not None:
                flag = "OK" if Counter(r["predicted"]) == Counter(r["observed"]) else "x"
            if r["unrepresented"]:
                flag += " (not in model: " + ",".join(r["unrepresented"]) + ")"
            sec.append(f"| {r['T_K']:.0f} | {r['x']:.3f} | {'+'.join(r['observed'])} | {pred} | {r['note']} {flag} |")
        sec.append("")
        sec.append("### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）\n")
        if inv_out:
            sec += ["| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |",
                    "|---|---|---|---|---|---|---|---|---|---|---|"]
            for r in inv_out:
                Te = f"{r['T_exp_median']:.0f} ({r['T_exp_range'][0]:.0f}–{r['T_exp_range'][1]:.0f})" if r["T_exp_median"] is not None else "-"
                dT = f"{r['dT_exp']:+.0f}" if r["dT_exp"] is not None else "-"
                Tm = f"{r['T_model_median']:.0f}" if r["T_model_median"] is not None else "-"
                xl = json.dumps(r["x_lit"], ensure_ascii=False) if r["x_lit"] else "-"
                sec.append(f"| {r['T_low']:.0f}–{r['T_high']:.0f} | {r['kind']} | {r['phases']} | {json.dumps(r['x_run'])} | {r['n_exp']} | {Te} | {dT} | {r['n_model']} | {Tm} | {xl} | {r['status']} |")
        else:
            sec.append("run に不変反応なし（07_invariants.tsv が空）。")
        if missed:
            sec.append("\n文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:\n")
            for key, Tl, ne, nm, rep, inT in sorted(missed, key=lambda t: t[1]):
                sec.append(f"- {'+'.join(sorted(key))}: {Tl:.0f} K ({ne}/{nm}); represented={rep}; in_T_grid={inT}")
        sec.append("")
        report.extend(sec)
        per_system[system].append((name, sc, sc_rep, inv_out))

    # ---- overview table
    over = ["## 一覧\n", "| run | system | points evaluable/total | exact | S | precision | S (represented only) | invariants matched | dT_exp (K) |",
            "|---|---|---|---|---|---|---|---|---|"]
    for system, items in per_system.items():
        for name, sc, sc_rep, inv_out in items:
            dts = [f"{r['phases']}: {r['dT_exp']:+.0f}" for r in inv_out if r["dT_exp"] is not None]
            nm = sum(1 for r in inv_out if r["dT_exp"] is not None)
            ncmp = sum(1 for r in inv_out if r["kind"] in ("melting", "reaction"))
            over.append(f"| {name} | {system} | {sc['n_evaluable']}/{sc['n_points']} | {sc['exact']} | {sc['recall_S']:.2f} | "
                        f"{sc['precision']:.2f} | {sc_rep['recall_S']:.2f} | {nm}/{ncmp} | {'; '.join(dts) or '-'} |")
    over.append("")
    report = report[:2] + over + report[2:]

    with open(os.path.join(args.out, "REPORT.md"), "w") as fh:
        fh.write("\n".join(report) + "\n")
    with open(os.path.join(args.out, "assemblage_points.tsv"), "w") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["run", "system", "orchid_id", "T_K", "x", "observed", "predicted", "match", "note", "unrepresented", "confidence"])
        for r in point_rows:
            match = "" if r["predicted"] is None else ("exact" if Counter(r["predicted"]) == Counter(r["observed"]) else "differ")
            w.writerow([r["run"], r["system"], r["id"], f"{r['T_K']:.1f}", f"{r['x']:.4f}", "+".join(r["observed"]),
                        "+".join(r["predicted"]) if r["predicted"] else "", match, r["note"], ",".join(r["unrepresented"]), r["confidence"]])
    with open(os.path.join(args.out, "invariants.tsv"), "w") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["run", "system", "T_low", "T_high", "kind", "phases", "x_run", "n_exp", "T_exp_median", "T_exp_min", "T_exp_max",
                    "dT_exp", "n_model", "T_model_median", "x_lit", "status"])
        for r in inv_rows:
            w.writerow([r["run"], r["system"], r["T_low"], r["T_high"], r["kind"], r["phases"], json.dumps(r["x_run"]), r["n_exp"],
                        r["T_exp_median"] if r["T_exp_median"] is not None else "",
                        r["T_exp_range"][0] if r["T_exp_range"] else "", r["T_exp_range"][1] if r["T_exp_range"] else "",
                        f"{r['dT_exp']:.1f}" if r["dT_exp"] is not None else "", r["n_model"],
                        r["T_model_median"] if r["T_model_median"] is not None else "", json.dumps(r["x_lit"]), r["status"]])
    print("\n".join(over))
    print(f"written: {args.out}/REPORT.md, assemblage_points.tsv, invariants.tsv")


def _lit_comps(recs):
    """Median printed composition per phase label over the experimental records."""
    acc = defaultdict(list)
    for r in recs:
        if r["class"] != "experimental":
            continue
        for lab, x in r["comps"].items():
            acc[lab].append(x)
    return {lab: round(statistics.median(v), 3) for lab, v in acc.items()}


if __name__ == "__main__":
    main()
