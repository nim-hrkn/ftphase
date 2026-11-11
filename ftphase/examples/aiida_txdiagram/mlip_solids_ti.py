"""Ni-Al / Ag-Cu MLIP runs (QHA solids, 2026-10-30): calphy solid TI (>= 2000-atom cells) of the melting-point cells,
because QHA puts the melting points of several MLIPs far off (GRACE-FS / SevenNet-0 fcc Al: S_solid > S_liquid at
1000 K).  Stage 1 (user decision 2026-10-31): only the pure / stoichiometric cells (fcc Al, fcc Ni, B2 NiAl, L1_2
Ni3Al; fcc Ag, fcc Cu), one CalphyCalculation each, on the calphy code of the original WorkChain.

    python mlip_solids_ti.py submit                 all six WorkChains (records out/<name>/solids_ti.json)
    python mlip_solids_ti.py submit --names nial_grace_fs --only s00_fccAl --T-lo s00_fccAl=500 --T-hi s00_fccAl=860
    python mlip_solids_ti.py submit2 [--dry]        stage 2 (2026-11-01): every alloy cell, sweep caps from the stage-1 melting points
    python mlip_solids_ti.py liqlow [--dry]         Ag-Cu liquids from (old lowest T + 100 K) down to 750 K (records out/<name>/liquids_low.json)
    python mlip_solids_ti.py status
    python mlip_solids_ti.py melt                   solid(TI)-liquid crossings -> out/mlip_compare_nial_agcu/melting_ti.tsv
    python mlip_solids_ti.py assemble [--names ..]  assemble_diagram with the TI sweeps -> out/<name>_ti/
"""

import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
MIN_ATOMS = 2000
RUNS = {"nial_grace_fs": 4784, "nial_grace_1l": 4798, "nial_sevenn_0": 4813, "agcu_grace_fs": 4869, "agcu_grace_1l": 4900, "agcu_sevenn_0": 4928,
        "ptrh_grace_2l": 9105, "ptrh_nequip_oam_m": 9348, "ptrh_mace_mpa_0": 9585, "ptrh_sevenn_mf_ompa": 10792,
        "nial_grace_1l_b2ext_solid": 15488}   # 2026-11-11 B2 extended defect sampling (vacancies 4-7, anti-sites 8-10), solids only   # Pt-Rh (2026-11-06): pure-end fcc cells only, 4x4x4 of 32 = 2048 atoms
#: (phase, x) -> sweep [T_lo, T_hi]; T_hi about 1.05 T_m(expt).  The first try with 1.2 T_m (pk 6503-6595) failed: GRACE-FS
#: fcc Al melted at ~1000 K on the way to 1150 K (MeltedError, pk 6503), so the MLIP melting points are near the experimental
#: ones and a superheated cell does not survive 1.2 T_m.  A crossing above T_hi is reported as "> T_hi" plus a linear extrapolation.
CELLS = {"nial": {("fccAl", 0.0): [600.0, 920.0], ("fccNi", 1.0): [1200.0, 1800.0], ("B2", 0.5): [1300.0, 2000.0], ("L12", 0.75): [1200.0, 1750.0]},
         "agcu": {("fcc", 0.0): [800.0, 1250.0], ("fcc", 1.0): [900.0, 1420.0]},
         "ptrh": {("fcc", 0.0): [1700.0, 2150.0], ("fcc", 1.0): [1900.0, 2350.0]}}   # Pt 2041 K, Rh 2237 K (expt); caps ~1.05 T_m
EXPT = {("nial", "fccAl", 0.0): 933, ("nial", "fccNi", 1.0): 1728, ("nial", "B2", 0.5): 1911, ("nial", "L12", 0.75): 1645, ("agcu", "fcc", 0.0): 1235, ("agcu", "fcc", 1.0): 1358, ("ptrh", "fcc", 0.0): 2041, ("ptrh", "fcc", 1.0): 2237}


def _workchain(pk):
    from aiida import orm

    wc = orm.load_node(pk)
    kids = {}
    for link in wc.base.links.get_outgoing(node_class=orm.ProcessNode).all():
        kids.setdefault(link.node.process_label, []).append(link.node)
    prep = [n for n in kids.get("prepare_cells", []) if n.is_finished_ok][0]
    return wc, kids, prep


