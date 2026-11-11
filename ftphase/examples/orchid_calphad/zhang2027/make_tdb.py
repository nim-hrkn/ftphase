"""Build the six TDBs for an MLIP result folder with the deposit's own 03-make_tdb.py functions (SGTE unary + polynomial end members +
dilute / L1-L2 solid solutions + CEF, liquid from data/liquid_description.json re-optimised to the solid free energies).
    python make_tdb.py <deposit dir> <folder with <system>/*.json> [--systems ...]
Writes <folder>/<system>.tdb.  Run in env/ftphase (pycalphad, phonopy, scipy).
"""
import argparse, importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "benchmark")); sys.path.insert(0, HERE)
FUNCS = {"W-Re": "make_tdb_for_WRe", "Cu-Mg": "make_tdb_for_CuMg", "Ru-Si": "make_tdb_for_RuSi", "Cu-Pt": "make_tdb_for_CuPt", "Mo-Rh": "make_tdb_for_MoRh", "Al-Zn": "make_tdb_for_AlZn"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("deposit"); ap.add_argument("folder"); ap.add_argument("--systems", nargs="*", default=list(FUNCS)); a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("make_tdb_deposit", os.path.join(a.deposit, "03-make_tdb.py")); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    for s in a.systems:
        src = os.path.join(a.folder, s)
        if not os.path.isdir(src):
            print(s, "no folder"); continue
        out = os.path.join(a.folder, f"{s}.tdb")
        try:
            getattr(mod, FUNCS[s])(src, out); print("wrote", out)
        except Exception as e:
            print(s, "FAILED:", repr(e)[:300])


if __name__ == "__main__":
    main()
