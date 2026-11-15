#!/bin/bash
# Bayesian update of the Ru-Si diagram for one TDB:  run_model.sh <name> <tdb> "<label>" [cores]
# -> bayes/runs/<name>/{rusi-start.tdb, mcmc.yaml, trace.npy, out/summary.json, out/fig4_lines.png}
H=$(cd "$(dirname "$0")" && pwd); PY=$H/../../../../../env/pycalphad/bin
name=$1; tdb=$(readlink -f "$2"); export BAYES_LABEL="$3"; cores=${4:-10}; export BAYES_DIR=$H/runs/$name
mkdir -p $BAYES_DIR && cd $BAYES_DIR || exit 1
$PY/python $H/build_inputs.py --tdb "$tdb" --iterations 3000 --cores $cores > build.log 2>&1 || { echo "$name build failed"; exit 1; }
$PY/espei --input mcmc.yaml > mcmc.stdout 2>&1 || { echo "$name mcmc failed"; exit 1; }
$PY/python $H/posterior.py --n 1000 --workers $cores > posterior.log 2>&1 || { echo "$name posterior failed"; exit 1; }
$PY/python $H/invariants.py > invariants.log 2>&1 || { echo "$name invariants failed"; exit 1; }
echo "$name done $(date)"