def _rec_path(name):
    return os.path.join(OUT, name, "solids_ti.json")


def submit(names, only=None, t_hi=None, t_lo=None):
    from aiida import orm
    from aiida.engine import submit as aiida_submit
    from aiida.plugins import CalculationFactory

    from ftphase.aiida.functions import repeat_structure

    Calphy = CalculationFactory("ftphase.calphy")
    for name in names:
        wc, kids, prep = _workchain(RUNS[name])
        sp = wc.inputs.spec.get_dict(); sol_p = prep.outputs.solid_params.get_dict()
        extra = wc.inputs.calphy_extra.get_dict() if "calphy_extra" in wc.inputs else {}
        rec = json.load(open(_rec_path(name))) if os.path.exists(_rec_path(name)) else {"pk_workchain": RUNS[name], "jobs": {}}
        done = set()
        for key, m in sorted(sol_p.items()):
            cell = next((c for c in CELLS[name[:4]] if c[0] == m["phase"] and abs(c[1] - m["x"]) < 1e-6), None)
            if cell is None or cell in done or (only and key not in only) or (not only and key in rec["jobs"]):
                continue
            done.add(cell)
            structure = prep.outputs[f"solid_{key}"]
            n_rep = max(1, int(np.ceil((MIN_ATOMS / m["n_atoms"]) ** (1 / 3) - 1e-9)))
            big = repeat_structure(structure, orm.Int(n_rep))
            T_sw = list(CELLS[name[:4]][cell]); T_sw[1] = float((t_hi or {}).get(key, T_sw[1])); T_sw[0] = float((t_lo or {}).get(key, T_sw[0]))
            params = {"name": f"sol_{key}", "folder_prefix": f"sol_{key}", "mode": "ts", "elements": sp["elements"], "masses": sp["masses"], "pair_style": sp["pair_style"],
                      "pair_coeff": sp["pair_coeff"], "temperature": T_sw, "pressure": 0.0, "reference_phase": "solid", "n_equilibration_steps": 10000,
                      "n_switching_steps": [10000, 10000], "n_iterations": 1}
            params.update(extra)
            b = Calphy.get_builder()
            b.code = wc.inputs.calphy_code; b.structure = big; b.potential = wc.inputs.potential; b.parameters = orm.Dict(dict=params)
            b.metadata.options = wc.inputs.calphy_options.get_dict()
            b.metadata.label = f"calphy solid ti {name} {key} {m['phase']} x={m['x']:.4f} ({len(big.sites)} atoms)"
            node = aiida_submit(b)
            rec["jobs"][key] = {"pk": node.pk, "phase": m["phase"], "x": m["x"], "n_atoms": len(big.sites), "T_sweep": T_sw}
            print(name, key, node.pk, len(big.sites), "atoms", T_sw, wc.inputs.calphy_code.full_label)
        with open(_rec_path(name), "w") as f:
            json.dump(rec, f, indent=1)


#: stage-1 solid(TI)-liquid crossings (K, melting_ti.tsv; "~" values extrapolated) -> sweep caps of the stage-2 alloy cells
TM1 = {"nial_grace_fs": {"fccAl": 630, "fccNi": 1654, "B2": 1670, "L12": 1512}, "nial_grace_1l": {"fccAl": 874, "fccNi": 1715, "B2": 1797, "L12": 1615},
       "nial_sevenn_0": {"fccAl": 784, "fccNi": 1461, "B2": 1964, "L12": 1567}, "nial_grace_1l_b2ext_solid": {"fccAl": 874, "fccNi": 1715, "B2": 1797, "L12": 1615},
       "agcu_grace_fs": {"Ag": 930, "Cu": 1190}, "agcu_grace_1l": {"Ag": 988, "Cu": 1310}, "agcu_sevenn_0": {"Ag": 949, "Cu": 1182}}
