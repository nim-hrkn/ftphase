# GRACE smoke test: fcc Al0.7Li0.3 random, ${n}^3 conventional cells, 50 NVE steps
# variables: n (cells per side), style (1 = grace/fs, 2 = grace/1l, 3 = hybrid/scaled grace/fs + ufm), pot (model file); run with or without -k on g 1 -sf kk
units           metal
boundary        p p p
atom_style      atomic
lattice         fcc 4.05
region          box block 0 ${n} 0 ${n} 0 ${n}
create_box      2 box
create_atoms    1 box
set             type 1 type/fraction 2 0.3 12345
mass            1 26.98
mass            2 6.94
if "${style} == 1" then &
  "pair_style grace/fs" &
  "pair_coeff * * ${pot} Al Li"
if "${style} == 2" then &
  "pair_style grace/1l" &
  "pair_coeff * * ${pot} Al Li"
if "${style} == 3" then &
  "variable f1 equal 0.7" &
  "variable f2 equal 0.3" &
  "pair_style hybrid/scaled v_f1 grace/fs v_f2 ufm 7.5" &
  "pair_coeff * * grace/fs ${pot} Al Li" &
  "pair_coeff * * ufm 0.1 1.5 7.5"
velocity        all create 600.0 4928459 loop geom
fix             1 all nve
timestep        0.001
thermo          10
thermo_style    custom step temp pe press cpu
run             50
