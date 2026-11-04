"""Add the interaction parameters that ESPEI's parameter generation cannot create (ORCHID has no mixing data for Al-Li),
as free VV#### symbols so that the MCMC step fits them to the ZPF data.

    python add_params.py alli-gen.tdb alli-start.tdb

Parameters added (Redlich-Kister, J/mol-formula): LIQUID L0 = a + b T, L1 = a; FCC_A1 L0 = a + b T;
ALLI_B32 L(AL,LI:AL) = L(AL,LI:LI) = L(AL:AL,LI) = L(LI:AL,LI) = a (one symmetric symbol).
Start values are generic (negative mixing, no literature parameter copied); every walker must start non-zero because
ESPEI scatters walkers multiplicatively around the start value."""

import re
import sys

src, dst = sys.argv[1], sys.argv[2]
txt = open(src, encoding="utf-8").read()
nums = [int(m) for m in re.findall(r"\bVV(\d{4})\b", txt)]
n = max(nums) + 1 if nums else 0


def sym(val):
    global n
    name = f"VV{n:04d}"
    n += 1
    return name, f"FUNCTION {name} 298.15 {val}; 6000 N !\n"


funcs, params = [], []
# LIQUID
a0, f = sym(-30000.0); funcs.append(f)
b0, f = sym(8.0); funcs.append(f)
params.append(f"PARAMETER L(LIQUID,AL,LI;0) 298.15 {a0}+{b0}*T; 6000 N !\n")
a1, f = sym(3000.0); funcs.append(f)
params.append(f"PARAMETER L(LIQUID,AL,LI;1) 298.15 {a1}; 6000 N !\n")
# FCC_A1
c0, f = sym(-20000.0); funcs.append(f)
d0, f = sym(5.0); funcs.append(f)
params.append(f"PARAMETER L(FCC_A1,AL,LI:VA;0) 298.15 {c0}+{d0}*T; 6000 N !\n")
# ALLI_B32 (symmetric)
e0, f = sym(-10000.0); funcs.append(f)
for sub in ["AL,LI:AL", "AL,LI:LI", "AL:AL,LI", "LI:AL,LI"]:
    params.append(f"PARAMETER L(ALLI_B32,{sub};0) 298.15 {e0}; 6000 N !\n")

# tie the two B32 ordered end members (AL:LI, LI:AL) to one symbol and give the compounds a free T-linear term
txt = txt.replace("0.5*GHSERLI+0.5*GHSERAL+VV0005;", "0.5*GHSERLI+0.5*GHSERAL+VV0004;")
tb, f = sym(2.0); funcs.append(f)
txt = txt.replace("+VV0004;", f"+VV0004+T*{tb};")
t2, f = sym(5.0); funcs.append(f)
txt = txt.replace("+VV0000;", f"+VV0000+T*{t2};")
t4, f = sym(10.0); funcs.append(f)
txt = txt.replace("+VV0001;", f"+VV0001+T*{t4};")
out = txt.rstrip() + "\n\n" + "".join(funcs) + "".join(params)
open(dst, "w", encoding="utf-8").write(out)
print("added", len(funcs), "symbols,", len(params), "parameters ->", dst)
print("symbols to fit:", [m for m in re.findall(r"FUNCTION (VV\d{4})", out) if m not in ("VV0002", "VV0003", "VV0005")])