#: where the stage-2 jobs of each run go (user 2026-11-01: laurel, mygardenx1/x2, mygarden5/6 GPUs allowed; mygardenx1 was full,
#: laurel has no ftphase env): GRACE-FS on the mygardenx2 CPUs (grace/fs + hybrid/scaled in the conda LAMMPS), the rest on the GPUs
HOST2 = {"nial_grace_fs": ("calphy@mygardenx2", 12), "agcu_grace_fs": ("calphy@mygardenx2", 12), "nial_grace_1l": ("calphy@mygarden6", None), "nial_grace_1l_b2ext_solid": ("calphy@mygarden6", None),
         "agcu_grace_1l": ("calphy@mygarden5", None), "nial_sevenn_0": ("calphy@mygarden5", None), "agcu_sevenn_0": ("calphy@mygarden6", None)}


NONCUBIC = ("NiAl3", "Ni2Al3")   #: phases calphy's melt detection cannot classify


def stage2_range(name, m):
    """Sweep [T_lo, T_hi] for an alloy cell, or None for cells that keep QHA (Ag-Cu 0.25 < x < 0.75, inside the miscibility gap, as in the
    EAM run) and for the stage-1 cells.  T_hi = the stage-1 melting point of the phase (alloy cells melt lower than the stoichiometric one,
    so no superheating margin); point phases: 0.9 x the Al-B2 interpolation; Ag-Cu: T_m(end) x (1 - 0.6 d), d = distance from that end."""
    tm, ph, x = TM1[name], m["phase"], m["x"]
    if name.startswith("nial"):
        lo = {"fccAl": 600.0, "fccNi": 1200.0, "B2": 1300.0, "L12": 1200.0, "Ni2Al3": 900.0, "NiAl3": 900.0}[ph]
        if "b2ext" in name and ph == "B2":
            lo = 1000.0   # multi-vacancy B2 cells lose atoms in Frenkel-Ladd when started at 1300 K (stage-2 note): start the extended-defect cells at 1000 K
        if ph in tm:
            if (ph, x) in CELLS["nial"]:
                return None
            hi = float(tm[ph])
            if ph == "fccNi":   # random fcc with Al melts below pure Ni (GRACE-FS x=0.75 melted at the 1654 K cap, pk 7596)
                hi *= 1.0 - 0.4 * (1.0 - x)
        else:
            hi = 0.9 * float(np.interp(x, [0.0, 0.5], [tm["fccAl"], tm["B2"]]))
    else:
        if x in (0.0, 1.0) or 0.25 < x < 0.75:
            return None
        d, end = (x, "Ag") if x < 0.5 else (1.0 - x, "Cu")
        lo, hi = 700.0, tm[end] * (1.0 - 0.6 * d)
    return [float(round(min(lo, 0.8 * hi))), float(round(hi))]


def qha_excluded(name, m):
    """Cells whose QHA rows are left out of the assembly (2026-11-06): QHA - TI reaches -33..-45 meV/atom at x_Cu = 0.25/0.75 (Ag-Cu, all
    three MLIPs; -2..-13 at the pure ends), so the TI-less cells inside the Ag-Cu gap (0.25 < x < 0.75) are far too stable and bend the one
    fcc curve into alternating fcc+fcc / fcc+liquid bands; the dilute fcc-Al cells of Ni-Al had their TI dropped (below the 900 K floor) and
    SevenNet-0 QHA puts fcc Al 37 meV/atom low, which kept a fccAl+liquid band up to 2000 K."""
    if name.startswith("agcu"):
        return 0.25 < m["x"] < 0.75
    return m["phase"] == "fccAl" and m["x"] > 0.0


