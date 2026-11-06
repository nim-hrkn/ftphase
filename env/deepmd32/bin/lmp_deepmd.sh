#!/bin/bash
# wrapper for the PyPI LAMMPS (22Jul2025u2, PLUGIN) of env/deepmd32 with the deepmd-kit 3.2.0 plugin: `plugin load` is
# prepended to every -in script (calphy's runner rejects it as an init command), libraries on LD_LIBRARY_PATH.
# pair_style deepmd <model.pth> runs the PyTorch model on the GPU by itself; LAMMPS integrates on the CPU.
R=/home/kino/kino/Claude/Projects/PhaseDiagram/env/deepmd32
SP=$R/lib/python3.12/site-packages
# drop Intel oneAPI entries (its old libfabric breaks the pip mpich's libmpi.so.12: "version FABRIC_1.9 not found")
CLEAN=$(echo "${LD_LIBRARY_PATH:-}" | tr ':' '\n' | grep -v '/opt/intel' | paste -sd: -)
export LD_LIBRARY_PATH=$SP/deepmd/lib:$SP/torch/lib:$R/lib${CLEAN:+:$CLEAN}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4} DP_INTRA_OP_PARALLELISM_THREADS=${DP_INTRA_OP_PARALLELISM_THREADS:-4} DP_INTER_OP_PARALLELISM_THREADS=${DP_INTER_OP_PARALLELISM_THREADS:-1}
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [ "${args[$i]}" = "-in" ] && [ -f "${args[$((i+1))]}" ]; then
    f="${args[$((i+1))]}"; t="${f}.dp.lmp"
    { echo "plugin load $SP/deepmd/lib/libdeepmd_lmpplugin.so"; cat "$f"; } > "$t"; args[$((i+1))]="$t"
  fi
done
exec $R/bin/lmp "${args[@]}"
