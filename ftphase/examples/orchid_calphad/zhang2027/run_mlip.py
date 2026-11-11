"""Run one of this project's MLIPs through the Zhang 2027 workflow (deposit's benchmark.mlip.calculate_with_mlip: GoodOldQuasiNewton +
FrechetCellFilter relaxation, fmax 2.5 meV/A, then finite-displacement phonons with the DFT supercell/displacement) on the DFT structure
set of the deposit, writing JSON files in the deposit layout so that errors.py / make_tdb.py / classify.py accept the folder.
    python run_mlip.py <deposit dir> <outdir> --calc mace|mattersim|sevenn|deepmd --model <path or name> [--systems ...] [--device cuda]
Resumable: structures whose JSON exists are skipped.
"""
import argparse, glob, os, sys, time, traceback
os.environ.setdefault("MPLBACKEND", "Agg")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "benchmark")); sys.path.insert(0, HERE)
from dft import DFTCompound          # noqa: E402  (deposit modules; mlip.py imports `dft` by its bare name)
from mlip import calculate_with_mlip  # noqa: E402
# the deposit's driver draws a band structure through seekpath after the phonon run; spglib's Niggli reduction fails for a few relaxed
# low-symmetry SQS cells (MACE Mo8Rh24) and would lose the whole structure, so the band-structure step is made non-fatal (mesh/free energy unaffected)
import phonopy  # noqa: E402
_auto_band, _plot_band = phonopy.Phonopy.auto_band_structure, phonopy.Phonopy.plot_band_structure


def _safe_auto_band(self, *a, **k):
    try:
        return _auto_band(self, *a, **k)
    except Exception as e:  # noqa: BLE001
        print("band structure skipped:", str(e)[:80], flush=True); self._band_skipped = True


class _NoFig:
    def savefig(self, *a, **k):
        pass


def _safe_plot_band(self, *a, **k):
    return _NoFig() if getattr(self, "_band_skipped", False) else _plot_band(self, *a, **k)


phonopy.Phonopy.auto_band_structure, phonopy.Phonopy.plot_band_structure = _safe_auto_band, _safe_plot_band


def make_calculator(kind, model, device):
    if kind == "mace":
        from mace.calculators import MACECalculator
        return MACECalculator(model_paths=model, device=device, default_dtype="float64")
    if kind == "mattersim":
        from mattersim.forcefield import MatterSimCalculator
        return MatterSimCalculator(load_path=model, device=device)
    if kind == "sevenn":
        from sevenn.calculator import SevenNetCalculator
        modal = "mpa" if "mf" in os.path.basename(model).lower() or "ompa" in model.lower() else None
        return SevenNetCalculator(model=model, device=device, modal=modal)
    if kind == "deepmd":
        from deepmd.calculator import DP
        return DP(model=model)
    raise SystemExit(kind)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("deposit"); ap.add_argument("outdir"); ap.add_argument("--calc", required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--systems", nargs="*", default=["Al-Zn", "Cu-Mg", "Cu-Pt", "Mo-Rh", "Ru-Si", "W-Re"]); ap.add_argument("--device", default="cuda"); a = ap.parse_args()
    calc = make_calculator(a.calc, a.model, a.device)
    for system in a.systems:
        os.makedirs(os.path.join(a.outdir, system, "results"), exist_ok=True)
        for f in sorted(glob.glob(os.path.join(a.deposit, "DFT", system, "*.json"))):
            fn = os.path.basename(f); out = os.path.join(a.outdir, system, fn)
            if os.path.exists(out):
                continue
            t0 = time.time()
            try:
                comp = DFTCompound.from_json(f)
                new = calculate_with_mlip(comp, calc, foldername=os.path.join(a.outdir, system, "results", fn[:-5]), is_plusminus=True)
                new.save_json(out)
                print(f"{system} {fn[:-5]:24s} E {new.energy_per_atom_eV:9.4f} eV/atom  {time.time() - t0:6.0f} s", flush=True)
            except Exception:
                print(f"{system} {fn[:-5]} FAILED"); traceback.print_exc(); sys.stdout.flush()


if __name__ == "__main__":
    main()
