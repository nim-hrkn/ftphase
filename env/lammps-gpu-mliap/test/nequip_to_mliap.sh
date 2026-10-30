#!/bin/bash
# Export a NequIP / Allegro package (nequip.net ID, .nequip.zip or checkpoint) as LAMMPS ML-IAP unified files (nequip 0.19.1, nequip-allegro 0.8.3).
#   env/lammps-gpu-mliap/test/nequip_to_mliap.sh [nequip.net:mir-group/NequIP-OAM-L:0.1] [name]
# Writes potentials/nequip/<name>.nequip.lmp.pt (OpenEquivariance, torch.compile; GPU only), <name>-nocompile.nequip.lmp.pt (OEQ eager)
# and <name>-plain.nequip.lmp.pt (e3nn, also runs on the CPU), plus a copy of the package zip from ~/.nequip/model_cache.
# Allegro models (e.g. nequip.net:mir-group/Allegro-OAM-L:0.1) take --modifiers enable_CuEquivarianceContracter or enable_TritonContracter
# instead of enable_OpenEquivariance (nequip docs, integrations/lammps/index.html); set MODIFIER to override.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
SRC=${1:-nequip.net:mir-group/NequIP-OAM-L:0.1}
NAME=${2:-$(echo "$SRC" | sed -E 's|.*/||; s|:|-|g')}
MODIFIER=${MODIFIER:-enable_OpenEquivariance}
OUT=$ROOT/potentials/nequip; mkdir -p "$OUT"
export CUDA_VISIBLE_DEVICES= TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
PREP=$ROOT/env/torch/bin/nequip-prepare-lmp-mliap
"$PREP" "$SRC" "$OUT/$NAME.nequip.lmp.pt" --modifiers "$MODIFIER"
"$PREP" "$SRC" "$OUT/$NAME-nocompile.nequip.lmp.pt" --modifiers "$MODIFIER" --no-compile
"$PREP" "$SRC" "$OUT/$NAME-plain.nequip.lmp.pt"
if [[ "$SRC" == nequip.net:* ]]; then
  z=$(ls -t ~/.nequip/model_cache/*.nequip.zip 2>/dev/null | head -1); [ -n "$z" ] && cp -n "$z" "$OUT/$NAME.nequip.zip" || true
elif [[ "$SRC" == *.nequip.zip ]]; then cp -n "$SRC" "$OUT/$NAME.nequip.zip" || true; fi
ls -la "$OUT" | grep "$NAME"
