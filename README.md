# EuReCa — Haemodialysis Prescription & Adequacy Calculator

**Live Application:** [https://clearance.streamlit.app/](https://clearance.streamlit.app/)  
**Full Project Documentation:** [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md)

---

## Overview

The **EuReCa** app (*European Renal Calculator*) provides clinical guidance for the assessment and prescription of **haemodialysis (HD)** in general and **incremental haemodialysis (iHD)** in particular. It is intended for nephrologists involved in the care of adult patients on maintenance HD (all calculations must be confirmed by qualified medical professionals before clinical use).

Developed by **Francesco Gaetano Casino** (Nephrologist), **Antonio Casino** (Management Engineer), and **Carlo Basile** (Nephrologist), EuReCa is an updated, web-based evolution of the **SPEEDY** spreadsheet (*Spreadsheet for the Prescription of incrEmental haEmoDialYsis*), applying double-pool urea kinetic modeling (UKM) equations consistent with KDOQI guidelines and *Solute-Solver*.

---

## Application Modules & Tabs

The Streamlit app ([`main.py`](main.py)) is organized into **7 tabs** (2 informational tabs and 5 calculation tabs):

1. **Home** ([`pages/home.py`](pages/home.py)) — Overview of the EuReCa application, clinical rationale for incremental HD, standard Kt/V (`stdKt/V`) vs. normalized Equivalent Renal Urea Clearance (`EKRUN`), scientific references, and medical disclaimer.
2. **Key Information** ([`pages/key_information.py`](pages/key_information.py)) — Detailed clinical guide for nephrologists, including input/output parameter tables, symbols, units, acceptable ranges, and worked clinical examples for all 5 calculators.
3. **Adequacy** ([`pages/adequacy.py`](pages/adequacy.py) / [`components/adequacy.py`](components/adequacy.py)) — Main double-pool urea kinetic model (UKM) calculator. Computes dialyzer clearance (`Kd Tot`), `spKt/V`, `eKt/V`, double-pool urea volume (`Vdp`), normalized protein catabolic rate (`PCRn`), residual renal urea clearance (`KRU`, `KRUN`), `EKRUN`, `stdKt/V`, ultrafiltration rate (`UFR`), weekly net ultrafiltration (`UFwk`), and simulated `eKt/V` & `spKt/V` prescriptions for 1, 2, and 3 HD sessions/week.
4. **stdKt/V & EKRU** ([`pages/assessment.py`](pages/assessment.py) / [`components/assessment_calculator.py`](components/assessment_calculator.py)) — Evaluates `UFwk`, `stdKt/V`, `EKRUN`, the variable target (`12 - KRUN`), and the minimum adequate threshold (`10 - 1.5 * KRUN`) from delivered `eKt/V`, `KRUN`, treatment frequency (`NHDWK`), preceding interdialytic interval (`PIDI`), and interdialytic weight gain (`IDWG`).
5. **Dose Calculator** ([`pages/prescription.py`](pages/prescription.py) / [`components/prescription_calculator.py`](components/prescription_calculator.py)) — Computes the required per-session dialysis dose (`eKt/V`) to achieve either the `EKRUN = 12 - KRUN` target or the `stdKt/V = 2.3` target for a given schedule (`NHDWK`, `KRUN`, `PIDI`, `IDWG`).
6. **Kd&Qb** ([`pages/clearance.py`](pages/clearance.py) / [`components/kdn_calculator.py`](components/kdn_calculator.py)) — Calculates the dialyzer urea clearance needed (`Kdn`) and blood flow rate needed (`Qbn`) to reach a target `eKt/V` based on the patient's urea distribution volume (`Vdp`), expected weight loss (`UF`), dialyzer in vitro `KoA`, HDF dilution rates (`HDFPRE`, `HDFPOST`), dialysate flow (`QD`), and session length (`T`).
7. **KoA** ([`pages/koa.py`](pages/koa.py) / [`components/koa_calculator.py`](components/koa_calculator.py)) — Computes the diffusive clearance (`Kd0`) and in vitro mass-transfer-area coefficient (`KoA`) of a dialyzer from manufacturer datasheet test parameters (`Qb`, `Qd`, `Qf`, `Kd`).

---

## Batch Processing with Excel Templates

Each of the 5 calculation tabs (**Adequacy**, **stdKt/V & EKRU**, **Dose Calculator**, **Kd&Qb**, **KoA**) includes a **Batch Processing (Excel)** workflow powered by [`components/excel_handler.py`](components/excel_handler.py) and [`components/batch_ui.py`](components/batch_ui.py):

1. **Download Excel Template (`.xlsx`)**:
   - Available directly inside each tab via the **"Download ... Template (.xlsx)"** button and pre-generated in the [`templates/`](templates/) folder:
     - [`templates/adequacy_template.xlsx`](templates/adequacy_template.xlsx)
     - [`templates/stdktv_ekru_template.xlsx`](templates/stdktv_ekru_template.xlsx)
     - [`templates/dose_calculator_template.xlsx`](templates/dose_calculator_template.xlsx)
     - [`templates/kd_qb_template.xlsx`](templates/kd_qb_template.xlsx)
     - [`templates/koa_template.xlsx`](templates/koa_template.xlsx)
   - Every template workbook contains:
     - **`Inputs`**: Pre-formatted input column headers with sample rows.
     - **`Legend`**: Complete input parameter specification (column name, description, clinical symbol, measurement units, min/max bounds, example value, and clinical validation notes).
     - **`Output_Legend`**: Complete legend of all calculated output columns, symbols, and units.
     - **`Dialyzers`** *(in Adequacy and Kd&Qb templates)*: Full reference list of dialyzer manufacturers, models, and in vitro `KoA` values from [`Table_of_Dialyzers.csv`](Table_of_Dialyzers.csv).
2. **Upload & Multi-Row Iteration with Live Progress Bar**:
   - Upload an updated `.xlsx` file containing one or multiple patient/dialyzer rows.
   - As rows are processed sequentially, a live progress bar displays:
     - **Processed rows** (`processed / total`)
     - **Remaining (missing to process) rows** (`remaining`)
     - **Valid rows** and **Rows with missing/invalid inputs**
3. **Download Output Excel (`.xlsx`)**:
   - Produces a downloadable `.xlsx` workbook containing:
     - **`Results`**: All original input columns, a `Status` column (`OK` or detailed `Error: ...` message), and all calculated output columns.
     - **`Output_Legend`** and **`Input_Legend`** reference sheets.

---

## Project Structure

```text
clearance/
├── main.py                              # Streamlit entry point & tab navigation
├── requirements.txt                     # Python dependencies
├── Table_of_Dialyzers.csv               # Reference dataset of dialyzers (Manufacturer;Model;KoA)
├── README.md                            # Project overview & quickstart
├── docs/
│   └── PROJECT_DOCUMENTATION.md         # Comprehensive technical & clinical documentation
├── templates/                           # Pre-generated Excel (.xlsx) input templates
│   ├── adequacy_template.xlsx
│   ├── stdktv_ekru_template.xlsx
│   ├── dose_calculator_template.xlsx
│   ├── kd_qb_template.xlsx
│   └── koa_template.xlsx
├── pages/                               # Streamlit tab pages
│   ├── home.py                          # Tab 1: Home
│   ├── key_information.py               # Tab 2: Key Information
│   ├── adequacy.py                      # Tab 3: Adequacy
│   ├── assessment.py                    # Tab 4: stdKt/V & EKRU
│   ├── prescription.py                  # Tab 5: Dose Calculator
│   ├── clearance.py                     # Tab 6: Kd&Qb
│   └── koa.py                           # Tab 7: KoA
├── components/                          # Core calculation engines & utilities
│   ├── adequacy.py                      # Double-pool UKM & simulated prescription engine
│   ├── assessment_calculator.py         # stdKt/V & EKRUN assessment calculator
│   ├── prescription_calculator.py       # Target eKt/V dose calculator
│   ├── kdn_calculator.py                # Required Kdn & Qbn iterative calculator
│   ├── koa_calculator.py                # In vitro dialyzer KoA calculator
│   ├── pdf_builder.py                   # Single-patient ReportLab PDF report generator
│   ├── excel_handler.py                 # Excel template generator, validator & batch processor
│   └── batch_ui.py                      # Reusable Streamlit UI for batch Excel processing
└── tests/                               # Automated unit & integration test suite
    ├── test_calculators.py              # Unit tests for all 5 clinical calculators
    ├── test_excel_templates_and_batch.py# Tests for Excel templates, legends & batch processing
    └── test_batch_ui.py                 # UI tests for Streamlit batch component & progress bar
```

---

## Installation & Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Application

```bash
streamlit run main.py
```

### 3. Run the Test Suite

```bash
python3 -m unittest discover -s tests -v
```
