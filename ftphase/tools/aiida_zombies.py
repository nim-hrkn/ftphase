"""Find (and optionally cancel) Slurm jobs and CalcJob processes left behind by killed/finished WorkChains.

`verdi process kill <workchain> -F` does not reliably propagate to child CalcJobs: they stay 'waiting' and their Slurm
jobs keep running or queued on the computers (80 such jobs were found on 2026-10-25, two of them hogging the GPUs for
hours).  Usage:

    env/ftphase/bin/python ftphase/tools/aiida_zombies.py            # list only
    env/ftphase/bin/python ftphase/tools/aiida_zombies.py --cancel   # scancel those jobs and kill the orphan CalcJobs
"""

import re
import subprocess
import sys

from aiida import load_profile
from aiida.orm import CalcJobNode, QueryBuilder, load_node

HOSTS = {"mygarden5": None, "mygarden6": "mygarden6", "mygardenx2": "mygardenx2"}   # computer label -> ssh alias (None = local)
TERMINATED = ("killed", "excepted", "finished")


def squeue(alias):
    cmd = ["squeue", "-h", "-o", "%i %j %T"] if alias is None else ["ssh", "-o", "ConnectTimeout=8", alias, "squeue -h -o '%i %j %T'"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception as e:  # noqa: BLE001
        print(f"{alias}: squeue failed: {e}")
        return []
    return [line.split() for line in out.split("\n") if line.strip()]


def main():
    cancel = "--cancel" in sys.argv
    load_profile("ftphase")
    # 1) orphan CalcJobs: not terminated while their caller is
    qb = QueryBuilder().append(CalcJobNode, filters={"attributes.process_state": {"in": ["waiting", "running", "created"]}}, project=["*"])
    orphans = [n for (n,) in qb.all() if n.caller is not None and n.caller.process_state.value in TERMINATED]
    print(f"orphan CalcJobs (caller terminated): {len(orphans)}")
    for n in orphans[:20]:
        print(f"  pk {n.pk} {n.label} on {n.computer.label} state {n.process_state.value}; caller {n.caller.pk} {n.caller.process_state.value}")
    # 2) Slurm jobs named aiida-<pk> whose process or caller is terminated
    for label, alias in HOSTS.items():
        bad = []
        for jid, name, st in squeue(alias):
            m = re.match(r"aiida-(\d+)$", name)
            if not m:
                continue
            try:
                n = load_node(int(m.group(1)))
            except Exception:  # noqa: BLE001
                continue
            ps = n.process_state.value
            cs = n.caller.process_state.value if n.caller else "?"
            if ps in TERMINATED or cs in TERMINATED:
                bad.append((jid, name, st))
        print(f"{label}: {len(bad)} Slurm jobs of terminated processes" + ("" if not bad else ": " + ", ".join(f"{j}({s})" for j, _, s in bad[:8]) + (" ..." if len(bad) > 8 else "")))
        if cancel and bad:
            ids = [b[0] for b in bad]
            subprocess.run(["scancel", *ids] if alias is None else ["ssh", alias, "scancel " + " ".join(ids)])
            print(f"  cancelled {len(ids)}")
    if cancel and orphans:
        verdi = sys.executable.rsplit("/", 1)[0] + "/verdi"
        subprocess.run([verdi, "-p", "ftphase", "process", "kill", "-F", "-t", "30", *[str(n.pk) for n in orphans]])


if __name__ == "__main__":
    main()