def submit2(names, only=None, t_hi=None, t_lo=None, dry=False):
    """Stage 2: every alloy cell (stage2_range), on HOST2[name]."""
    from aiida import orm
    from aiida.engine import submit as aiida_submit
    from aiida.plugins import CalculationFactory

    from ftphase.aiida.functions import repeat_structure

    Calphy = CalculationFactory("ftphase.calphy")
    for name in names:
        wc, kids, prep = _workchain(RUNS[name])
        sp = wc.inputs.spec.get_dict(); sol_p = prep.outputs.solid_params.get_dict()
        code_label, cores = HOST2[name]
        code = orm.load_code(code_label)
        if cores:   # CPU host: calphy starts `cores` LAMMPS ranks itself; plain (non-Kokkos) pair style
            extra = {"gpu": False, "cores": cores}
            opts = {"resources": {"num_machines": 1, "num_mpiprocs_per_machine": cores}, "max_wallclock_seconds": 172800, "queue_name": "debug",
                    "withmpi": False, "custom_scheduler_commands": "#SBATCH --hint=nomultithread"}
        else:
            extra = wc.inputs.calphy_extra.get_dict() if "calphy_extra" in wc.inputs else {}
            opts = wc.inputs.calphy_options.get_dict()
        rec = json.load(open(_rec_path(name))) if os.path.exists(_rec_path(name)) else {"pk_workchain": RUNS[name], "jobs": {}}
        for key, m in sorted(sol_p.items()):
            T_sw = stage2_range(name, m)
            if T_sw is None or (only and key not in only) or (not only and key in rec["jobs"]):
                continue
            T_sw[1] = float((t_hi or {}).get(key, T_sw[1])); T_sw[0] = float((t_lo or {}).get(key, T_sw[0]))
            if dry:
                print(name, key, m["phase"], round(m["x"], 4), T_sw, code_label); continue
            structure = prep.outputs[f"solid_{key}"]
            n_rep = max(1, int(np.ceil((MIN_ATOMS / m["n_atoms"]) ** (1 / 3) - 1e-9)))
            big = repeat_structure(structure, orm.Int(n_rep))
            params = {"name": f"sol_{key}", "folder_prefix": f"sol_{key}", "mode": "ts", "elements": sp["elements"], "masses": sp["masses"], "pair_style": sp["pair_style"],
                      "pair_coeff": sp["pair_coeff"], "temperature": T_sw, "pressure": 0.0, "reference_phase": "solid", "n_equilibration_steps": 10000,
                      "n_switching_steps": [10000, 10000], "n_iterations": 1}
            params.update(extra)
            if m["phase"] in NONCUBIC:   # calphy's solid detection (CNA) only knows bcc/fcc/hcp/sc/dia: an orthorhombic NiAl3 cell is
                # reported as melted right after equilibration (GRACE-FS pk 7666).  Switch it off; check the sweep volume for a jump instead.
                params["extra"] = {**params.get("extra", {}), "tolerance": {"solid_fraction": 0.0}}
            b = Calphy.get_builder()
            b.code = code; b.structure = big; b.potential = wc.inputs.potential; b.parameters = orm.Dict(dict=params)
            b.metadata.options = opts
            b.metadata.label = f"calphy solid ti2 {name} {key} {m['phase']} x={m['x']:.4f} ({len(big.sites)} atoms)"
            node = aiida_submit(b)
            rec["jobs"][key] = {"pk": node.pk, "phase": m["phase"], "x": m["x"], "n_atoms": len(big.sites), "T_sweep": T_sw, "stage": 2, "code": code_label}
            print(name, key, node.pk, len(big.sites), "atoms", T_sw, code_label)
        if not dry:
            with open(_rec_path(name), "w") as f:
                json.dump(rec, f, indent=1)


LIQ_LOW = 750.0   #: Ag-Cu liquids are extended to this temperature (stage-1: the MLIP Ag melting points 930-990 K lie below the 1050 K liquid end)


