"""SGTE (Dinsdale 1991) Gibbs energies of the pure elements in the phases the project uses, tabulated on a temperature grid.
Source: espei.refdata.SGTE91 (GHSER and lattice stabilities, J/mol relative to H_SER(298.15 K)).  Run in env/pycalphad:
    env/pycalphad/bin/python sgte_unary.py Al Li [--T 200 1200 5]   ->  sgte_unary.json  {el: {phase: [G eV/atom ...]}, "T": [...]}
"""
import argparse, json, os
import numpy as np
from espei import refdata
from symengine import Symbol, lambdify

J2EV = 1.0 / 96485.33212


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("elements", nargs="+"); ap.add_argument("--T", nargs=3, type=float, default=[200.0, 1200.0, 5.0]); a = ap.parse_args()
    T = np.arange(a.T[0], a.T[1] + 1e-9, a.T[2]); Ts = Symbol("T"); out = {"T": T.tolist(), "units": "eV/atom relative to H_SER(298.15 K)", "source": "espei.refdata.SGTE91 (Dinsdale 1991)", "ser": {}}
    for el in a.elements:
        out[el] = {}; EL = el.upper(); out["ser"][el] = refdata.SGTE91SER.get(EL, {}).get("phase") if hasattr(refdata, "SGTE91SER") else None
        for ph, key in (("fcc", "FCC_A1"), ("bcc", "BCC_A2"), ("hcp", "HCP_A3"), ("liquid", "LIQUID")):
            expr = refdata.SGTE91.get((EL, key))
            if expr is None:
                continue
            expr = expr.subs({Symbol("GHSER" + EL): refdata.SGTE91Stable[EL]})     # lattice stabilities are written relative to GHSER
            out[el][ph] = [float(expr.subs({Ts: float(t)}).n()) * J2EV for t in T]
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sgte_unary.json"), "w"))
    for el in a.elements:
        s = out[el]; i = lambda t: int(np.argmin(abs(T - t)))
        if "liquid" in s:
            for ph in s:
                if ph != "liquid":
                    d = np.array(s["liquid"]) - np.array(s[ph]); j = np.where(np.diff(np.sign(d)))[0]
                    print(el, ph, "G_liq - G_%s = 0 at" % ph, [round(float(T[k] - d[k] * (T[k + 1] - T[k]) / (d[k + 1] - d[k])), 1) for k in j], "K; at 300 K fcc-bcc etc:", round((np.array(s[ph])[i(300)] - min(np.array(v)[i(300)] for v in s.values())) * 1000, 2), "meV above the lowest")


if __name__ == "__main__":
    main()
