import sys
from lammps import lammps
from lammps.mliap import activate_mliappy, load_unified
from lammps.mliap.mliap_unified_lj import MLIAPUnifiedLJ
def setup(lmp, pair):
    lmp.commands_string(f"""
units lj
atom_style atomic
lattice fcc 0.8442
region box block 0 5 0 5 0 5
create_box 1 box
create_atoms 1 box
mass 1 1.0
displace_atoms all random 0.05 0.05 0.05 1234
{pair}
thermo_style custom step pe press pxx pxy
run 0
""")
    return lmp.get_thermo("pe"), lmp.get_thermo("press"), lmp.get_thermo("pxy")
res={}
for name,pair in [("ljcut","pair_style lj/cut 2.5\npair_coeff * * 1 1"),
                  ("mliap","pair_style mliap unified EXISTS 0\npair_coeff * * Ar"),
                  ("hs1","variable lam equal 1.0\npair_style hybrid/scaled v_lam mliap unified EXISTS 0\npair_coeff * * mliap Ar"),
                  ("hs1222","variable lam equal 1.222\npair_style hybrid/scaled v_lam mliap unified EXISTS 0\npair_coeff * * mliap Ar"),
                  ("hsmix","pair_style hybrid/scaled 0.6 mliap unified EXISTS 0 0.4 lj/cut 2.5\npair_coeff * * mliap Ar\npair_coeff * * lj/cut 1 1")]:
    lmp = lammps(cmdargs=["-log","none","-screen","none"])
    if "mliap" in pair:
        activate_mliappy(lmp)
        load_unified(MLIAPUnifiedLJ(["Ar"], rcutfac=1.25))
    res[name]=setup(lmp,pair); lmp.close()
for k,v in res.items(): print(f"{k:8s} pe={v[0]:.8f} press={v[1]:.8f} pxy={v[2]:.8f}")
