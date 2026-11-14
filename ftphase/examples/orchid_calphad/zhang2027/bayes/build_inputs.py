"""Inputs for the Bayesian update of Zhang et al. 2027 Fig. 4b (Ru-Si, eSEN) with ESPEI's MCMC.

Parameters theta: for every compound and for the HCP L0, a shift dH (J per mole of atoms) and dS (J/K per mole of atoms):
G += n_sites * (dH - T dS)  (HCP: L0 += dH - T dS).  Liquid (taken from CPDDB by the authors) and the pure elements are fixed.
Prior (the paper's UMLIP-level uncertainty): dH ~ N(0, 1410 J/mol), dS ~ N(0, 1.73 J/mol/K), independent.
Data D: the three tie-lines marked in Fig. 4b = the Modified_CPDDB assessment at 1250 K (HCP + Ru4Si3), 1550 K (Ru2Si + Ru4Si3)
and 1900 K (liquid + RuSi); compositions computed here from that TDB.
Writes rusi-start.tdb (VV symbols = 0), phases.json, datasets/zpf_fig4b.json, prior.json, start_trace.npy (walkers drawn from
the prior) and mcmc.yaml.      env/pycalphad/bin/python build_inputs.py [--walkers 88] [--iterations 2000] [--cores 16]
"""
import argparse, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEP = os.path.abspath(os.path.join(HERE, "../../../../../data/Zhang2027/zenodo-phase-diagrams"))
SIGMA_H, SIGMA_S = 1410.0, 1.73
POINTS = [(1250.0, 0.20, ("HCP", "RU4SI3")), (1550.0, 0.38, ("RU2SI", "RU4SI3")), (1900.0, 0.44, ("LIQUID", "RUSI"))]


def site_counts(text):
    return {m.group(1).upper(): [float(v) for v in m.group(3).split()] for m in re.finditer(r"^\s*PHASE\s+(\w+)\s+%\s+(\d+)\s+([\d.\s]+)!", text, re.M)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", default="eSEN-uma-s-1p1"); ap.add_argument("--walkers", type=int, default=88)
    ap.add_argument("--iterations", type=int, default=2000); ap.add_argument("--cores", type=int, default=16); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    text = open(os.path.join(DEP, a.model, "Ru-Si.tdb")).read(); sc = site_counts(text); lines = text.split("\n"); params = []
    for i, l in enumerate(lines):
        m = re.match(r"\s*PARAMETER\s+([GL])\((\w+),([^;]+);(\d)\)", l)
        if not m:
            continue
        ph, sub = m.group(2).upper(), m.group(3)
        if ph == "HCP" and "," in sub and m.group(4) == "0":
            mult = 1.0
        elif ph not in ("LIQUID", "HCP", "SI") and "," not in sub and ph in sc:
            mult = sum(sc[ph])
        else:
            continue
        k = len(params); vh, vs = f"VV{2 * k:04d}", f"VV{2 * k + 1:04d}"
        lines[i] = re.sub(r";(\s*\d+(?:\.\d+)?\s+N\s*!)", f"+{mult:g}*{vh}-{mult:g}*{vs}*T;\\1", l, count=1)
        params.append({"phase": ph, "mult": mult, "dH": vh, "dS": vs})
    funcs = "\n".join(f"FUNCTION {p[k]} 1 0.0; 6000 N !" for p in params for k in ("dH", "dS"))
    idx = next(i for i, l in enumerate(lines) if l.startswith("FUNCTION"))
    lines.insert(idx, "$ fitting symbols: dH (J per mole of atoms) and dS (J/K per mole of atoms) shifts, see build_inputs.py\n" + funcs + "\n")
    open(os.path.join(HERE, "rusi-start.tdb"), "w").write("\n".join(lines))
    # phase models for ESPEI
    cons = {m.group(1).upper(): [s.strip().upper().split(",") for s in m.group(2).strip(": ").split(":")] for m in re.finditer(r"^\s*CONSTITUENT\s+(\w+)\s*:(.*?):\s*!", text, re.M)}
    pm = {"components": ["RU", "SI"], "phases": {ph: {"sublattice_model": cons[ph], "sublattice_site_ratios": sc[ph]} for ph in sc}}
    json.dump(pm, open(os.path.join(HERE, "phases.json"), "w"), indent=1)
    # the three tie-lines from the assessment
    from pycalphad import Database, equilibrium, variables as v
    ref = Database(os.path.join(DEP, "Modified_CPDDB", "Ru-Si.tdb")); values = []; temps = []
    for T, x, expect in POINTS:
        eq = equilibrium(ref, ["RU", "SI"], list(ref.phases), {v.X("SI"): x, v.T: T, v.P: 101325, v.N: 1})
        ph = [str(p) for p in eq.Phase.values.ravel() if p]; xs = [float(q) for q in eq.X.sel(component="SI").values.ravel()[:len(ph)]]
        assert tuple(sorted(ph)) == tuple(sorted(expect)), (T, ph)
        # line compounds: composition null (ESPEI then takes the phase's own composition); a __HYPERPLANE__ vertex in the middle of the
        # tie-line defines the target chemical potentials (equilibrium with ALL phases of the model there): without it a tie-line
        # between two line compounds has an undetermined hyperplane and ESPEI silently gives it zero weight
        stoich = lambda p: all(len(c) == 1 for c in cons[p])
        temps.append(T); values.append([["__HYPERPLANE__", ["SI"], [round(float(np.mean(xs)), 4)]]] + [[p, ["SI"], [None if stoich(p) else round(q, 6)]] for p, q in zip(ph, xs)])
        print("tie-line", T, values[-1])
    os.makedirs(os.path.join(HERE, "datasets"), exist_ok=True)
    json.dump({"components": ["RU", "SI"], "phases": sorted({p for _, _, e in POINTS for p in e}), "conditions": {"P": 101325, "T": temps}, "output": "ZPF", "values": values,
               "reference": "Zhang2027 Fig. 4b reference points = Modified_CPDDB Ru-Si assessment", "comment": "three tie-lines at 1250, 1550, 1900 K"},
              open(os.path.join(HERE, "datasets", "zpf_fig4b.json"), "w"), indent=1)
    names = [p[k] for p in params for k in ("dH", "dS")]; sig = np.array([SIGMA_H, SIGMA_S] * len(params))
    prior = [{"name": "normal", "loc_absolute": 0.0, "scale_absolute": float(s)} for s in sig]
    json.dump({"params": params, "symbols": names, "sigma": sig.tolist()}, open(os.path.join(HERE, "prior.json"), "w"), indent=1)
    rng = np.random.default_rng(a.seed); assert a.walkers >= 2 * len(names) and a.walkers % 2 == 0
    np.save(os.path.join(HERE, "start_trace.npy"), (rng.normal(0, 1, (a.walkers, 1, len(names))) * sig))
    import yaml
    cfg = {"system": {"phase_models": "phases.json", "datasets": "datasets"},
           "mcmc": {"iterations": a.iterations, "save_interval": 20, "input_db": "rusi-start.tdb", "scheduler": "dask", "cores": a.cores, "restart_trace": "start_trace.npy",
                    "prior": prior, "symbols": names},
           "output": {"output_db": "rusi-mcmc.tdb", "tracefile": "trace.npy", "probfile": "lnprob.npy", "verbosity": 1, "logfile": "mcmc.log"}}
    yaml.safe_dump(cfg, open(os.path.join(HERE, "mcmc.yaml"), "w"), sort_keys=False)
    print(len(params), "phases ->", len(names), "parameters;", a.walkers, "walkers x", a.iterations, "iterations")


if __name__ == "__main__":
    main()
