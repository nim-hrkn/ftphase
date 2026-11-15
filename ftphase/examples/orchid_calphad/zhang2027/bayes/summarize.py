"""Table of the Ru-Si Bayesian updates (eSEN TDB of the deposit + the MLIPs computed in this project) -> out/models.tsv, printed."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
RUNS = [("eSEN (deposit TDB)", "out")] + [(m, f"runs/{m}/out") for m in ("dpa4-plus-omat24", "sevenn-mf-ompa", "mace-mpa-0", "mattersim-5m")]
PH = ["RU2SI", "SI3RU5", "RU4SI3", "RUSI", "RU2SI3"]; rows = []
for n, d in RUNS:
    f = os.path.join(H, d, "summary.json")
    if not os.path.exists(f):
        continue
    s = json.load(open(f)); pr, po = s["prior"], s["posterior"]; cmp_ = lambda l: ",".join(p for p in l if p not in ("HCP", "LIQUID", "SI"))
    r = {"model": n, "iterations": s["iterations"], "ref_prior": cmp_(s["point_mlip_phases"]), "ref_post": cmp_(s["point_posterior_mean_phases"])}
    for p in PH:
        r[p] = f'{pr["P_stable_anywhere"].get(p, 0):.2f}>{po["P_stable_anywhere"].get(p, 0):.2f}'
    for k, lab in (("P_region_1250K_x0.22", "p1250"), ("P_region_1550K_x0.38", "p1550"), ("P_region_1900K_x0.44", "p1900")):
        r[lab] = f'{list(pr[k].values())[0]:.2f}>{list(po[k].values())[0]:.2f}'
    r["T_liq_min_Ru"] = "%.0f±%.0f>%.0f±%.0f" % (*pr["lowest_T_liquid_x<=0.33"], *po["lowest_T_liquid_x<=0.33"])
    il = s.get("invariant_lines", {}); r["inv_T_5_50_95"] = ">".join("/".join("%.0f" % il[k]["their_T_percentiles_5_25_50_75_95"][i] for i in (0, 2, 4)) for k in ("prior", "posterior")) if il else ""
    r["shifts(dH J, dS J/K)"] = " ".join("%s %+.0f/%+.2f" % (p["phase"], p["dH_post_mean_std_J"][0], p["dS_post_mean_std_J_K"][0]) for p in s["parameters"] if abs(p["dH_post_mean_std_J"][0]) > 250 or abs(p["dS_post_mean_std_J_K"][0]) > 0.4)
    rows.append(r)
cols = list(rows[0]); open(os.path.join(H, "out", "models.tsv"), "w").write("\t".join(cols) + "\n" + "\n".join("\t".join(str(r[c]) for c in cols) for r in rows) + "\n")
for r in rows:
    print("==", r["model"], "iterations", r["iterations"]); [print("   %-22s %s" % (c, r[c])) for c in cols[2:]]
