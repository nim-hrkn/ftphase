#!/bin/bash
# Smoke + timing tests of lmp_gpugrace: grace/fs (CPU 1 rank, CPU 4 ranks, GPU kk), grace/1l (GPU kk), hybrid/scaled + grace/fs + ufm (GPU kk, calphy's liquid mix).
# Output: test/results.md.  The pure-CPU reference uses the same binary without -k on.
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd); P=$ROOT/../..
source /home/kino/miniforge3/etc/profile.d/conda.sh; conda activate "$ROOT/../ftphase"; set -u
LMP=$ROOT/bin/lmp_gpugrace; FS=$P/potentials/grace/GRACE-FS-OAM.yaml; NPZ=$P/potentials/grace/GRACE-1L-OMAT-medium-base-fp64-kokkos.npz
KK="-k on g 1 -sf kk -pk kokkos newton on neigh half"
cd "$ROOT/test"; OUT=results.md; : > $OUT
run() { # tag, n, style, pot, kokkos(0/1), ranks
  local tag=$1 n=$2 style=$3 pot=$4 kk=$5 np=$6 args="-in in.grace -var n $2 -var style $3 -var pot $4 -log log.$1 -screen none"
  if [ "$kk" = 1 ]; then args="$args $KK"; fi
  local t0=$(date +%s.%N)
  if "$ROOT/../ftphase/bin/mpirun" -np $np "$LMP" $args; then
    local t1=$(date +%s.%N); local pe=$(awk '/^ *50 /{print $3}' log.$1 | tail -1); local pe0=$(awk '/^ *0 /{print $3}' log.$1 | tail -1); local nat=$(awk '/Loop time/{print $12}' log.$1)
    local styles=$(grep -m1 "pair_style" log.$1 | cut -c1-60)
    printf "| %s | %s | %s | %s | %s | %.1f |\n" "$tag" "$nat" "$pe0" "$pe" "$(grep -c 'KOKKOS' log.$1)" "$(echo "$t1 - $t0" | bc)" >> $OUT
  else
    echo "| $tag | FAILED (see log.$tag) | | | | |" >> $OUT
  fi
}
echo "| run | atoms | PE step 0 (eV) | PE step 50 (eV) | KOKKOS lines in log | wall (s) |" >> $OUT; echo "|---|---|---|---|---|---|" >> $OUT
run fs_cpu1_n4   4 1 $FS  0 1
run fs_gpu_n4    4 1 $FS  1 1
run hyb_gpu_n4   4 3 $FS  1 1
run hyb_cpu1_n4  4 3 $FS  0 1
run 1l_gpu_n4    4 2 $NPZ 1 1
run fs_cpu4_n8   8 1 $FS  0 4
run fs_gpu_n8    8 1 $FS  1 1
run hyb_cpu4_n8  8 3 $FS  0 4
run hyb_gpu_n8   8 3 $FS  1 1
run 1l_gpu_n8    8 2 $NPZ 1 1
echo; echo "== styles in the binary"; "$LMP" -h | grep -o "grace[a-z0-9/]*\|hybrid/scaled[a-z/]*\|pace[a-z/]*\|ufm[a-z/]*" | sort -u | tr '\n' ' '; echo
cat $OUT
