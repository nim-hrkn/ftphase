units metal
boundary p p p
atom_style atomic
atom_modify map yes
newton on
read_data conf.data
mass 1 26.9815
mass 2 6.94
thermo_style custom step pe press pxx pxy vol
variable lam equal 1.0
if "${v} == 0" then "pair_style mliap unified ${pot} 0" "pair_coeff * * Al Li"
if "${v} == 1" then "pair_style hybrid/scaled v_lam mliap unified ${pot} 0" "pair_coeff * * mliap Al Li"
if "${v} == 2" then "variable lam equal 1.222222" "pair_style hybrid/scaled v_lam mliap unified ${pot} 0" "pair_coeff * * mliap Al Li"
if "${v} == 3" then "variable f1 equal 0.7" "variable f2 equal 0.3" "pair_style hybrid/scaled v_f1 mliap unified ${pot} 0 v_f2 ufm 7.5" "pair_coeff * * mliap Al Li" "pair_coeff * * ufm 0.1 1.5 7.5"
run 0
change_box all x final 0.0 12.851 y final 0.0 12.851 z final 0.0 12.851 remap units box
run 0
velocity all create 600.0 4928459 loop geom
fix 1 all nve
timestep 0.001
run 20
run 100