def submit_liq_low(names, dry=False):
    """Ag-Cu: a second calphy ts liquid run per composition from (old lowest T + 100 K) down to LIQ_LOW, same cell and settings;
    assemble() splices it below the old sweep (merge_sweeps).  GRACE-FS runs on the mygardenx2 CPUs, the others on their GPU."""
    from aiida import orm
    from aiida.engine import submit as aiida_submit

    for name in [n for n in names if n.startswith("agcu")]:
        wc, kids, prep = _workchain(RUNS[name])
        base = {n.label.split()[1]: n for n in kids.get("CalphyCalculation", []) if n.label.startswith("calphy lqd") and n.is_finished_ok}
        lr = os.path.join(OUT, name, "liquids_rerun.json")
        if os.path.exists(lr):
            for tag, j in json.load(open(lr))["jobs"].items():
                n = orm.load_node(j["pk"])
                if n.is_finished_ok:
                    base[tag] = n
        code_label, cores = HOST2[name]
        path = os.path.join(OUT, name, "liquids_low.json")
        rec = json.load(open(path)) if os.path.exists(path) else {"pk_workchain": RUNS[name], "T_low": LIQ_LOW, "jobs": {}}
        for tag, old in sorted(base.items()):
            if tag in rec["jobs"]:
                continue
            p = old.inputs.parameters.get_dict()
            T_hi = float(min(p["temperature"])) + 100.0
            p.update({"temperature": [T_hi, LIQ_LOW], "name": tag + "_low", "folder_prefix": tag + "_low"})
            b = old.get_builder_restart()
            if cores:
                p.pop("lammps_executable", None); p.update({"gpu": False, "cores": cores})
                b.code = orm.load_code(code_label)
                b.metadata.options = {"resources": {"num_machines": 1, "num_mpiprocs_per_machine": cores}, "max_wallclock_seconds": 172800, "queue_name": "debug",
                                      "withmpi": False, "custom_scheduler_commands": "#SBATCH --hint=nomultithread"}
            b.parameters = orm.Dict(dict=p)
            b.metadata.label = f"calphy {tag} low {T_hi:.0f}->{LIQ_LOW:.0f} K"
            if dry:
                print(name, tag, old.pk, p["temperature"], b.code.full_label); continue
            n = aiida_submit(b)
            rec["jobs"][tag] = {"pk": n.pk, "base_pk": old.pk, "temperature": p["temperature"]}
            print(name, tag, old.pk, "->", n.pk, p["temperature"], b.code.full_label)
        if not dry:
            with open(path, "w") as f:
                json.dump(rec, f, indent=1)


def submit_liq_ext(names, spec, dry=False):
    """Extend a liquid sweep of the original WorkChain to lower temperatures (same cell, settings and code): spec = {x: [T_hi, T_lo]},
    e.g. {1.0: [2200, 1900]} for the Rh liquid of the Pt-Rh runs (the production sweep stops at 2100 K, the TI-liquid crossing lies
    below).  Records go to out/<name>/liquids_low.json like submit_liq_low, so assemble() splices them with merge_sweeps."""
    from aiida import orm
    from aiida.engine import submit as aiida_submit

    for name in names:
        wc, kids, prep = _workchain(RUNS[name])
        path = os.path.join(OUT, name, "liquids_low.json")
        rec = json.load(open(path)) if os.path.exists(path) else {"pk_workchain": RUNS[name], "jobs": {}}
        for old in sorted((n for n in kids.get("CalphyCalculation", []) if n.label.startswith("calphy lqd") and n.is_finished_ok), key=lambda n: n.label):
            tag = old.label.split()[1]; x = float(old.label.split("x=")[1])
            hit = next((v for k, v in spec.items() if abs(float(k) - x) < 2e-3), None)
            if hit is None or tag in rec["jobs"]:
                continue
            p = old.inputs.parameters.get_dict()
            p.update({"temperature": [float(hit[0]), float(hit[1])], "name": tag + "_low", "folder_prefix": tag + "_low"})
            b = old.get_builder_restart()
            b.parameters = orm.Dict(dict=p)
            b.metadata.label = f"calphy {tag} low {hit[0]:.0f}->{hit[1]:.0f} K"
            if dry:
                print(name, tag, old.pk, p["temperature"], b.code.full_label); continue
            n = aiida_submit(b)
            rec["jobs"][tag] = {"pk": n.pk, "base_pk": old.pk, "temperature": p["temperature"]}
            print(name, tag, old.pk, "->", n.pk, p["temperature"], b.code.full_label)
        if not dry:
            with open(path, "w") as f:
                json.dump(rec, f, indent=1)


