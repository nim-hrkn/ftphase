# ptrh_nequip_oam_m: low-T solids-only re-assembly (100-1900 K, 10 K)

Classical level, liquid rows dropped, same fits/entropy models as the WorkChain spec.

## Highest temperature with the ordered phase in a two-phase region

* PtRh: 200.0
* PtRh3: 1180.0
* Pt3Rh: 1900.0

## Invariant reactions (pair-set changes)

* 100-110 K: ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh3+PtRh3', 'PtRh3+fcc'] -> ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh3+fcc']
* 170-180 K: ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc']
* 190-200 K: ['Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc']
* 200-210 K: ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc']
* 530-540 K: ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['PtRh3+fcc', 'fcc+fcc']
* 1180-1190 K: ['PtRh3+fcc', 'fcc+fcc'] -> ['fcc+fcc']
* 1730-1740 K: ['fcc+fcc'] -> ['Pt3Rh+fcc', 'fcc+fcc']

## Same-phase segments (fit noise)

* PtRh+PtRh x = 0.438-0.562 at 100 K
* PtRh3+PtRh3 x = 0.656-0.812 at 100 K
* fcc+fcc x = 0.473-0.480 at 200 K
* fcc+fcc x = 0.473-0.480 at 210 K
* fcc+fcc x = 0.473-0.480 at 220 K
* fcc+fcc x = 0.473-0.480 at 230 K
* fcc+fcc x = 0.473-0.480 at 240 K
* fcc+fcc x = 0.473-0.480 at 250 K
* fcc+fcc x = 0.473-0.480 at 260 K
* fcc+fcc x = 0.473-0.480 at 270 K
* fcc+fcc x = 0.473-0.480 at 280 K
* fcc+fcc x = 0.473-0.480 at 290 K
* fcc+fcc x = 0.473-0.480 at 300 K
* fcc+fcc x = 0.473-0.480 at 310 K
* fcc+fcc x = 0.473-0.480 at 320 K
* fcc+fcc x = 0.473-0.480 at 330 K
* fcc+fcc x = 0.473-0.480 at 340 K
* fcc+fcc x = 0.473-0.480 at 350 K
* fcc+fcc x = 0.473-0.480 at 360 K
* fcc+fcc x = 0.473-0.480 at 370 K
* two-phase regions at 150 K: fcc(0.000)-Pt3Rh(0.188); Pt3Rh(0.188)-PtRh(0.438); PtRh(0.438)-PtRh3(0.812); PtRh3(0.812)-fcc(0.943)
* two-phase regions at 200 K: fcc(0.003)-Pt3Rh(0.188); Pt3Rh(0.188)-fcc(0.348); fcc(0.425)-PtRh(0.438); PtRh(0.438)-fcc(0.453); fcc(0.473)-fcc(0.480); fcc(0.500)-PtRh3(0.812); PtRh3(0.812)-fcc(0.940)
* two-phase regions at 300 K: fcc(0.003)-Pt3Rh(0.188); Pt3Rh(0.188)-fcc(0.328); fcc(0.473)-fcc(0.480); fcc(0.525)-PtRh3(0.812); PtRh3(0.812)-fcc(0.932)
* two-phase regions at 500 K: fcc(0.003)-Pt3Rh(0.188); Pt3Rh(0.188)-fcc(0.297); fcc(0.473)-fcc(0.480); fcc(0.562)-PtRh3(0.812); PtRh3(0.812)-fcc(0.920)
* two-phase regions at 1000 K: fcc(0.000)-fcc(0.375); fcc(0.473)-fcc(0.480); fcc(0.680)-PtRh3(0.812); PtRh3(0.812)-fcc(0.890)
