"""The uniform compound procedure for one system, run to convergence of the sampled composition windows.

    python auto.py <system> [--rounds 4] [--dry] [--replay KMAX]

1. single-defect cells (4 point defects x 3 cell sizes) for every compound that has none yet,
2. multi-defect cells with the default numbers of defects (2, 4, 8, 12) on both sides,
3. assemble (assemble.py): hull, widths, which compound sides touch the edge of the compositions covered by the multi-defect cells,
4. for those sides: cells with more defects (ftphase.compounds.next_defect_counts), then 3 again,
until no side is at the edge, the cells cannot hold more defects, or --rounds is reached.

--dry      only print what would be computed
--replay K assemble with the cells of at most K defects only and print the extension that would follow (no calculation): shows what the
           loop would have done on results that already contain the larger cells (Ni-Al GRACE-1L: B2 was cut at 12 defects)
Run with the python of the system's calculator (env/ftphase for LAMMPS styles, env/torch for SevenNet).  Lesson behind it: with 12 defects
in 250 sites the B2 window is x = 0.475-0.548 and B2 came out 0.480-0.544 ('at the window edge'); with 20-40 defects it is 0.458-0.608.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)


def main():
    import assemble, run_defects as rd
    from ftphase.compounds import next_defect_counts
    ap = argparse.ArgumentParser(); ap.add_argument("system"); ap.add_argument("--rounds", type=int, default=4); ap.add_argument("--dry", action="store_true"); ap.add_argument("--replay", type=int, default=None)
    a = ap.parse_args(); out = os.path.join(HERE, "out", a.system); names = assemble.CFG[a.system]["compounds"]

    def load(name):
        f = os.path.join(out, f"defects_{name}.json"); return json.load(open(f)) if os.path.exists(f) else {}

    def plan(need, kmax=None):
        todo = []
        for name, sides in need.items():
            r = load(name); mu = r["multi"]; N = mu["n_sites"]; c = rd.SYSTEMS[a.system]()["compounds"][name]; na, nb_ = c["site_counts"]
            for side in sides:
                dk = mu["constitutional_defects"][side]; host_is_A = dk in ("B_on_A", "Va_on_A"); n_host = N * (na if host_is_A else nb_) // (na + nb_)
                km = max(v["k"] for v in mu["cells"].values() if v["side"] == side and (kmax is None or v["k"] <= kmax)); ks = next_defect_counts(km, n_host)
                todo.append((name, side, dk, km, ks))
        return todo

    if a.replay is not None:
        need = assemble.main(a.system, kmax=a.replay, quiet=True); print(f"replay with cells of at most {a.replay} defects: sides at the window edge = {need}")
        for name, side, dk, km, ks in plan(need, a.replay):
            print(f"  -> {name} {side} ({dk}): largest so far {km} defects, next {ks or 'none (the cell cannot hold more)'}")
        assemble.main(a.system, quiet=True); return
    for name in names:
        r = load(name)
        if not r.get("sizes"):
            print("single-defect cells:", name, flush=True); a.dry or rd.single(a.system, name)
        if not load(name).get("multi", {}).get("cells"):
            print("multi-defect cells (2, 4, 8, 12):", name, flush=True); a.dry or rd.multi(a.system, name)
    if a.dry and any(not load(n).get("multi", {}).get("cells") for n in names):
        print("(dry run: the assembly needs the cells above)"); return
    for rnd in range(1, a.rounds + 1):
        need = assemble.main(a.system, quiet=True); todo = [t for t in plan(need) if t[4]]
        print(f"round {rnd}: sides at the window edge = {need}", flush=True)
        if not todo:
            print("converged: no side at the edge of its window" if not need else "stopped: the cells cannot hold more defects on " + str(need)); break
        for name, side, dk, km, ks in todo:
            print(f"  {name} {side} ({dk}): largest so far {km}, computing {ks}", flush=True); a.dry or rd.multi(a.system, name, ks=tuple(ks), sides=(side,))
        if a.dry:
            break
    else:
        print("stopped after", a.rounds, "rounds; still at the edge:", assemble.main(a.system, quiet=True))


if __name__ == "__main__":
    main()