def _merge_sweeps():
    from aiida.engine import calcfunction

    @calcfunction
    def merge_sweeps(hi, lo):
        """Splice two calphy ts sweeps of the same liquid: `hi` where it exists, `lo` below hi's lowest temperature.  The offset of lo
        against hi in their overlap is stored (attribute overlap_offset_meV) but not applied."""
        from aiida import orm

        Th, Gh, Eh = (hi.get_array(k) for k in ("temperature", "free_energy", "error"))
        Tl, Gl, El = (lo.get_array(k) for k in ("temperature", "free_energy", "error"))
        ov = (Tl >= Th.min()) & (Tl <= Th.max())
        off = float(np.mean(Gl[ov] - np.interp(Tl[ov], Th[::-1], Gh[::-1]) if Th[0] > Th[-1] else Gl[ov] - np.interp(Tl[ov], Th, Gh))) if ov.any() else float("nan")
        keep = Tl < Th.min()
        out = orm.ArrayData()
        for k, a, b in (("temperature", Th, Tl), ("free_energy", Gh, Gl), ("error", Eh, El)):
            out.set_array(k, np.concatenate([a, b[keep]]))
        out.base.attributes.set("overlap_offset_meV", off * 1000 if np.isfinite(off) else None)
        return out

    return merge_sweeps


def status(names):
    from aiida import orm

    for name in names:
        if not os.path.exists(_rec_path(name)):
            continue
        for key, j in json.load(open(_rec_path(name)))["jobs"].items():
            n = orm.load_node(j["pk"])
            print(f"{name:15s} {key:11s} pk {j['pk']} {n.process_state.value if n.process_state else '?':9s} exit {n.exit_status} {n.ctime:%m-%d %H:%M} -> {n.mtime:%m-%d %H:%M}")


