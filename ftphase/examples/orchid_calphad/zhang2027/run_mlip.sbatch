#!/bin/bash
#SBATCH -p debug -J zhang-mlip -N 1 -n 1 --cpus-per-task=4 --gres=gpu:1 --mem=16G
# usage: sbatch run_mlip.sbatch <env name under env/> <calc kind> <model path or name> <outdir name>
set -u
P=/home/kino/kino/Claude/Projects/PhaseDiagram
ENV=$1; CALC=$2; MODEL=$3; OUT=$4
unset PYTHONPATH PYTHONHOME
export MPLBACKEND=Agg OMP_NUM_THREADS=4
cd $P/ftphase/examples/orchid_calphad/zhang2027
exec $P/env/$ENV/bin/python -I run_mlip.py $P/data/Zhang2027/zenodo-phase-diagrams mlip_runs/$OUT --calc $CALC --model "$MODEL" --device cuda
