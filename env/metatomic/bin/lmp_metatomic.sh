#!/bin/bash
# wrapper for env/metatomic/bin/lmp: `pair_style metatomic` (and its /kk variant) segfaults when issued before the box exists
# (calphy's executable runner writes pair_style before read_data in the first segment; 2026-11-06). Any pair_style line that
# precedes the first read_data/read_restart in the -in script is moved to directly after that line; later segments already
# start with read_restart and need no change.
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [ "${args[$i]}" = "-in" ] && [ -f "${args[$((i+1))]}" ]; then
    f="${args[$((i+1))]}"; t="${f}.mta.lmp"
    awk '
      BEGIN { seen = 0; n = 0 }
      !seen && $1 == "pair_style" { held[n++] = $0; next }
      { print }
      !seen && ($1 == "read_data" || $1 == "read_restart") { seen = 1; for (k = 0; k < n; k++) print held[k] }
      END { if (!seen) for (k = 0; k < n; k++) print held[k] }
    ' "$f" > "$t"; args[$((i+1))]="$t"
  fi
done
exec /home/kino/kino/Claude/Projects/PhaseDiagram/env/metatomic/bin/lmp "${args[@]}"
