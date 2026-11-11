# Al-Li: phase-label accuracy of each run against SGTE AlLi-20Lon (grid 10 K x 100 compositions, 300 K .. top of the run's window)

| run | all (masked: x > 0.5 above the liquid window) | Al side, liquid window | solids below the liquid window |
|---|---|---|---|
| ACE (aiida, x<=0.5) | 0.644 | 0.400 | 0.760 |
| GRACE-FS-OAM | 0.364 | 0.359 | 0.367 |
| GRACE-1L-OMAT | 0.329 | 0.306 | 0.335 |
| GRACE-2L-OMAT | 0.564 | 0.397 | 0.622 |
| SevenNet-0 | 0.399 | 0.482 | 0.362 |
| SevenNet-MF-ompa | 0.620 | 0.638 | 0.612 |
| MACE-MPA-0 | 0.533 | 0.389 | 0.598 |
| MatterSim-v1-1M | 0.338 | 0.170 | 0.365 |
| MatterSim-v1-5M | 0.343 | 0.224 | 0.395 |
| NequIP-OAM-M | 0.541 | 0.591 | 0.523 |
| NequIP-OAM-S | 0.424 | 0.471 | 0.404 |
| DPA4-Plus-OMat24 | 0.427 | 0.419 | 0.431 |
| DPA-4.1-Air-OAM | 0.442 | 0.535 | 0.401 |