def melt(names):
    """Crossing of the TI solid sweep with the liquid sweep of the same composition (05 table of the original run)."""
    import pandas as pd
    from aiida import orm

    rows = []
    for name in names:
        if not os.path.exists(_rec_path(name)):
            continue
        ti_tab = os.path.join(OUT, name + "_ti", "05_free_energies.tsv")   # after `assemble`: includes rerun liquids
        t = pd.read_csv(ti_tab if os.path.exists(ti_tab) else os.path.join(OUT, name, "05_free_energies.tsv"), sep="\t")
        for key, j in json.load(open(_rec_path(name)))["jobs"].items():
            n = orm.load_node(j["pk"])
            liq = t[(t.phase == "liquid") & np.isclose(t.x, j["x"], atol=2e-3)].groupby("T")["G"].mean()
            lx = t[t.phase == "liquid"].x.unique()
            if liq.empty and (lx < j["x"]).any() and (lx > j["x"]).any():   # e.g. L1_2 x=0.75: linear interpolation in x between the neighbouring liquid compositions (common temperatures)
                lt = t[t.phase == "liquid"]; xs = np.sort(lt.x.unique()); xl, xh = xs[xs < j["x"]].max(), xs[xs > j["x"]].min()
                gl, gh = (lt[np.isclose(lt.x, v)].groupby("T")["G"].mean() for v in (xl, xh)); Tc = gl.index.intersection(gh.index)
                w = (j["x"] - xl) / (xh - xl); liq = (1 - w) * gl[Tc] + w * gh[Tc]
            alli = os.path.join(OUT, "alli" + name[4:], "05_free_energies.tsv")
            if name.startswith("nial") and j["x"] == 0.0 and os.path.exists(alli):   # pure-Al liquid of the Al-Li run (same MLIP) reaches 700 K; agrees within 0.6 meV/atom
                ta = pd.read_csv(alli, sep="\t"); la = ta[(ta.phase == "liquid") & np.isclose(ta.x, 0.0)].groupby("T")["G"].mean()
                liq = pd.concat([la[la.index < liq.index.min()], liq]).sort_index()
            t0 = pd.read_csv(os.path.join(OUT, name, "05_free_energies.tsv"), sep="\t")   # QHA-only table of the original run
            qha = t0[(t0.phase == j["phase"]) & np.isclose(t0.x, j["x"])].groupby("T")["G"].mean()
            r = {"run": name, "cell": key, "phase": j["phase"], "x": j["x"], "T_expt": EXPT.get((name[:4], j["phase"], j["x"])), "state": n.process_state.value, "exit": n.exit_status}
            if n.is_finished_ok and "sweep" in n.outputs and len(liq) > 1:
                Ts, Gs = n.outputs.sweep.get_array("temperature"), n.outputs.sweep.get_array("free_energy")
                lo, hi = max(Ts.min(), liq.index.min()), min(Ts.max(), liq.index.max())
                grid = np.linspace(lo, hi, 400) if hi > lo else np.array([])
                d = np.interp(grid, liq.index, liq.values) - np.interp(grid, Ts, Gs) if grid.size else np.array([])
                s = np.where(np.diff(np.sign(d)) != 0)[0]
                r["T_m_ti"] = f"{grid[s[0]]:.0f}" if s.size else ("> %.0f" % hi if d.size and d[-1] > 0 else "< %.0f" % lo if d.size else "no overlap")
                if not s.size and d.size > 20:   # linear extrapolation of dG = G_liq - G_sol from the last/first 20 % of the overlap
                    k = max(5, d.size // 5); sl = slice(-k, None) if d[-1] > 0 else slice(0, k)
                    c = np.polyfit(grid[sl], d[sl], 1); r["T_m_extrap"] = round(float(-c[1] / c[0])) if c[0] != 0 else None
                tm = 0.5 * (Ts.min() + Ts.max())
                r["qha_minus_ti_meV@%s" % "mid"] = round(float((np.interp(tm, qha.index, qha.values) - np.interp(tm, Ts, Gs)) * 1000), 1) if len(qha) else None
                r["T_mid"] = round(float(tm))
            rows.append(r)
    df = pd.DataFrame(rows)
    cmp_dir = "mlip_compare_ptrh" if all(n.startswith("ptrh") for n in names) else "mlip_compare_nial_agcu"   # keep the Ni-Al / Ag-Cu table intact
    os.makedirs(os.path.join(OUT, cmp_dir), exist_ok=True)
    df.to_csv(os.path.join(OUT, cmp_dir, "melting_ti.tsv"), sep="\t", index=False)
    print(df.to_string(index=False))


def assemble(names):
    from aiida import orm

    from ftphase.aiida.functions import assemble_diagram

    for name in names:
        rec = json.load(open(_rec_path(name)))
        wc, kids, prep = _workchain(rec["pk_workchain"])
        nodes = {}
        sol_p = prep.outputs.solid_params.get_dict()
        for n in kids.get("QhaCalculation", []):
            key = n.label.split()[1]
            if n.is_finished_ok and not qha_excluded(name, sol_p[key]):
                nodes[f"qha_{key}"] = n.outputs.arrays
        for n in kids.get("CalphyCalculation", []):
            if n.is_finished_ok and "sweep" in n.outputs and n.label.startswith("calphy lqd"):
                nodes[f"liq_{''.join(c if c.isalnum() else '_' for c in n.label.split()[1])}"] = n.outputs.sweep
        for key, j in rec["jobs"].items():
            n = orm.load_node(j["pk"])
            if n.is_finished_ok and "sweep" in n.outputs:
                nodes[f"sti_{key}"] = n.outputs.sweep
        # identical pure-element twins (e.g. Ag-Cu s23/s24 at x=1) share the TI sweep
        for key, m in sol_p.items():
            if f"sti_{key}" not in nodes and m["x"] in (0.0, 1.0):
                twin = next((k for k, j in rec["jobs"].items() if f"sti_{k}" in nodes and j["phase"] == m["phase"] and j["x"] == m["x"]), None)
                if twin:
                    nodes[f"sti_{key}"] = nodes[f"sti_{twin}"]
        lr = os.path.join(OUT, name, "liquids_rerun.json")   # liquids rerun after a fix (agcu_sevenn_0: pair_e3gnn nedges bound)
        if os.path.exists(lr):
            for tag, j in json.load(open(lr))["jobs"].items():
                n = orm.load_node(j["pk"])
                if n.is_finished_ok and "sweep" in n.outputs:
                    nodes[f"liq_{''.join(c if c.isalnum() else '_' for c in tag)}"] = n.outputs.sweep
        ll = os.path.join(OUT, name, "liquids_low.json")   # Ag-Cu liquids extended to LIQ_LOW: spliced below the old sweep
        if os.path.exists(ll):
            merge = _merge_sweeps()
            import re
            # several extensions of one liquid (e.g. 2000->1700 then 1800->1500 K): splice in order of decreasing T_hi; the record key may carry a suffix
            for tag, j in sorted(json.load(open(ll))["jobs"].items(), key=lambda kv: -max(kv[1]["temperature"])):
                base_tag = (re.match(r"(lqd_x\d+\.\d+)", tag) or re.match(r"(.*)", tag)).group(1)
                n, k = orm.load_node(j["pk"]), f"liq_{''.join(c if c.isalnum() else '_' for c in base_tag)}"
                if n.is_finished_ok and "sweep" in n.outputs and k in nodes:
                    nodes[k] = merge(nodes[k], n.outputs.sweep)
                    print(name, tag, "low sweep spliced, overlap offset", nodes[k].base.attributes.get("overlap_offset_meV"), "meV/atom")
        spec = wc.inputs.spec
        if name.startswith("agcu") and os.path.exists(os.path.join(OUT, name, "liquids_low.json")):   # liquids now reach LIQ_LOW: assemble from there
            sp = spec.get_dict(); sp["assemble"] = {**sp["assemble"], "T_min": LIQ_LOW, "liquid_partial": True}   # pure-Cu liquids stop at 1100 K (crystallize below)
            spec = orm.Dict(dict=sp); spec.label = f"{name} spec, assemble.T_min {LIQ_LOW:.0f} K, liquid_partial"
        res = assemble_diagram(spec, prep.outputs.solid_params, prep.outputs.liquid_params, **nodes)
        out = os.path.join(OUT, name + "_ti"); os.makedirs(out, exist_ok=True)
        for label, fn in (("report", "REPORT.md"), ("figure", "07_phase_diagram.png"), ("free_energies", "05_free_energies.tsv"), ("regions", "07_two_phase_regions.tsv"), ("invariants", "07_invariants.tsv")):
            with res[label].open(mode="rb") as f, open(os.path.join(out, fn), "wb") as g:
                g.write(f.read())
        with open(os.path.join(out, "summary.json"), "w") as f:
            json.dump(res["summary"].get_dict(), f, indent=1, default=str)
        print(name, "->", out, "| sti", sum(k.startswith("sti_") for k in nodes))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["submit", "submit2", "liqlow", "liqext", "status", "melt", "assemble"])
    ap.add_argument("--liq", default="1.0:2200:1900", help="liqext: comma-separated x:T_hi:T_lo")
    ap.add_argument("--names", default=",".join(RUNS)); ap.add_argument("--profile", default="ftphase")
    ap.add_argument("--only", default=None, help="comma-separated solid keys to (re)submit")
    ap.add_argument("--T-hi", dest="t_hi", default=None, help="sweep-end overrides key=T,key=T")
    ap.add_argument("--dry", action="store_true", help="submit2: print the cells and sweeps only")
    ap.add_argument("--T-lo", dest="t_lo", default=None, help="sweep-start overrides key=T,key=T")
    a = ap.parse_args()
    from aiida import load_profile

    load_profile(a.profile)
    names = a.names.split(",")
    only = set(a.only.split(",")) if a.only else None
    t_hi = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in a.t_hi.split(",")} if a.t_hi else None
    t_lo = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in a.t_lo.split(",")} if a.t_lo else None
    {"submit": lambda: submit(names, only, t_hi, t_lo), "submit2": lambda: submit2(names, only, t_hi, t_lo, a.dry), "liqlow": lambda: submit_liq_low(names, a.dry), "liqext": lambda: submit_liq_ext(names, {float(t.split(":")[0]): [float(t.split(":")[1]), float(t.split(":")[2])] for t in a.liq.split(",")}, a.dry), "status": lambda: status(names), "melt": lambda: melt(names), "assemble": lambda: assemble(names)}[a.cmd]()
