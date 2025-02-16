# Dialysis Prescription Calculator

The "Clearance" section is dedicated to prescription calculations. By inputting the data shown in Table 1 and clicking "Calculate," the required dialyzer urea clearance (Kdn) to achieve the target eKt/V is determined. The necessary blood flow rate (Qbn) to attain the calculated Kdn is also computed, considering the dialyzer's characteristics (KoA) and other operational parameters (QD, UF, HDFPRE, HDFPOST).

The calculations are based on the same equations used in the "SPEEDY" software, as described by Casino and Basile in "A user-friendly tool for incremental haemodialysis prescription. Nephrol Dial Transplant. 2018;33(6): 1046-1053. [https://doi.org/10.1093/ndt/gfx343](https://doi.org/10.1093/ndt/gfx343)"

## Table 1: Input Data

| # | Input                                     | Symbol | Units    | Min | Max | Example |
|---|-------------------------------------------|--------|----------|-----|-----|---------|
| 1 | Patient ID                                | PTID   |          |     |     | PTID    |
| 2 | Patient’s urea volume                     | V      | L        | 20  | 50  | 35      |
| 3 | Expected intradialysis weight loss        | UF     | L or kg  | 0.1 | 5   | 2       |
| 4 | KoA in vitro of the dialyzer             | KoA    | ml/min   | 600 | 2000| 1200    |
| 5 | Pre-dialyzer infusion rate                | HDFPRE | ml/min   | 0   | 250 | 0       |
| 6 | Post-dialyzer infusion rate               | HDFPOST| ml/min   | 0   | 150 | 0       |
| 7 | Dialysate flow rate                       | QD     | ml/min   | 100 | 1000| 500     |
| 8 | Session length                            | TD     | Min      | 60  | 480 | 240     |
| 9 | eKt/V target of the current prescription | eKt/V  | dimensionless | 0.3 | 2.0 | 1.4     |

## Table 2: Output Data

| #  | Output                                          | Symbol | Units    | Min | Max | Example |
|----|-------------------------------------------------|--------|----------|-----|-----|---------|
| 10 | Dialyzer Urea Clearance needed to attain the eKt/V target * | Kdn    | ml/min   | 100 | 300 | 239     |
| 11 | Blood flow rate needed to attain the required Kdn value * | Qbn    | ml/min   | 100 | 450 | 351     |

* The calculated values for Kdn and Qbn are theoretical estimates under ideal conditions. The actual values can be influenced by various factors, such as the measurement method used, variability of blood and dialysis flows, presence of vascular access recirculation, etc.
