# EuReCa (Clearance Calculator) — Complete Project Documentation

## Table of Contents

1. [Introduction & Clinical Background](#1-introduction--clinical-background)
2. [System Architecture](#2-system-architecture)
3. [Detailed Module & Mathematical Reference](#3-detailed-module--mathematical-reference)
   - [Module 1: Adequacy (`adequacy`)](#31-module-1-adequacy-adequacy)
   - [Module 2: stdKt/V & EKRU (`assessment`)](#32-module-2-stdktv--ekru-assessment)
   - [Module 3: Dose Calculator (`prescription`)](#33-module-3-dose-calculator-prescription)
   - [Module 4: Kd&Qb (`clearance`)](#34-module-4-kdqb-clearance)
   - [Module 5: KoA (`koa`)](#35-module-5-koa-koa)
4. [Batch Excel Processing Feature](#4-batch-excel-processing-feature)
   - [Excel Template Structure](#41-excel-template-structure)
   - [Row Iteration, Validation & Progress Bar](#42-row-iteration-validation--progress-bar)
   - [Output Excel Structure](#43-output-excel-structure)
5. [Codebase API Reference](#5-codebase-api-reference)
6. [Testing & Verification Guide](#6-testing--verification-guide)
7. [Scientific References](#7-scientific-references)

---

## 1. Introduction & Clinical Background

**EuReCa** (*European Renal Calculator*, hosted at [https://clearance.streamlit.app/](https://clearance.streamlit.app/)) is a clinical decision-support tool designed for nephrologists managing adult patients on maintenance haemodialysis (HD) and **incremental haemodialysis (iHD)**.

In patients initiating kidney replacement therapy with preserved residual kidney function (RKF), expressed as residual renal urea clearance ($KRU$), incremental HD starts with a reduced session frequency (1 or 2 sessions/week) and/or reduced dialysis dose ($eKt/V$), adjusting the prescription as $KRU$ declines over time.

Total weekly urea removal (dialysis + native kidneys) is quantified using an **Equivalent Continuous Clearance (ECC)**:
- **Standard $Kt/V$ ($\text{stdKt/V}$)**: Target $= 2.3\text{ volumes/week}$, minimum adequate threshold $\ge 2.1\text{ volumes/week}$ (KDOQI 2015).
- **Normalized Equivalent Renal Urea Clearance ($\text{EKRUN}$)**: Normalized to a typical urea distribution volume of $35\text{ L}$ ($\text{EKRUN} = \text{EKRU} / V \times 35$). Under the Variable Target Model (Casino & Basile):
  - Prescription target: $\text{EKRUN}_{\text{target}} = 12 - \text{KRUN}$
  - Minimum adequate threshold: $\text{EKRUN}_{\min} = 10 - 1.5 \times \text{KRUN}$

---

## 2. System Architecture

The application follows a modular two-layer architecture separating **Streamlit presentation pages** (`pages/`) from **calculation & file-processing components** (`components/`):

```text
main.py
 ├── pages/home.py               (Tab 1: Home)
 ├── pages/key_information.py    (Tab 2: Key Information)
 ├── pages/adequacy.py           (Tab 3: Adequacy)
 │    ├── components/adequacy.py
 │    ├── components/pdf_builder.py
 │    └── components/batch_ui.py ──► components/excel_handler.py
 ├── pages/assessment.py         (Tab 4: stdKt/V & EKRU)
 │    ├── components/assessment_calculator.py
 │    ├── components/pdf_builder.py
 │    └── components/batch_ui.py ──► components/excel_handler.py
 ├── pages/prescription.py       (Tab 5: Dose Calculator)
 │    ├── components/prescription_calculator.py
 │    ├── components/pdf_builder.py
 │    └── components/batch_ui.py ──► components/excel_handler.py
 ├── pages/clearance.py          (Tab 6: Kd&Qb)
 │    ├── components/kdn_calculator.py
 │    ├── components/pdf_builder.py
 │    └── components/batch_ui.py ──► components/excel_handler.py
 └── pages/koa.py                (Tab 7: KoA)
      ├── components/koa_calculator.py
      └── components/batch_ui.py ──► components/excel_handler.py
```

---

## 3. Detailed Module & Mathematical Reference

### 3.1 Module 1: Adequacy (`adequacy`)

- **UI Page:** [`pages/adequacy.py`](../pages/adequacy.py)
- **Calculation Engine:** [`ihd_calculation(inputs)`](../components/adequacy.py)
- **Excel Template:** [`templates/adequacy_template.xlsx`](../templates/adequacy_template.xlsx)

#### Input Parameters (`Inputs` Sheet)

| # | Column | Description | Symbol | Units | Min | Max | Example | Notes |
|---|--------|-------------|--------|-------|-----|-----|---------|-------|
| 1 | `PTID` | Patient Identifier | PTID | text | - | - | `Patient_01` | Required |
| 2 | `LABDATE` | Lab Date | Lab date | dd/mm/yyyy | - | - | `03/02/2025` | Required |
| 3 | `UNIT` | Concentration Unit | Unit | `BUN_mg_dl` \| `Urea_mg_dl` \| `Urea_mmol_l` | - | - | `BUN_mg_dl` | Conversion factor `BUN`: `1.0`, `2.14`, or `0.357` |
| 4 | `NHDWK` | Number of HD sessions per week | NHDWK | sessions/wk | 1 | 3 | `1` | Integer: 1, 2, or 3 |
| 5 | `PIDI` | Preceding inter-dialytic interval | PIDI | days | 2 | 7 | `7` | `7` if NHDWK=1; `3,4` if NHDWK=2; `2,3` if NHDWK=3 |
| 6 | `BW0` | Pre-dialysis Body Weight | BW0 | kg | 20.0 | 140.0 | `71.0` | Required |
| 7 | `BWT` | Post-dialysis Body Weight | BWT | kg | 20.0 | 140.0 | `70.0` | Required |
| 8 | `T` | Session length | TD | min | 60 | 480 | `240` | Required |
| 9 | `QB` | Blood Flow Rate | Qb | ml/min | 100 | 450 | `300` | Required |
| 10 | `HDFPRE` | Pre-dilution infusion rate | HDFpre | ml/min | 0 | 250 | `0` | Set 0 in HD or post-HDF |
| 11 | `HDFPOST` | Post-dilution infusion rate | HDFpost | ml/min | 0 | 150 | `0` | Set 0 in HD or pre-HDF |
| 12 | `QD` | Dialysate flow rate | Qd | ml/min | 300 | 800 | `500` | Required |
| 13 | `Manufacturer` | Dialyzer Manufacturer | Manufacturer | text | - | - | `Fresenius` | Optional if `KOAvitro` provided |
| 14 | `Model` | Dialyzer Model | Model | text | - | - | `FX10` | Optional if `KOAvitro` provided |
| 15 | `KOAvitro` | Dialyzer Urea KoA in vitro | KoA | ml/min | 500 | 2400 | `977` | Auto-resolved if Manufacturer & Model match `Dialyzers` |
| 16 | `C0` | Pre-dialysis Blood Urea/BUN | C0 | mg/dl or mmol/l | `20*BUN` | `200*BUN` | `80.0` | Required |
| 17 | `CT` | Post-dialysis Blood Urea/BUN | CT | mg/dl or mmol/l | `5*BUN` | `199*BUN` | `25.0` | Must be `< C0` |
| 18 | `UO` | Urinary Output | UO | ml/24h | 0 | 4000 | `1000` | Set 0 if anuric or entering KRUw directly |
| 19 | `UUN` | Urinary Urea or BUN | UU(N) | mg/dl or mmol/l | 0.0 | `1000*BUN` | `300.0` | Set 0 if entering KRUw directly |
| 20 | `KRUw` | Renal urea clearance | KRU | ml/min | 0 | 999 | `999` | Enter `999` to calculate from `UO` & `UUN`, else `0..7` |

#### Output Parameters (`Results` Sheet)

| # | Column | Description | Symbol | Units |
|---|--------|-------------|--------|-------|
| 1 | `KTOT` | Total Dialyzer Urea Clearance | Kd Tot | ml/min |
| 2 | `SPKTV` | Single pool Kt/V | spKt/V | dimensionless |
| 3 | `EKTV` | Equilibrated Kt/V | eKt/V | dimensionless |
| 4 | `VDP` | Urea distribution volume (double pool) | Vdp | l |
| 5 | `PCRN` | Protein catabolic rate | PCRn | g/kg/day |
| 6 | `Kru` | Renal urea clearance (calculated) | KRU | ml/min |
| 7 | `krun` | KRU normalized per V 35 l | KRUN | ml/min per 35l V |
| 8 | `ekrun` | Equivalent Renal Urea Clearance per V 35 l | EKRUN | ml/min per 35l V |
| 9 | `ekrun_min` | EKRUN variable target ($10 - 1.5 \times \text{KRUN}$) | EKRU_VTM | ml/min per 35l V |
| 10 | `AdeqEKR` | $\text{EKRUN} \ge 10 - 1.5 \times \text{KRUN}$ | Adequacy | Yes/No |
| 11 | `STDKTV` | Standard Kt/V | StdKt/V | Volume/wk |
| 12 | `AdeqStdKTV` | $\text{StdKt/V} \ge 2.1$ | Adequacy | Yes/No |
| 13 | `UFR` | Ultrafiltration rate | UFR | ml/h per kg |
| 14 | `AdeqUFR` | $\text{UFR} \le 13\text{ ml/h/kg}$ | Adequacy | Yes/No |
| 15 | `TDN` | Session duration needed for $\text{UFR}=13\text{ ml/h/kg}$ | TDN | min per session |
| 16 | `Ufwk` | Weekly net Ultrafiltration | UFwk | l |
| 17 | `Ektv_ekru` | $eKt/V$ to get $\text{EKRUN} = 12 - \text{KRUN}$ | eKt/V | dimensionless |
| 18 | `Ektv_stdktv` | $eKt/V$ to get $\text{stdKt/V} = 2.3$ | eKt/V | dimensionless |
| 19–30 | `ektv_s1`, `spktv_s1`, `ektv_E1`, `spktv_E1`, `ektv_s2`, `spktv_s2`, `ektv_E2`, `spktv_E2`, `ektv_s3`, `spktv_s3`, `ektv_E3`, `spktv_E3` | Simulated $eKt/V$ and $spKt/V$ ($= 1.128 \times eKt/V$) prescriptions for 1, 2, and 3 HD/week to reach $\text{stdKt/V}$ and $\text{EKRUN}$ targets | eKt/V, spKt/V | dimensionless |

---

### 3.2 Module 2: stdKt/V & EKRU (`assessment`)

- **UI Page:** [`pages/assessment.py`](../pages/assessment.py)
- **Calculation Engine:** [`assessment_calculation(inputs)`](../components/assessment_calculator.py)
- **Excel Template:** [`templates/stdktv_ekru_template.xlsx`](../templates/stdktv_ekru_template.xlsx)

#### Input Parameters

| # | Column | Description | Symbol | Units | Min | Max | Example |
|---|--------|-------------|--------|-------|-----|-----|---------|
| 1 | `PTID` | Patient Identifier | PTID | text | - | - | `Patient_01` |
| 2 | `NHDWK` | Number of HD per week | NHDWK | number | 1 | 3 | `1` |
| 3 | `KRUN` | Normalised Kru | KRUN | ml/min per 35l V | 0.0 | 7.0 | `4.0` |
| 4 | `EKTV` | Delivered eKt/V | eKt/V | dimensionless | 0.5 | 2.0 | `1.2` |
| 5 | `PIDI` | Preceding interdialytic interval | PIDI | days | 1 | 7 | `7` |
| 6 | `IDWG` | Weight gain during PIDI | IDWG | kg | 0.0 | 5.0 | `1.0` |

#### Output Parameters

| # | Column | Description | Symbol | Units |
|---|--------|-------------|--------|-------|
| 1 | `ufwk` | Weekly net Ultrafiltration ($\text{IDWG} / \text{PIDI} \times 7$) | UFwk | l |
| 2 | `stdktv` | Standard Kt/V | stdKt/V | v/wk |
| 3 | `ekrun` | Normalised Equivalent Renal Urea Clearance | EKRUN | ml/min per 35 l V |
| 4 | `12_minus_krun` | EKRUN variable target ($12 - \text{KRUN}$) | EKRUN_VTM | ml/min per 35 l V |
| 5 | `10_minus_1.5_krun` | EKRUN minimum adequate ($10 - 1.5 \times \text{KRUN}$) | EKRUN_min | ml/min per 35 l V |

---

### 3.3 Module 3: Dose Calculator (`prescription`)

- **UI Page:** [`pages/prescription.py`](../pages/prescription.py)
- **Calculation Engine:** [`prescription_calculation(inputs)`](../components/prescription_calculator.py)
- **Excel Template:** [`templates/dose_calculator_template.xlsx`](../templates/dose_calculator_template.xlsx)

#### Input Parameters

| # | Column | Description | Symbol | Units | Min | Max | Example |
|---|--------|-------------|--------|-------|-----|-----|---------|
| 1 | `PTID` | Patient Identifier | PTID | text | - | - | `Patient_01` |
| 2 | `NHDWK` | Number of HD per week | NHDWK | number | 1 | 3 | `2` |
| 3 | `KRUN` | Normalised Kru | KRUN | ml/min per 35l V | 0.0 | 7.0 | `3.0` |
| 4 | `PIDI` | Preceding interdialytic interval | PIDI | days | 1 | 7 | `4` |
| 5 | `IDWG` | Weight gain during PIDI | IDWG | kg | 0.0 | 5.0 | `1.0` |

#### Output Parameters

| # | Column | Description | Symbol | Units |
|---|--------|-------------|--------|-------|
| 1 | `ufwk` | Weekly net Ultrafiltration | UFwk | l |
| 2 | `ektv_ekru` | $eKt/V$ to get $\text{EKRUN} = 12 - \text{KRUN}$ | eKt/V (EKRUN) | dimensionless |
| 3 | `ektv_stdktv` | $eKt/V$ to get $\text{stdKt/V} = 2.3$ | eKt/V (stdKt/V) | dimensionless |

---

### 3.4 Module 4: Kd&Qb (`clearance`)

- **UI Page:** [`pages/clearance.py`](../pages/clearance.py)
- **Calculation Engine:** [`calculate_kdn_qbwn(vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt)`](../components/kdn_calculator.py)
- **Excel Template:** [`templates/kd_qb_template.xlsx`](../templates/kd_qb_template.xlsx)

#### Input Parameters

| # | Column | Description | Symbol | Units | Min | Max | Example |
|---|--------|-------------|--------|-------|-----|-----|---------|
| 1 | `PTID` | Patient Identifier | PTID | text | - | - | `Patient_01` |
| 2 | `DATE` | Date | date | dd/mm/yyyy | - | - | `03/02/2025` |
| 3 | `VDP` | Patient's urea volume | V | L | 20.0 | 50.0 | `35.0` |
| 4 | `UF` | Expected intradialysis weight loss | UF | L | 0.1 | 5.0 | `2.0` |
| 5 | `Manufacturer` | Dialyzer Manufacturer | Manufacturer | text | - | - | `Fresenius` |
| 6 | `Model` | Dialyzer Model | Model | text | - | - | `FX80` |
| 7 | `KOAvitro` | In vitro KoA of the dialyzer | KoA | ml/min | 500 | 2400 | `900` |
| 8 | `HDFPRE` | Pre-dilution infusion rate | HDFPRE | ml/min | 0 | 250 | `0` |
| 9 | `HDFPOST` | Post-dilution infusion rate | HDFPOST | ml/min | 0 | 150 | `0` |
| 10 | `QD` | Dialysate Flow rate | QD | ml/min | 301 | 800 | `500` |
| 11 | `T` | Session length | T | min | 60 | 480 | `210` |
| 12 | `EKVT` | eKt/V target | eKt/V | dimensionless | 0.3 | 2.0 | `1.2` |

#### Output Parameters

| # | Column | Description | Symbol | Units |
|---|--------|-------------|--------|-------|
| 1 | `kdn` | Dialyzer urea clearance needed | Kdn | ml/min |
| 2 | `qbn` | Blood flow rate needed | Qbn | ml/min |
| 3 | `Warning` | Clinical warning if `qbn > 400` ml/min | Warning | text |

---

### 3.5 Module 5: KoA (`koa`)

- **UI Page:** [`pages/koa.py`](../pages/koa.py)
- **Calculation Engine:** [`koa(qb, qd, qf, kd)`](../components/koa_calculator.py)
- **Excel Template:** [`templates/koa_template.xlsx`](../templates/koa_template.xlsx)

#### Equations

$$K_{\text{conv}} = \frac{Q_b - K_d}{K_d} \cdot Q_f, \qquad K_{\text{dif}} = K_d - K_{\text{conv}}$$

$$KoA = \frac{Q_b}{1 - Q_b / Q_d} \cdot \ln\left(\frac{1 - K_{\text{dif}} / Q_d}{1 - K_{\text{dif}} / Q_b}\right)$$

#### Input Parameters

| # | Column | Description | Symbol | Units | Min | Max | Example |
|---|--------|-------------|--------|-------|-----|-----|---------|
| 1 | `QB` | Blood flow rate | Qb | ml/min | 100 | 300 | `300` |
| 2 | `QD` | Dialysate flow rate | Qd | ml/min | 100 | 1000 | `500` |
| 3 | `QF` | Ultrafiltration rate | Qf | ml/min | 0 | 30 | `0` |
| 4 | `KD` | Dialyzer Urea clearance | Kd | ml/min | 100 | 350 | `250` |

#### Output Parameters

| # | Column | Description | Symbol | Units |
|---|--------|-------------|--------|-------|
| 1 | `kdif` | Diffusive Kd | Kd0 | ml/min |
| 2 | `koa` | KoA of the dialyzer in vitro | KoA | ml/min |

---

## 4. Batch Excel Processing Feature

### 4.1 Excel Template Structure

Every template generated by [`generate_excel_template(tab_key)`](../components/excel_handler.py) (and stored in [`templates/`](../templates/)) is a multi-sheet OpenXML `.xlsx` workbook containing:
1. **`Inputs` Sheet**: Tabular header row matching the exact input parameter symbols/keys for that module, populated with 2 realistic clinical example rows. Users can edit these rows or append any number of rows.
2. **`Legend` Sheet**: Formatted specification table listing every input column, its full clinical description, symbol, measurement unit, minimum and maximum valid bounds, example value, required/optional flag, and validation notes, preceded by general module instructions.
3. **`Output_Legend` Sheet**: Specification table listing every output column produced by the calculator, its description, symbol, and units.
4. **`Dialyzers` Sheet** *(included in `adequacy` and `clearance` templates)*: Full table of 187 dialyzer models from [`Table_of_Dialyzers.csv`](../Table_of_Dialyzers.csv) (`Manufacturer`, `Model`, `KoA`). If a user leaves `KOAvitro` blank in the `Inputs` sheet and enters a valid `Manufacturer` and `Model`, the batch processor automatically looks up and populates `KOAvitro`.

### 4.2 Row Iteration, Validation & Progress Bar

When a user uploads an updated `.xlsx` file in any of the 5 tabs:
1. [`read_xlsx_sheet_rows()`](../components/excel_handler.py) parses all non-empty rows from the `Inputs` sheet (or the first worksheet if renamed).
2. [`process_excel_batch()`](../components/excel_handler.py) iterates through every row sequentially:
   - Calls [`validate_and_compute_row()`](../components/excel_handler.py) to validate all required fields, numeric types, clinical intervals (`PIDI` vs `NHDWK`, `CT < C0`, parameter ranges), and unit conversions.
   - If a row is valid, runs the tab's calculation function (`ihd_calculation`, `assessment_calculation`, `prescription_calculation`, `calculate_kdn_qbwn`, or `koa`) and populates all output columns (`Status = "OK"`).
   - If a row has missing or out-of-range inputs, records `Status = "Error: <specific validation messages>"` without interrupting the rest of the batch.
   - Invokes `progress_callback` after each row to update the Streamlit progress bar (`st.progress`) and status banner with:
     - **Processed rows**: `processed_rows / total_rows`
     - **Remaining (missing to process) rows**: `remaining_rows`
     - **Valid rows**: `valid_rows`
     - **Missing / Invalid data rows**: `missing_or_invalid_rows`

### 4.3 Output Excel Structure

[`generate_excel_output(tab_key, result_rows)`](../components/excel_handler.py) builds a downloadable `.xlsx` workbook containing:
- **`Results` Sheet**: All input columns + `Status` + all calculated output columns for every row.
- **`Output_Legend` Sheet**: Reference table for all output columns.
- **`Input_Legend` Sheet**: Reference table for all input columns and validation rules.

---

## 5. Codebase API Reference

- [`main.py`](../main.py): Entry point configuring the Streamlit page and rendering the 7 tabs.
- [`components/adequacy.py`](../components/adequacy.py):
  - `ihd_calculation(inputs: dict) -> dict`: Double-pool UKM and incremental HD prescription engine.
  - `compute_ektv(a2, b2, d2, e2, krun, ufwk, pidi) -> float`: Helper linear regression formula for target $eKt/V$.
- [`components/assessment_calculator.py`](../components/assessment_calculator.py):
  - `assessment_calculation(inputs: dict) -> dict`: Computes `ufwk`, `stdktv`, `ekrun`, `12_minus_krun`, and `10_minus_1.5_krun`.
- [`components/prescription_calculator.py`](../components/prescription_calculator.py):
  - `prescription_calculation(inputs: dict) -> dict`: Computes `ufwk`, `ektv_ekru`, and `ektv_stdktv`.
- [`components/kdn_calculator.py`](../components/kdn_calculator.py):
  - `calculate_kdn_qbwn(vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt) -> dict | str`: Computes required `kdn` and `qbn`.
- [`components/koa_calculator.py`](../components/koa_calculator.py):
  - `koa(qb, qd, qf, kd) -> tuple[float, float] | str`: Computes `(kdif, koa_value)`.
- [`components/pdf_builder.py`](../components/pdf_builder.py):
  - `create_pdf(input_data, output_data, simulated_data=None, pageBreak=False) -> BytesIO`: Builds single-patient PDF reports using ReportLab.
- [`components/excel_handler.py`](../components/excel_handler.py):
  - `generate_excel_template(tab_key: str, include_sample_rows: bool = True) -> bytes`
  - `validate_and_compute_row(tab_key: str, row_dict: dict, dialyzers_lookup: dict = None) -> dict`
  - `process_excel_batch(tab_key: str, file_or_records, progress_callback=None) -> dict`
  - `generate_excel_output(tab_key: str, result_rows: list[dict]) -> bytes`
  - `save_all_templates_to_directory(directory_path: str = None) -> dict[str, str]`
- [`components/batch_ui.py`](../components/batch_ui.py):
  - `render_batch_section(tab_key: str) -> None`: Renders the template download, file uploader, live progress bar, metrics, results dataframe, and output Excel download button in Streamlit.
- [`components/analytics.py`](../components/analytics.py):
  - `inject_google_analytics(measurement_id: str | None = None) -> bool`: Resolves the GA4 Measurement ID from function parameter, `GA_MEASUREMENT_ID` environment variable, `st.secrets["GA_MEASUREMENT_ID"]`, or `DEFAULT_GA_MEASUREMENT_ID`, patches Streamlit's static `index.html` `<head>` when writable, and injects the `gtag.js` script via `streamlit.components.v1.html`.

---

## 6. Testing & Verification Guide

The automated test suite is located in [`tests/`](../tests/) and can be run with standard `unittest` (or `pytest`):

```bash
python3 -m unittest discover -s tests -v
```

### Test Modules

1. **[`tests/test_calculators.py`](../tests/test_calculators.py)**:
   - Verifies `ihd_calculation`, `assessment_calculation`, `prescription_calculation`, `calculate_kdn_qbwn`, and `koa` against worked clinical examples in `pages/key_information.py`, multiple weekly schedules (1, 2, and 3 HD/week), HDF pre/post dilution modes, and boundary conditions.
2. **[`tests/test_excel_templates_and_batch.py`](../tests/test_excel_templates_and_batch.py)**:
   - Verifies `.xlsx` template generation and legend completeness (`Inputs`, `Legend`, `Output_Legend`, `Dialyzers`) for all 5 tabs.
   - Verifies row validation, automatic `KOAvitro` lookup from `Manufacturer` + `Model`, Excel serial date conversion, concentration unit conversion (`BUN_mg_dl`, `Urea_mg_dl`, `Urea_mmol_l`), and error reporting for missing/invalid data.
   - Verifies multi-row batch execution, step-by-step progress callback updates (`processed_rows`, `remaining_rows`, `valid_rows`, `missing_or_invalid_rows`), and `.xlsx` output generation.
3. **[`tests/test_batch_ui.py`](../tests/test_batch_ui.py)**:
   - Tests the Streamlit UI integration (`render_batch_section`) across all 5 tabs, including template download button rendering, file upload handling, progress bar completion, and output Excel download button rendering.

---

## 7. Scientific References

1. Casino FG, Lopez T, Santarsia G, et al. *Could incremental haemodialysis be a new standard of care? A suggestion from a long-term observational study.* G Ital Nefrol 2022; 39:3.
2. Casino FG, Basile C, Kirmizis D, et al; Eudial Working Group of ERA-EDTA. *The reasons for a clinical trial on incremental haemodialysis.* Nephrol Dial Transplant 2020; 35: 2015–2019.
3. Casino FG, Basile C. *A user-friendly tool for incremental haemodialysis prescription.* Nephrol Dial Transplant 2018; 33(6): 1046–1053.
4. Daugirdas JT, Depner TA, Greene T, et al. *Solute-solver: a web-based tool for modeling urea kinetics for a broad range of hemodialysis schedules in multiple patients.* Am J Kidney Dis 2009; 54: 798–809.
5. National Kidney Foundation. *KDOQI clinical practice guidelines for hemodialysis adequacy: 2015 update.* Am J Kidney Dis 2015; 66: 884–930.
6. European Best Practice Guidelines. *II.3 Haemodialysis dose and residual renal function (Kr).* Nephrol Dial Transplant 2002; 17 (Suppl 7): 24.
7. Casino FG, Lopez T. *The equivalent renal urea clearance: a new parameter to assess dialysis dose.* Nephrol Dial Transplant 1996; 11: 1574–1581.
8. Gotch FA. *The current place of urea kinetic modelling with respect to different dialysis modalities.* Nephrol Dial Transplant 1998; 13 (Suppl 6): S10–S14.
9. Casino FG, Basile C. *The variable target model: a paradigm shift in the incremental haemodialysis prescription.* Nephrol Dial Transplant 2017; 32: 182–190.
10. Casino FG, Casino A, Tarrio-Herva E, Basile C. *New formulas for calculating dialysis dose in incremental haemodialysis.* Nephrol Dial Transplant, https://doi.org/10.1093/ndt/gfaf147.
