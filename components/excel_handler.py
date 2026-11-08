"""
Excel Template Generator and Batch Calculation Processor for the EuReCa App.

Supports all 5 calculation modules:
1. Adequacy ("adequacy")
2. stdKt/V & EKRU ("assessment")
3. Dose Calculator ("prescription")
4. Kd&Qb ("clearance")
5. KoA ("koa")

Provides:
- Excel (.xlsx) template generation with Input data sheet, detailed Legend sheet,
  Output Legend sheet, and Dialyzer reference sheet.
- Excel (.xlsx) reader and writer supporting both openpyxl (when installed) and
  a built-in OpenXML (zipfile + xml.etree.ElementTree) engine.
- Row-by-row validation, execution of clinical urea kinetic functions, and
  progress bar callback updates tracking processed, remaining, valid, and
  incomplete/invalid rows.
"""

import csv
import datetime
from io import BytesIO
import math
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from components.adequacy import ihd_calculation
from components.assessment_calculator import assessment_calculation
from components.prescription_calculator import prescription_calculation
from components.kdn_calculator import calculate_kdn_qbwn
from components.koa_calculator import koa


# ---------------------------------------------------------------------------
# Tab Configurations & Legends
# ---------------------------------------------------------------------------

TAB_CONFIGS = {
    "adequacy": {
        "title": "Adequacy",
        "subtitle": "Prescription of incremental HD based on urea kinetics",
        "template_filename": "adequacy_template.xlsx",
        "output_filename": "adequacy_output.xlsx",
        "include_dialyzers_sheet": True,
        "general_notes": [
            "Module 1 ('Adequacy') calculates all key parameters of the double-pool urea kinetic model (UKM) and simulated prescriptions for 1, 2, and 3 HD sessions/week.",
            "Concentration Units (UNIT column): Enter 'BUN_mg_dl' (default, factor 1.0) for Blood/Urine Urea Nitrogen in mg/dl, 'Urea_mg_dl' (factor 2.14) for Urea in mg/dl, or 'Urea_mmol_l' (factor 0.357) for Urea in mmol/l.",
            "Preceding Interdialytic Interval (PIDI): Must be 7 when NHDWK=1; 3 or 4 when NHDWK=2; 2 or 3 when NHDWK=3.",
            "HDF Infusion Rates (HDFPRE, HDFPOST): Set both to 0 in conventional HD. Enter flow rate (ml/min) in HDFPRE for pre-dilution HDF or in HDFPOST for post-dilution HDF.",
            "Dialyzer KoA (KOAvitro): Provide KOAvitro directly (500-2400 ml/min), OR leave KOAvitro empty and specify Manufacturer and Model from the 'Dialyzers' sheet.",
            "Renal Urea Clearance (KRUw): Enter 999 to calculate KRU automatically from 24h Urinary Output (UO) and Urinary Urea Nitrogen (UUN). When UO > 0 and UUN > 0, KRUw automatically defaults to 999.",
        ],
        "inputs": [
            {
                "col": "PTID",
                "label": "Patient Identifier",
                "symbol": "PTID",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "Patient_01",
                "required": True,
                "notes": "Unique patient identifier or code.",
            },
            {
                "col": "LABDATE",
                "label": "Lab Date",
                "symbol": "Lab date",
                "unit": "dd/mm/yyyy",
                "min": "",
                "max": "",
                "example": "03/02/2025",
                "required": True,
                "notes": "Date of laboratory blood/urine sampling (dd/mm/yyyy).",
            },
            {
                "col": "UNIT",
                "label": "Blood and Urine Concentration Units",
                "symbol": "Unit",
                "unit": "BUN_mg_dl | Urea_mg_dl | Urea_mmol_l",
                "min": "",
                "max": "",
                "example": "BUN_mg_dl",
                "required": False,
                "notes": "Options: 'BUN_mg_dl' (Blood and urine urea nitrogen mg/dl, factor=1.0), 'Urea_mg_dl' (Urea mg/dl, factor=2.14), 'Urea_mmol_l' (Urea mmol/l, factor=0.357). Defaults to BUN_mg_dl if blank.",
            },
            {
                "col": "NHDWK",
                "label": "Number of HD sessions per week",
                "symbol": "NHDWK",
                "unit": "sessions/week",
                "min": 1,
                "max": 3,
                "example": 1,
                "required": True,
                "notes": "Integer: 1, 2, or 3 sessions per week.",
            },
            {
                "col": "PIDI",
                "label": "Preceding inter-dialytic interval",
                "symbol": "PIDI",
                "unit": "days",
                "min": 2,
                "max": 7,
                "example": 7,
                "required": True,
                "notes": "Allowed values depend on NHDWK: if NHDWK=1 -> 7; if NHDWK=2 -> 3 or 4; if NHDWK=3 -> 2 or 3.",
            },
            {
                "col": "BW0",
                "label": "Pre-dialysis Body Weight",
                "symbol": "BW0",
                "unit": "kg",
                "min": 20.0,
                "max": 140.0,
                "example": 71.0,
                "required": True,
                "notes": "Patient body weight before dialysis session (20 - 140 kg).",
            },
            {
                "col": "BWT",
                "label": "Post-dialysis Body Weight",
                "symbol": "BWT",
                "unit": "kg",
                "min": 20.0,
                "max": 140.0,
                "example": 70.0,
                "required": True,
                "notes": "Patient body weight after dialysis session (20 - 140 kg).",
            },
            {
                "col": "T",
                "label": "Session length",
                "symbol": "TD",
                "unit": "min",
                "min": 60,
                "max": 480,
                "example": 240,
                "required": True,
                "notes": "Duration of the dialysis session in minutes (60 - 480 min).",
            },
            {
                "col": "QB",
                "label": "Blood Flow Rate",
                "symbol": "Qb",
                "unit": "ml/min",
                "min": 100,
                "max": 450,
                "example": 300,
                "required": True,
                "notes": "Dialyzer blood flow rate (100 - 450 ml/min).",
            },
            {
                "col": "HDFPRE",
                "label": "Pre-dilution infusion rate",
                "symbol": "HDFpre",
                "unit": "ml/min",
                "min": 0,
                "max": 250,
                "example": 0,
                "required": True,
                "notes": "Set 0 in conventional HD or post-dilution HDF (0 - 250 ml/min).",
            },
            {
                "col": "HDFPOST",
                "label": "Post-dilution infusion rate",
                "symbol": "HDFpost",
                "unit": "ml/min",
                "min": 0,
                "max": 150,
                "example": 0,
                "required": True,
                "notes": "Set 0 in conventional HD or pre-dilution HDF (0 - 150 ml/min).",
            },
            {
                "col": "QD",
                "label": "Dialysate flow rate",
                "symbol": "Qd",
                "unit": "ml/min",
                "min": 300,
                "max": 800,
                "example": 500,
                "required": True,
                "notes": "Dialysate flow rate (300 - 800 ml/min).",
            },
            {
                "col": "Manufacturer",
                "label": "Dialyzer Manufacturer",
                "symbol": "Manufacturer",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "Fresenius",
                "required": False,
                "notes": "Optional if KOAvitro is provided directly. See 'Dialyzers' sheet for valid Manufacturer/Model pairs.",
            },
            {
                "col": "Model",
                "label": "Dialyzer Model",
                "symbol": "Model",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "FX10",
                "required": False,
                "notes": "Optional if KOAvitro is provided directly. Used with Manufacturer to auto-fill KOAvitro if KOAvitro is blank.",
            },
            {
                "col": "KOAvitro",
                "label": "Dialyzer Urea KoA in vitro",
                "symbol": "KoA",
                "unit": "ml/min",
                "min": 500,
                "max": 2400,
                "example": 977,
                "required": True,
                "notes": "In vitro dialyzer mass transfer coefficient for urea (500 - 2400 ml/min). Auto-resolved if Manufacturer & Model match 'Dialyzers' sheet.",
            },
            {
                "col": "C0",
                "label": "Pre-dialysis Blood Urea or Urea Nitrogen",
                "symbol": "C0",
                "unit": "mg/dl or mmol/l",
                "min": 20.0,
                "max": 200.0,
                "example": 80.0,
                "required": True,
                "notes": "Pre-dialysis concentration (min 20*BUN_factor, max 200*BUN_factor).",
            },
            {
                "col": "CT",
                "label": "Post-dialysis Blood Urea or Urea Nitrogen",
                "symbol": "CT",
                "unit": "mg/dl or mmol/l",
                "min": 5.0,
                "max": 199.0,
                "example": 25.0,
                "required": True,
                "notes": "Post-dialysis concentration (min 5*BUN_factor, max 199*BUN_factor). Must be strictly less than C0.",
            },
            {
                "col": "UO",
                "label": "Urinary Output",
                "symbol": "UO",
                "unit": "ml/24h",
                "min": 0,
                "max": 4000,
                "example": 1000,
                "required": True,
                "notes": "24-hour urine volume (0 - 4000 ml/24h). Set 0 if anuric or if entering KRUw directly.",
            },
            {
                "col": "UUN",
                "label": "Urinary Urea or Urea Nitrogen concentration",
                "symbol": "UU(N)",
                "unit": "mg/dl or mmol/l",
                "min": 0.0,
                "max": 1000.0,
                "example": 300.0,
                "required": True,
                "notes": "Urine urea or urea nitrogen concentration (0 - 1000*BUN_factor). Set 0 if entering KRUw directly.",
            },
            {
                "col": "KRUw",
                "label": "Renal urea clearance",
                "symbol": "KRU",
                "unit": "ml/min",
                "min": 0.0,
                "max": 999,
                "example": 999,
                "required": True,
                "notes": "Enter 999 to calculate from UO and UUN (when UO>0 and UUN>0), or enter known KRU (0 - 7 ml/min) when UO=0 or UUN=0.",
            },
        ],
        "sample_rows": [
            {
                "PTID": "Patient_01",
                "LABDATE": "03/02/2025",
                "UNIT": "BUN_mg_dl",
                "NHDWK": 1,
                "PIDI": 7,
                "BW0": 71.0,
                "BWT": 70.0,
                "T": 240,
                "QB": 300,
                "HDFPRE": 0,
                "HDFPOST": 0,
                "QD": 500,
                "Manufacturer": "Fresenius",
                "Model": "FX10",
                "KOAvitro": 977,
                "C0": 80.0,
                "CT": 25.0,
                "UO": 1000,
                "UUN": 300.0,
                "KRUw": 999,
            },
            {
                "PTID": "Patient_02",
                "LABDATE": "10/02/2025",
                "UNIT": "BUN_mg_dl",
                "NHDWK": 2,
                "PIDI": 4,
                "BW0": 75.0,
                "BWT": 73.0,
                "T": 240,
                "QB": 320,
                "HDFPRE": 0,
                "HDFPOST": 0,
                "QD": 500,
                "Manufacturer": "Fresenius",
                "Model": "FX80",
                "KOAvitro": 1422,
                "C0": 75.0,
                "CT": 22.0,
                "UO": 800,
                "UUN": 280.0,
                "KRUw": 999,
            },
        ],
        "outputs": [
            {"key": "KTOT", "col": "KTOT", "label": "Total Dialyzer Urea Clearance", "symbol": "Kd Tot", "unit": "ml/min"},
            {"key": "SPKTV", "col": "SPKTV", "label": "Single pool Kt/V", "symbol": "spKt/V", "unit": "dimensionless"},
            {"key": "EKTV", "col": "EKTV", "label": "Equilibrated Kt/V", "symbol": "eKt/V", "unit": "dimensionless"},
            {"key": "VDP", "col": "VDP", "label": "Urea distribution volume (double pool)", "symbol": "Vdp", "unit": "l"},
            {"key": "PCRN", "col": "PCRN", "label": "Protein catabolic rate (g/kg/day)", "symbol": "PCRn", "unit": "(g/kg/day)"},
            {"key": "Kru", "col": "Kru", "label": "Renal urea clearance (calculated)", "symbol": "KRU", "unit": "ml/min"},
            {"key": "krun", "col": "krun", "label": "KRU normalized per V 35 l", "symbol": "KRUN", "unit": "ml/min per 35l V"},
            {"key": "ekrun", "col": "ekrun", "label": "Equivalent Renal Urea Clearance normalized per V 35 l", "symbol": "EKRUN", "unit": "ml/min per 35l V"},
            {"key": "ekrun_min", "col": "ekrun_min", "label": "EKRUN_variable target (10-1.5 KRUN)*", "symbol": "EKRU_VTM", "unit": "ml/min per 35l V"},
            {"key": "AdeqEKR", "col": "AdeqEKR", "label": "EKRUN >= 10 - 1.5 KRUN *", "symbol": "Adequacy", "unit": "Yes/No"},
            {"key": "STDKTV", "col": "STDKTV", "label": "Standard Kt/V", "symbol": "StdKt/V", "unit": "Volume/wk"},
            {"key": "AdeqStdKTV", "col": "AdeqStdKTV", "label": "StdKt/V >= 2.1", "symbol": "Adequacy", "unit": "Yes/No"},
            {"key": "UFR", "col": "UFR", "label": "Ultrafiltration rate", "symbol": "UFR", "unit": "ml/h per kg"},
            {"key": "AdeqUFR", "col": "AdeqUFR", "label": "UFR <= 13 ml/h/kg", "symbol": "Adequacy", "unit": "Yes/No"},
            {"key": "TDN", "col": "TDN", "label": "TD needed for UFR=13 ml/h/kg", "symbol": "TDN", "unit": "min per session"},
            {"key": "Ufwk", "col": "Ufwk", "label": "Weekly net Ultrafiltration", "symbol": "UFwk", "unit": "(l)"},
            {"key": "Ektv_ekru", "col": "Ektv_ekru", "label": "eKt/V to get EKRUN=12-KRUN", "symbol": "eKt/V", "unit": "dimensionless"},
            {"key": "Ektv_stdktv", "col": "Ektv_stdktv", "label": "eKt/V to be prescribed to get stdKt/V=2.3", "symbol": "eKt/V", "unit": "dimensionless"},
            {"key": "ektv_s1", "col": "ektv_s1", "label": "1 HD/week: eKt/V to obtain stdKt/V target (2.3)", "symbol": "eKt/V (1HD stdKt/V)", "unit": "dimensionless"},
            {"key": "spktv_s1", "col": "spktv_s1", "label": "1 HD/week: spKt/V to obtain stdKt/V target (assuming 4h session)", "symbol": "spKt/V (1HD stdKt/V)", "unit": "dimensionless"},
            {"key": "ektv_E1", "col": "ektv_E1", "label": "1 HD/week: eKt/V to obtain EKRUN target (12-KRUN)", "symbol": "eKt/V (1HD EKRUN)", "unit": "dimensionless"},
            {"key": "spktv_E1", "col": "spktv_E1", "label": "1 HD/week: spKt/V to obtain EKRUN target (assuming 4h session)", "symbol": "spKt/V (1HD EKRUN)", "unit": "dimensionless"},
            {"key": "ektv_s2", "col": "ektv_s2", "label": "2 HD/week: eKt/V to obtain stdKt/V target (2.3)", "symbol": "eKt/V (2HD stdKt/V)", "unit": "dimensionless"},
            {"key": "spktv_s2", "col": "spktv_s2", "label": "2 HD/week: spKt/V to obtain stdKt/V target (assuming 4h session)", "symbol": "spKt/V (2HD stdKt/V)", "unit": "dimensionless"},
            {"key": "ektv_E2", "col": "ektv_E2", "label": "2 HD/week: eKt/V to obtain EKRUN target (12-KRUN)", "symbol": "eKt/V (2HD EKRUN)", "unit": "dimensionless"},
            {"key": "spktv_E2", "col": "spktv_E2", "label": "2 HD/week: spKt/V to obtain EKRUN target (assuming 4h session)", "symbol": "spKt/V (2HD EKRUN)", "unit": "dimensionless"},
            {"key": "ektv_s3", "col": "ektv_s3", "label": "3 HD/week: eKt/V to obtain stdKt/V target (2.3)", "symbol": "eKt/V (3HD stdKt/V)", "unit": "dimensionless"},
            {"key": "spktv_s3", "col": "spktv_s3", "label": "3 HD/week: spKt/V to obtain stdKt/V target (assuming 4h session)", "symbol": "spKt/V (3HD stdKt/V)", "unit": "dimensionless"},
            {"key": "ektv_E3", "col": "ektv_E3", "label": "3 HD/week: eKt/V to obtain EKRUN target (12-KRUN)", "symbol": "eKt/V (3HD EKRUN)", "unit": "dimensionless"},
            {"key": "spktv_E3", "col": "spktv_E3", "label": "3 HD/week: spKt/V to obtain EKRUN target (assuming 4h session)", "symbol": "spKt/V (3HD EKRUN)", "unit": "dimensionless"},
        ],
    },
    "assessment": {
        "title": "stdKt/V & EKRU",
        "subtitle": "Assessment of stdKt/V and EKRUN from delivered eKt/V and KRUN",
        "template_filename": "stdktv_ekru_template.xlsx",
        "output_filename": "stdktv_ekru_output.xlsx",
        "include_dialyzers_sheet": False,
        "general_notes": [
            "Module 2 ('stdKt/V & EKRU') calculates weekly net ultrafiltration (UFwk), Standard Kt/V (stdKt/V), and Normalized Equivalent Renal Urea Clearance (EKRUN) from delivered eKt/V and KRUN.",
            "Preceding Interdialytic Interval (PIDI): Must be 7 when NHDWK=1; 3 or 4 when NHDWK=2; 2 or 3 when NHDWK=3.",
            "Adequacy Targets: stdKt/V target is 2.3 v/wk (minimum adequate >= 2.1 v/wk); EKRUN variable target is 12 - KRUN (minimum adequate >= 10 - 1.5 * KRUN ml/min per 35l V).",
        ],
        "inputs": [
            {
                "col": "PTID",
                "label": "Patient Identifier",
                "symbol": "PTID",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "Patient_01",
                "required": True,
                "notes": "Unique patient identifier.",
            },
            {
                "col": "NHDWK",
                "label": "Number of HD per week",
                "symbol": "NHDWK",
                "unit": "number",
                "min": 1,
                "max": 3,
                "example": 1,
                "required": True,
                "notes": "Number of hemodialysis sessions per week (1, 2, or 3).",
            },
            {
                "col": "KRUN",
                "label": "Normalised Kru",
                "symbol": "KRUN",
                "unit": "ml/min per 35l V",
                "min": 0.0,
                "max": 7.0,
                "example": 4.0,
                "required": True,
                "notes": "Residual renal urea clearance normalized to 35 L urea volume (0.0 - 7.0).",
            },
            {
                "col": "EKTV",
                "label": "Delivered eKt/V",
                "symbol": "eKt/V",
                "unit": "dimensionless",
                "min": 0.5,
                "max": 2.0,
                "example": 1.2,
                "required": True,
                "notes": "Equilibrated Kt/V delivered per session (0.5 - 2.0).",
            },
            {
                "col": "PIDI",
                "label": "Preceding interdialytic interval",
                "symbol": "PIDI",
                "unit": "days",
                "min": 1,
                "max": 7,
                "example": 7,
                "required": True,
                "notes": "Allowed values: 7 when NHDWK=1; 3 or 4 when NHDWK=2; 2 or 3 when NHDWK=3.",
            },
            {
                "col": "IDWG",
                "label": "Weight gain during PIDI",
                "symbol": "IDWG",
                "unit": "kg",
                "min": 0.0,
                "max": 5.0,
                "example": 1.0,
                "required": True,
                "notes": "Interdialytic weight gain during the preceding interval (0 - 5 kg).",
            },
        ],
        "sample_rows": [
            {"PTID": "Patient_01", "NHDWK": 1, "KRUN": 4.0, "EKTV": 1.2, "PIDI": 7, "IDWG": 1.0},
            {"PTID": "Patient_02", "NHDWK": 2, "KRUN": 3.0, "EKTV": 1.0, "PIDI": 4, "IDWG": 1.0},
        ],
        "outputs": [
            {"key": "ufwk", "col": "ufwk", "label": "Weekly net Ultrafiltration", "symbol": "UFwk", "unit": "l"},
            {"key": "stdktv", "col": "stdktv", "label": "stdKt/V (v/wk)", "symbol": "stdKt/V", "unit": "v/wk"},
            {"key": "ekrun", "col": "ekrun", "label": "EKRUN", "symbol": "EKRUN", "unit": "ml/min per 35 l V"},
            {"key": "12_minus_krun", "col": "12_minus_krun", "label": "EKRUN variable target=12-KRUN", "symbol": "EKRUN_VTM", "unit": "ml/min per 35 l V"},
            {"key": "10_minus_1.5_krun", "col": "10_minus_1.5_krun", "label": "EKRUN_min_adequate", "symbol": "EKRUN_min", "unit": "ml/min per 35 l V"},
        ],
    },
    "prescription": {
        "title": "Dose Calculator",
        "subtitle": "Calculation of eKt/V to be prescribed",
        "template_filename": "dose_calculator_template.xlsx",
        "output_filename": "dose_calculator_output.xlsx",
        "include_dialyzers_sheet": False,
        "general_notes": [
            "Module 3 ('Dose Calculator') calculates the dialysis doses (eKt/V) to be prescribed to achieve targets based on both EKRUN (12 - KRUN) and stdKt/V (2.3 v/wk).",
            "Preceding Interdialytic Interval (PIDI): Must be 7 when NHDWK=1; 3 or 4 when NHDWK=2; 2 or 3 when NHDWK=3.",
        ],
        "inputs": [
            {
                "col": "PTID",
                "label": "Patient Identifier",
                "symbol": "PTID",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "Patient_01",
                "required": True,
                "notes": "Unique patient identifier.",
            },
            {
                "col": "NHDWK",
                "label": "Number of HD per week",
                "symbol": "NHDWK",
                "unit": "number",
                "min": 1,
                "max": 3,
                "example": 2,
                "required": True,
                "notes": "Number of hemodialysis sessions per week (1, 2, or 3).",
            },
            {
                "col": "KRUN",
                "label": "Normalised Kru",
                "symbol": "KRUN",
                "unit": "ml/min per 35l V",
                "min": 0.0,
                "max": 7.0,
                "example": 3.0,
                "required": True,
                "notes": "Residual renal urea clearance normalized to 35 L urea volume (0.0 - 7.0).",
            },
            {
                "col": "PIDI",
                "label": "Preceding interdialytic interval",
                "symbol": "PIDI",
                "unit": "days",
                "min": 1,
                "max": 7,
                "example": 4,
                "required": True,
                "notes": "Allowed values: 7 when NHDWK=1; 3 or 4 when NHDWK=2; 2 or 3 when NHDWK=3.",
            },
            {
                "col": "IDWG",
                "label": "Weight gain during PIDI",
                "symbol": "IDWG",
                "unit": "kg",
                "min": 0.0,
                "max": 5.0,
                "example": 1.0,
                "required": True,
                "notes": "Interdialytic weight gain during the preceding interval (0 - 5 kg).",
            },
        ],
        "sample_rows": [
            {"PTID": "Patient_01", "NHDWK": 2, "KRUN": 3.0, "PIDI": 4, "IDWG": 1.0},
            {"PTID": "Patient_02", "NHDWK": 3, "KRUN": 1.5, "PIDI": 3, "IDWG": 2.0},
        ],
        "outputs": [
            {"key": "ufwk", "col": "ufwk", "label": "Weekly net Ultrafiltration", "symbol": "UFwk", "unit": "l"},
            {"key": "ektv_ekru", "col": "ektv_ekru", "label": "eKtV to get EKRUN = 12 - KRUN", "symbol": "eKt/V (EKRUN)", "unit": "dimensionless"},
            {"key": "ektv_stdktv", "col": "ektv_stdktv", "label": "eKtV to get stdKt/V = 2.3", "symbol": "eKt/V (stdKt/V)", "unit": "dimensionless"},
        ],
    },
    "clearance": {
        "title": "Kd&Qb",
        "subtitle": "Dialyzer clearance and blood flow rate needed to reach target eKt/V",
        "template_filename": "kd_qb_template.xlsx",
        "output_filename": "kd_qb_output.xlsx",
        "include_dialyzers_sheet": True,
        "general_notes": [
            "Module 4 ('Kd&Qb') calculates the dialyzer urea clearance needed (Kdn) and blood flow rate needed (Qbn) to achieve a prescribed target eKt/V.",
            "Dialyzer KoA (KOAvitro): Provide KOAvitro directly (500-2400 ml/min), OR leave KOAvitro blank and enter Manufacturer and Model from the 'Dialyzers' sheet.",
            "If calculated Qbn > 400 ml/min, a clinical warning is added recommending an increase in dialyzer KoA and/or a reduction in target eKt/V.",
        ],
        "inputs": [
            {
                "col": "PTID",
                "label": "Patient Identifier",
                "symbol": "PTID",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "Patient_01",
                "required": True,
                "notes": "Unique patient identifier.",
            },
            {
                "col": "DATE",
                "label": "Date",
                "symbol": "date",
                "unit": "dd/mm/yyyy",
                "min": "",
                "max": "",
                "example": "03/02/2025",
                "required": True,
                "notes": "Prescription or assessment date (dd/mm/yyyy).",
            },
            {
                "col": "VDP",
                "label": "Patient's urea volume",
                "symbol": "V",
                "unit": "L",
                "min": 20.0,
                "max": 50.0,
                "example": 35.0,
                "required": True,
                "notes": "Double-pool urea distribution volume (20 - 50 L).",
            },
            {
                "col": "UF",
                "label": "Expected intradialysis weight loss",
                "symbol": "UF",
                "unit": "L",
                "min": 0.1,
                "max": 5.0,
                "example": 2.0,
                "required": True,
                "notes": "Expected ultrafiltration volume during the session (0.1 - 5.0 L).",
            },
            {
                "col": "Manufacturer",
                "label": "Dialyzer Manufacturer",
                "symbol": "Manufacturer",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "Fresenius",
                "required": False,
                "notes": "Optional if KOAvitro is provided directly. See 'Dialyzers' sheet.",
            },
            {
                "col": "Model",
                "label": "Dialyzer Model",
                "symbol": "Model",
                "unit": "text",
                "min": "",
                "max": "",
                "example": "FX10",
                "required": False,
                "notes": "Optional if KOAvitro is provided directly. See 'Dialyzers' sheet.",
            },
            {
                "col": "KOAvitro",
                "label": "In vitro KOA of the dialyzer",
                "symbol": "KoA",
                "unit": "ml/min",
                "min": 500,
                "max": 2400,
                "example": 900,
                "required": True,
                "notes": "In vitro dialyzer mass transfer coefficient for urea (500 - 2400 ml/min). Auto-resolved if Manufacturer & Model match 'Dialyzers' sheet.",
            },
            {
                "col": "HDFPRE",
                "label": "Pre-dilution infusion rate",
                "symbol": "HDFPRE",
                "unit": "ml/min",
                "min": 0,
                "max": 250,
                "example": 0,
                "required": True,
                "notes": "Pre-dilution infusion rate (0 - 250 ml/min; set 0 in HD or post-dilution HDF).",
            },
            {
                "col": "HDFPOST",
                "label": "Post-dilution infusion rate",
                "symbol": "HDFPOST",
                "unit": "ml/min",
                "min": 0,
                "max": 150,
                "example": 0,
                "required": True,
                "notes": "Post-dilution infusion rate (0 - 150 ml/min; set 0 in HD or pre-dilution HDF).",
            },
            {
                "col": "QD",
                "label": "Dialysate Flow rate",
                "symbol": "QD",
                "unit": "ml/min",
                "min": 301,
                "max": 800,
                "example": 500,
                "required": True,
                "notes": "Dialysate flow rate (301 - 800 ml/min).",
            },
            {
                "col": "T",
                "label": "Session length",
                "symbol": "T",
                "unit": "min",
                "min": 60,
                "max": 480,
                "example": 210,
                "required": True,
                "notes": "Dialysis session duration (60 - 480 min).",
            },
            {
                "col": "EKVT",
                "label": "eKt/V target",
                "symbol": "eKt/V",
                "unit": "dimensionless",
                "min": 0.3,
                "max": 2.0,
                "example": 1.2,
                "required": True,
                "notes": "Target equilibrated Kt/V to be achieved (0.3 - 2.0).",
            },
        ],
        "sample_rows": [
            {
                "PTID": "Patient_01",
                "DATE": "03/02/2025",
                "VDP": 35.0,
                "UF": 2.0,
                "Manufacturer": "Other",
                "Model": "Other",
                "KOAvitro": 900,
                "HDFPRE": 0,
                "HDFPOST": 0,
                "QD": 500,
                "T": 210,
                "EKVT": 1.2,
            },
            {
                "PTID": "Patient_02",
                "DATE": "10/02/2025",
                "VDP": 38.0,
                "UF": 1.5,
                "Manufacturer": "Fresenius",
                "Model": "FX80",
                "KOAvitro": 1422,
                "HDFPRE": 0,
                "HDFPOST": 0,
                "QD": 500,
                "T": 240,
                "EKVT": 1.3,
            },
        ],
        "outputs": [
            {"key": "kdn", "col": "kdn", "label": "Dialyzer urea clearance needed", "symbol": "Kdn", "unit": "ml/min"},
            {"key": "qbn", "col": "qbn", "label": "Blood flow rate needed", "symbol": "Qbn", "unit": "ml/min"},
            {"key": "Warning", "col": "Warning", "label": "Clinical Warning (if Qbn > 400 ml/min)", "symbol": "Warning", "unit": "text"},
        ],
    },
    "koa": {
        "title": "KoA",
        "subtitle": "Dialyzer's characteristics (in vitro KoA calculation)",
        "template_filename": "koa_template.xlsx",
        "output_filename": "koa_output.xlsx",
        "include_dialyzers_sheet": False,
        "general_notes": [
            "Module 5 ('KoA') calculates the diffusive dialyzer clearance (Kd0) and the in vitro mass-transfer-area coefficient (KoA) for urea from manufacturer datasheet values.",
            "Note: Measured Dialyzer urea clearance (KD) must be strictly less than Blood flow rate (QB) and Dialysate flow rate (QD), and QB must not equal QD.",
        ],
        "inputs": [
            {
                "col": "QB",
                "label": "Blood flow rate",
                "symbol": "Qb",
                "unit": "ml/min",
                "min": 100,
                "max": 300,
                "example": 300,
                "required": True,
                "notes": "In vitro test blood flow rate (100 - 300 ml/min).",
            },
            {
                "col": "QD",
                "label": "Dialysate flow rate",
                "symbol": "Qd",
                "unit": "ml/min",
                "min": 100,
                "max": 1000,
                "example": 500,
                "required": True,
                "notes": "In vitro test dialysate flow rate (100 - 1000 ml/min).",
            },
            {
                "col": "QF",
                "label": "Ultrafiltration rate",
                "symbol": "Qf",
                "unit": "ml/min",
                "min": 0,
                "max": 30,
                "example": 0,
                "required": True,
                "notes": "In vitro test ultrafiltration rate (0 - 30 ml/min).",
            },
            {
                "col": "KD",
                "label": "Dialyzer Urea clearance",
                "symbol": "Kd",
                "unit": "ml/min",
                "min": 100,
                "max": 350,
                "example": 250,
                "required": True,
                "notes": "Measured dialyzer urea clearance from datasheet (100 - 350 ml/min; must be < QB and < QD).",
            },
        ],
        "sample_rows": [
            {"QB": 300, "QD": 500, "QF": 0, "KD": 250},
            {"QB": 300, "QD": 500, "QF": 10, "KD": 265},
        ],
        "outputs": [
            {"key": "kdif", "col": "kdif", "label": "Diffusive Kd", "symbol": "Kd0", "unit": "ml/min"},
            {"key": "koa", "col": "koa", "label": "KoA of the dialyzer in vitro", "symbol": "KoA", "unit": "ml/min"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Dialyzer Table Loader
# ---------------------------------------------------------------------------

def load_dialyzers_list(csv_path=None):
    """
    Loads Table_of_Dialyzers.csv and returns a list of dicts:
    [{"Manufacturer": str, "Model": str, "KoA": int}, ...]
    """
    if csv_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "Table_of_Dialyzers.csv")

    dialyzers = []
    if not os.path.exists(csv_path):
        return dialyzers

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            manuf = (row.get("Manufacturer") or "").strip()
            model = (row.get("Model") or "").strip()
            koa_raw = (row.get("KoA") or "").strip()
            try:
                koa_val = int(float(koa_raw))
                dialyzers.append({"Manufacturer": manuf, "Model": model, "KoA": koa_val})
            except (ValueError, TypeError):
                continue
    return dialyzers


def build_dialyzer_lookup(csv_path=None):
    """
    Returns a dict mapping (manufacturer_lower, model_lower) -> int(KoA).
    """
    lookup = {}
    for item in load_dialyzers_list(csv_path):
        key = (item["Manufacturer"].lower(), item["Model"].lower())
        lookup[key] = item["KoA"]
    return lookup


# ---------------------------------------------------------------------------
# OpenXML (.xlsx) Writer & Reader (Zero External Dependency + Excel Compatible)
# ---------------------------------------------------------------------------

def _col_letter(col_idx_1based):
    """Converts 1-based column index to Excel column letters (1 -> A, 27 -> AA)."""
    result = []
    n = col_idx_1based
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result.append(chr(65 + rem))
    return "".join(reversed(result))


def _sanitize_xml_text(val):
    """Ensures string is valid XML text without control characters."""
    s = str(val)
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
    return escape(s)


def write_xlsx_workbook(sheets):
    """
    Writes a multi-sheet .xlsx workbook into bytes.

    Args:
        sheets: list of dicts:
            {
                "name": str,
                "rows": list of lists (cell values),
                "header_rows": set/list of 0-based row indices to style as table headers (default {0}),
                "banner_rows": set/list of 0-based row indices to style as section banners (default set()),
            }

    Returns:
        bytes representing a valid OpenXML .xlsx file.
    """
    buf = BytesIO()
    shared_strings = []
    shared_string_map = {}

    def get_sst_index(text):
        s = str(text)
        if s not in shared_string_map:
            shared_string_map[s] = len(shared_strings)
            shared_strings.append(s)
        return shared_string_map[s]

    sheet_xmls = []
    for sheet in sheets:
        rows = sheet.get("rows", [])
        header_rows = set(sheet.get("header_rows", {0}))
        banner_rows = set(sheet.get("banner_rows", set()))

        # Compute column widths
        col_widths = {}
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                s_len = len(str(val)) if val is not None else 0
                if r_idx in banner_rows and c_idx == 0:
                    continue
                col_widths[c_idx] = max(col_widths.get(c_idx, 10), min(s_len + 4, 55))

        lines = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        ]
        if col_widths:
            lines.append("  <cols>")
            for c_idx in sorted(col_widths.keys()):
                w = col_widths[c_idx]
                col_num = c_idx + 1
                lines.append(f'    <col min="{col_num}" max="{col_num}" width="{w}" customWidth="1"/>')
            lines.append("  </cols>")

        lines.append("  <sheetData>")
        for r_idx, row in enumerate(rows):
            row_num = r_idx + 1
            lines.append(f'    <row r="{row_num}">')
            for c_idx, val in enumerate(row):
                col_ref = f"{_col_letter(c_idx + 1)}{row_num}"
                if r_idx in header_rows:
                    style_id = 1
                elif r_idx in banner_rows:
                    style_id = 2
                else:
                    style_id = 0

                if val is None or val == "":
                    if style_id != 0:
                        lines.append(f'      <c r="{col_ref}" s="{style_id}"/>')
                    continue

                if isinstance(val, bool):
                    sst_idx = get_sst_index("TRUE" if val else "FALSE")
                    lines.append(f'      <c r="{col_ref}" t="s" s="{style_id}"><v>{sst_idx}</v></c>')
                elif isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val):
                    lines.append(f'      <c r="{col_ref}" s="{style_id}"><v>{val}</v></c>')
                else:
                    sst_idx = get_sst_index(str(val))
                    lines.append(f'      <c r="{col_ref}" t="s" s="{style_id}"><v>{sst_idx}</v></c>')
            lines.append("    </row>")
        lines.append("  </sheetData>")
        lines.append("</worksheet>")
        sheet_xmls.append("\n".join(lines))

    # Build sharedStrings.xml
    sst_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">',
    ]
    for s in shared_strings:
        sst_lines.append(f'  <si><t xml:space="preserve">{_sanitize_xml_text(s)}</t></si>')
    sst_lines.append("</sst>")
    sst_xml = "\n".join(sst_lines)

    # Build styles.xml (0 = normal, 1 = table header, 2 = section banner)
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="3">
    <font><sz val="11"/><color theme="1"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="12"/><color rgb="FF1F4E78"/><name val="Calibri"/></font>
  </fonts>
  <fills count="4">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFD9E1F2"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFBFBFBF"/></left>
      <right style="thin"><color rgb="FFBFBFBF"/></right>
      <top style="thin"><color rgb="FFBFBFBF"/></top>
      <bottom style="thin"><color rgb="FFBFBFBF"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="3">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>
  </cellXfs>
</styleSheet>"""

    # Build workbook.xml and workbook.xml.rels
    wb_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        "  <sheets>",
    ]
    wb_rels_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    ct_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '  <Default Extension="xml" ContentType="application/xml"/>',
        '  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        '  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>',
    ]

    for idx, sheet in enumerate(sheets, start=1):
        safe_name = _sanitize_xml_text(sheet["name"][:31])
        wb_lines.append(f'    <sheet name="{safe_name}" sheetId="{idx}" r:id="rId{idx}"/>')
        wb_rels_lines.append(
            f'  <Relationship Id="rId{idx}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{idx}.xml"/>'
        )
        ct_lines.append(
            f'  <Override PartName="/xl/worksheets/sheet{idx}.xml" '
            f'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )

    wb_lines.append("  </sheets>")
    wb_lines.append("</workbook>")

    style_rid = len(sheets) + 1
    sst_rid = len(sheets) + 2
    wb_rels_lines.append(
        f'  <Relationship Id="rId{style_rid}" '
        f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        f'Target="styles.xml"/>'
    )
    wb_rels_lines.append(
        f'  <Relationship Id="rId{sst_rid}" '
        f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
        f'Target="sharedStrings.xml"/>'
    )
    wb_rels_lines.append("</Relationships>")
    ct_lines.append("</Types>")

    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "\n".join(ct_lines))
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", "\n".join(wb_lines))
        zf.writestr("xl/_rels/workbook.xml.rels", "\n".join(wb_rels_lines))
        zf.writestr("xl/styles.xml", styles_xml)
        zf.writestr("xl/sharedStrings.xml", sst_xml)
        for idx, sheet_xml in enumerate(sheet_xmls, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml)

    buf.seek(0)
    return buf.getvalue()


def _col_letters_to_index(col_letters):
    """Converts Excel column letters ('A', 'B', ..., 'AA') to 0-based index."""
    idx = 0
    for ch in col_letters.upper():
        if "A" <= ch <= "Z":
            idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def read_xlsx_sheet_rows(file_or_bytes, preferred_sheet_name="Inputs"):
    """
    Reads an .xlsx file (bytes, BytesIO, or file path) and returns a list of
    dictionaries (one per non-empty data row) using the first non-empty row as column headers.

    Also returns the list of headers found.
    """
    if isinstance(file_or_bytes, (bytes, bytearray)):
        stream = BytesIO(file_or_bytes)
    elif isinstance(file_or_bytes, str):
        with open(file_or_bytes, "rb") as f:
            stream = BytesIO(f.read())
    else:
        file_or_bytes.seek(0)
        stream = BytesIO(file_or_bytes.read())

    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

    with zipfile.ZipFile(stream, mode="r") as zf:
        # 1. Load sharedStrings if present
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            sst_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in sst_root.findall("main:si", ns):
                texts = [t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")]
                shared_strings.append("".join(texts))

        # 2. Find target worksheet path via workbook.xml + workbook.xml.rels
        wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
        rels_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {}
        for rel in rels_root:
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target", "")
            if target.startswith("/"):
                target = target.lstrip("/")
            elif not target.startswith("xl/"):
                target = "xl/" + target
            rid_to_target[rid] = target

        sheet_targets = []
        for sheet_elem in wb_root.findall(".//main:sheet", ns):
            s_name = sheet_elem.attrib.get("name", "")
            r_id = sheet_elem.attrib.get(rel_ns, "")
            target = rid_to_target.get(r_id, "")
            if target in zf.namelist():
                sheet_targets.append((s_name, target))

        if not sheet_targets:
            raise ValueError("No valid worksheet found in the Excel file.")

        chosen_target = sheet_targets[0][1]
        for s_name, target in sheet_targets:
            if s_name.strip().lower() == preferred_sheet_name.strip().lower():
                chosen_target = target
                break

        # 3. Parse worksheet rows
        ws_root = ET.fromstring(zf.read(chosen_target))
        raw_rows = []
        for row_elem in ws_root.findall(".//main:sheetData/main:row", ns):
            row_cells = {}
            max_col = -1
            for c_elem in row_elem.findall("main:c", ns):
                cell_ref = c_elem.attrib.get("r", "")
                col_letters = "".join(ch for ch in cell_ref if ch.isalpha())
                c_idx = _col_letters_to_index(col_letters) if col_letters else (max_col + 1)
                max_col = max(max_col, c_idx)

                cell_type = c_elem.attrib.get("t", "")
                v_elem = c_elem.find("main:v", ns)
                is_elem = c_elem.find("main:is", ns)

                val = None
                if cell_type == "s" and v_elem is not None and v_elem.text is not None:
                    sst_idx = int(v_elem.text)
                    val = shared_strings[sst_idx] if 0 <= sst_idx < len(shared_strings) else ""
                elif cell_type == "inlineStr" and is_elem is not None:
                    texts = [t.text or "" for t in is_elem.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")]
                    val = "".join(texts)
                elif cell_type == "b" and v_elem is not None:
                    val = v_elem.text == "1"
                elif cell_type == "str" and v_elem is not None:
                    val = v_elem.text or ""
                elif v_elem is not None and v_elem.text is not None:
                    raw_text = v_elem.text.strip()
                    try:
                        f_val = float(raw_text)
                        val = int(f_val) if f_val.is_integer() and "." not in raw_text else f_val
                    except ValueError:
                        val = raw_text

                row_cells[c_idx] = val

            if max_col >= 0:
                row_list = [row_cells.get(i, None) for i in range(max_col + 1)]
                if any(v is not None and str(v).strip() != "" for v in row_list):
                    raw_rows.append(row_list)

    if not raw_rows:
        return [], []

    headers = [str(h).strip() if h is not None else f"Col_{i+1}" for i, h in enumerate(raw_rows[0])]
    records = []
    for r in raw_rows[1:]:
        rec = {}
        non_empty = False
        for i, h in enumerate(headers):
            v = r[i] if i < len(r) else None
            if isinstance(v, str):
                v = v.strip()
                if v == "":
                    v = None
            if v is not None:
                non_empty = True
            rec[h] = v
        if non_empty:
            records.append(rec)

    return headers, records


def read_all_sheets_from_xlsx(file_or_bytes):
    """
    Helper to inspect all sheet names and their 2D row arrays from an .xlsx file.
    Useful for testing and validation.
    """
    if isinstance(file_or_bytes, (bytes, bytearray)):
        stream = BytesIO(file_or_bytes)
    else:
        file_or_bytes.seek(0)
        stream = BytesIO(file_or_bytes.read())

    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

    result = {}
    with zipfile.ZipFile(stream, mode="r") as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            sst_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in sst_root.findall("main:si", ns):
                texts = [t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")]
                shared_strings.append("".join(texts))

        wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
        rels_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {}
        for rel in rels_root:
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target", "")
            if target.startswith("/"):
                target = target.lstrip("/")
            elif not target.startswith("xl/"):
                target = "xl/" + target
            rid_to_target[rid] = target

        for sheet_elem in wb_root.findall(".//main:sheet", ns):
            s_name = sheet_elem.attrib.get("name", "")
            r_id = sheet_elem.attrib.get(rel_ns, "")
            target = rid_to_target.get(r_id, "")
            if target not in zf.namelist():
                continue

            ws_root = ET.fromstring(zf.read(target))
            rows = []
            for row_elem in ws_root.findall(".//main:sheetData/main:row", ns):
                row_cells = {}
                max_col = -1
                for c_elem in row_elem.findall("main:c", ns):
                    cell_ref = c_elem.attrib.get("r", "")
                    col_letters = "".join(ch for ch in cell_ref if ch.isalpha())
                    c_idx = _col_letters_to_index(col_letters) if col_letters else (max_col + 1)
                    max_col = max(max_col, c_idx)
                    cell_type = c_elem.attrib.get("t", "")
                    v_elem = c_elem.find("main:v", ns)
                    val = None
                    if cell_type == "s" and v_elem is not None and v_elem.text is not None:
                        val = shared_strings[int(v_elem.text)]
                    elif v_elem is not None and v_elem.text is not None:
                        raw_text = v_elem.text.strip()
                        try:
                            f_val = float(raw_text)
                            val = int(f_val) if f_val.is_integer() and "." not in raw_text else f_val
                        except ValueError:
                            val = raw_text
                    row_cells[c_idx] = val
                if max_col >= 0:
                    rows.append([row_cells.get(i, None) for i in range(max_col + 1)])
            result[s_name] = rows
    return result


# ---------------------------------------------------------------------------
# Template Generation
# ---------------------------------------------------------------------------

def _build_legend_sheet_rows(config):
    """Builds rows, header_rows, and banner_rows for the Input Legend worksheet."""
    rows = []
    header_rows = set()
    banner_rows = set()

    # Title banner
    banner_rows.add(len(rows))
    rows.append([f"{config['title']} - {config['subtitle']} (Input Legend & Instructions)"])
    rows.append([])

    # General instructions section
    banner_rows.add(len(rows))
    rows.append(["General Instructions & Clinical Notes"])
    for idx, note in enumerate(config.get("general_notes", []), start=1):
        rows.append([f"{idx}. {note}"])
    rows.append([])

    # Input Parameters Legend Table
    banner_rows.add(len(rows))
    rows.append(["Input Parameters Specification"])
    header_rows.add(len(rows))
    rows.append([
        "#",
        "Column Header (in 'Inputs' sheet)",
        "Parameter Description",
        "Symbol",
        "Units",
        "Min Value",
        "Max Value",
        "Example Value",
        "Required",
        "Validation & Clinical Notes",
    ])
    for idx, inp in enumerate(config["inputs"], start=1):
        rows.append([
            idx,
            inp["col"],
            inp["label"],
            inp["symbol"],
            inp["unit"],
            inp["min"],
            inp["max"],
            inp["example"],
            "Yes" if inp.get("required", True) else "Optional",
            inp.get("notes", ""),
        ])

    return {
        "name": "Legend",
        "rows": rows,
        "header_rows": header_rows,
        "banner_rows": banner_rows,
    }


def _build_output_legend_sheet_rows(config):
    """Builds rows, header_rows, and banner_rows for the Output Legend worksheet."""
    rows = []
    header_rows = set()
    banner_rows = set()

    banner_rows.add(len(rows))
    rows.append([f"{config['title']} - Output Parameters Legend"])
    rows.append([])

    header_rows.add(len(rows))
    rows.append([
        "#",
        "Output Column Header",
        "Output Description",
        "Symbol",
        "Units",
    ])
    rows.append([
        0,
        "Status",
        "Row processing status ('OK' if valid, or 'Error: <details>' if missing/invalid inputs)",
        "Status",
        "text",
    ])
    for idx, out in enumerate(config["outputs"], start=1):
        rows.append([
            idx,
            out["col"],
            out["label"],
            out["symbol"],
            out["unit"],
        ])

    return {
        "name": "Output_Legend",
        "rows": rows,
        "header_rows": header_rows,
        "banner_rows": banner_rows,
    }


def generate_excel_template(tab_key, include_sample_rows=True):
    """
    Generates an Excel (.xlsx) template as bytes for the specified tab_key.

    Sheets included:
    1. 'Inputs': Column headers for all inputs + optional sample rows.
    2. 'Legend': Clear legend of all input columns, units, min/max, examples, and instructions.
    3. 'Output_Legend': Clear legend of all output columns produced by the batch calculation.
    4. 'Dialyzers' (for 'adequacy' and 'clearance'): Reference table of dialyzers and in vitro KoA values.
    """
    if tab_key not in TAB_CONFIGS:
        raise ValueError(f"Unknown tab_key '{tab_key}'. Valid keys: {list(TAB_CONFIGS.keys())}")

    config = TAB_CONFIGS[tab_key]
    input_cols = [inp["col"] for inp in config["inputs"]]

    input_rows = [input_cols]
    if include_sample_rows:
        for sample in config.get("sample_rows", []):
            input_rows.append([sample.get(col, "") for col in input_cols])

    sheets = [
        {
            "name": "Inputs",
            "rows": input_rows,
            "header_rows": {0},
            "banner_rows": set(),
        },
        _build_legend_sheet_rows(config),
        _build_output_legend_sheet_rows(config),
    ]

    if config.get("include_dialyzers_sheet"):
        dialyzers = load_dialyzers_list()
        dialyzer_rows = [["Manufacturer", "Model", "KoA"]]
        for d in dialyzers:
            dialyzer_rows.append([d["Manufacturer"], d["Model"], d["KoA"]])
        sheets.append({
            "name": "Dialyzers",
            "rows": dialyzer_rows,
            "header_rows": {0},
            "banner_rows": set(),
        })

    return write_xlsx_workbook(sheets)


# ---------------------------------------------------------------------------
# Row Validation & Calculation Engine
# ---------------------------------------------------------------------------

def _parse_float(val, field_name):
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return None, f"Missing '{field_name}'"
    try:
        if isinstance(val, str):
            val = val.replace(",", ".").strip()
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None, f"Invalid numeric value for '{field_name}'"
        return f, None
    except (ValueError, TypeError):
        return None, f"Invalid numeric value for '{field_name}': {val}"


def _parse_int(val, field_name):
    f, err = _parse_float(val, field_name)
    if err:
        return None, err
    if not float(f).is_integer():
        return None, f"'{field_name}' must be an integer (got {val})"
    return int(round(f)), None


def _validate_pidi(nhdwk, pidi):
    if nhdwk == 1 and pidi != 7:
        return "The only value allowed for Preceding interdialytic interval (PIDI) when NHDWK=1 is 7"
    if nhdwk == 2 and pidi not in (3, 4):
        return "Values allowed for Preceding interdialytic interval (PIDI) when NHDWK=2 are 3 and 4"
    if nhdwk == 3 and pidi not in (2, 3):
        return "Values allowed for Preceding interdialytic interval (PIDI) when NHDWK=3 are 2 and 3"
    return None


def _resolve_bun_factor(unit_val):
    """
    Resolves the BUN conversion factor from the UNIT column value.
    Returns (bun_factor, error_message).
    """
    if unit_val is None or str(unit_val).strip() == "":
        return 1.0, None

    s = str(unit_val).strip().lower()
    if s in (
        "bun_mg_dl",
        "bun",
        "1",
        "1.0",
        "mg/dl (bun)",
        "blood and urine urea nitrogen concentrations (mg/dl)",
    ):
        return 1.0, None
    if s in (
        "urea_mg_dl",
        "urea mg/dl",
        "2.14",
        "blood and urine urea concentrations (mg/dl)",
    ):
        return 2.14, None
    if s in (
        "urea_mmol_l",
        "urea mmol/l",
        "mmol/l",
        "0.357",
        "blood and urine urea concentrations (mmol/l)",
    ):
        return 0.357, None

    return None, (
        f"Invalid UNIT '{unit_val}'. Allowed values: "
        "'BUN_mg_dl' (1.0), 'Urea_mg_dl' (2.14), or 'Urea_mmol_l' (0.357)"
    )


def _format_date_value(val):
    if val is None or str(val).strip() == "":
        return None
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime("%d/%m/%Y")
    if isinstance(val, (int, float)) and 20000 <= val <= 80000:
        dt = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(val))
        return dt.strftime("%d/%m/%Y")
    return str(val).strip()


def _get_case_insensitive(row_dict, col_name):
    """Fetches a column value from row_dict matching col_name case-insensitively."""
    if col_name in row_dict:
        return row_dict[col_name]
    target = col_name.strip().lower()
    for k, v in row_dict.items():
        if str(k).strip().lower() == target:
            return v
    return None


def validate_and_compute_row(tab_key, row_dict, dialyzers_lookup=None):
    """
    Validates a single input row dictionary for the given tab_key and executes
    the corresponding calculation function.

    Returns a dictionary containing:
    - Normalized input columns
    - 'Status': 'OK' or 'Error: ...'
    - All output columns for the tab (set to None if Status is Error)
    """
    if tab_key not in TAB_CONFIGS:
        raise ValueError(f"Unknown tab_key: {tab_key}")

    config = TAB_CONFIGS[tab_key]
    input_cols = [inp["col"] for inp in config["inputs"]]
    output_cols = [out["col"] for out in config["outputs"]]

    out_row = {col: _get_case_insensitive(row_dict, col) for col in input_cols}
    out_row["Status"] = "OK"
    for ocol in output_cols:
        out_row[ocol] = None

    errors = []

    if tab_key == "adequacy":
        ptid = out_row["PTID"]
        if ptid is None or str(ptid).strip() == "":
            errors.append("Missing 'PTID' (Patient Identifier)")
        labdate = _format_date_value(out_row["LABDATE"])
        if not labdate:
            errors.append("Missing 'LABDATE'")
        else:
            out_row["LABDATE"] = labdate

        bun_factor, unit_err = _resolve_bun_factor(out_row.get("UNIT"))
        if unit_err:
            errors.append(unit_err)
            bun_factor = 1.0
        elif not out_row.get("UNIT"):
            out_row["UNIT"] = "BUN_mg_dl"

        nhdwk, err = _parse_int(out_row["NHDWK"], "NHDWK")
        if err:
            errors.append(err)
        elif not (1 <= nhdwk <= 3):
            errors.append("NHDWK must be 1, 2, or 3")

        pidi, err = _parse_int(out_row["PIDI"], "PIDI")
        if err:
            errors.append(err)
        elif nhdwk in (1, 2, 3):
            pidi_err = _validate_pidi(nhdwk, pidi)
            if pidi_err:
                errors.append(pidi_err)

        bw0, err = _parse_float(out_row["BW0"], "BW0")
        if err:
            errors.append(err)
        elif not (20.0 <= bw0 <= 140.0):
            errors.append("BW0 must be between 20.0 and 140.0 kg")

        bwt, err = _parse_float(out_row["BWT"], "BWT")
        if err:
            errors.append(err)
        elif not (20.0 <= bwt <= 140.0):
            errors.append("BWT must be between 20.0 and 140.0 kg")

        t, err = _parse_float(out_row["T"], "T")
        if err:
            errors.append(err)
        elif not (60 <= t <= 480):
            errors.append("T (Session length) must be between 60 and 480 min")

        qb, err = _parse_float(out_row["QB"], "QB")
        if err:
            errors.append(err)
        elif not (100 <= qb <= 450):
            errors.append("QB (Blood Flow Rate) must be between 100 and 450 ml/min")

        hdfpre, err = _parse_float(out_row["HDFPRE"], "HDFPRE")
        if err:
            errors.append(err)
        elif not (0 <= hdfpre <= 250):
            errors.append("HDFPRE must be between 0 and 250 ml/min")

        hdfpost, err = _parse_float(out_row["HDFPOST"], "HDFPOST")
        if err:
            errors.append(err)
        elif not (0 <= hdfpost <= 150):
            errors.append("HDFPOST must be between 0 and 150 ml/min")

        qd, err = _parse_float(out_row["QD"], "QD")
        if err:
            errors.append(err)
        elif not (300 <= qd <= 800):
            errors.append("QD (Dialysate flow rate) must be between 300 and 800 ml/min")

        # Resolve KOAvitro either directly or via Manufacturer + Model
        raw_koa = out_row.get("KOAvitro")
        if (raw_koa is None or str(raw_koa).strip() == "") and dialyzers_lookup:
            manuf = str(out_row.get("Manufacturer") or "").strip().lower()
            model = str(out_row.get("Model") or "").strip().lower()
            if (manuf, model) in dialyzers_lookup:
                raw_koa = dialyzers_lookup[(manuf, model)]
                out_row["KOAvitro"] = raw_koa

        koavitro, err = _parse_float(raw_koa, "KOAvitro")
        if err:
            errors.append("Missing 'KOAvitro' (provide KOAvitro or a valid Manufacturer & Model)")
        elif not (500 <= koavitro <= 2500):
            errors.append("KOAvitro must be between 500 and 2500 ml/min")

        c0, err = _parse_float(out_row["C0"], "C0")
        if err:
            errors.append(err)
        elif not (20.0 * bun_factor - 1e-6 <= c0 <= 200.0 * bun_factor + 1e-6):
            errors.append(
                f"C0 must be between {round(20.0 * bun_factor, 2)} and {round(200.0 * bun_factor, 2)}"
            )

        ct, err = _parse_float(out_row["CT"], "CT")
        if err:
            errors.append(err)
        elif not (5.0 * bun_factor - 1e-6 <= ct <= 199.0 * bun_factor + 1e-6):
            errors.append(
                f"CT must be between {round(5.0 * bun_factor, 2)} and {round(199.0 * bun_factor, 2)}"
            )

        if c0 is not None and ct is not None and ct >= c0:
            errors.append("Post-dialysis Blood Urea Nitrogen (CT) must be less than Pre-dialysis (C0)")

        uo, err = _parse_float(out_row["UO"], "UO")
        if err:
            errors.append(err)
        elif not (0 <= uo <= 4000):
            errors.append("UO (Urinary Output) must be between 0 and 4000 ml/24h")

        uun, err = _parse_float(out_row["UUN"], "UUN")
        if err:
            errors.append(err)
        elif not (0.0 <= uun <= 1000.0 * bun_factor + 1e-6):
            errors.append(f"UUN must be between 0 and {round(1000.0 * bun_factor, 2)}")

        raw_kruw = out_row.get("KRUw")
        if uo is not None and uun is not None and uo > 0 and uun > 0 and (raw_kruw is None or str(raw_kruw).strip() == ""):
            raw_kruw = 999
            out_row["KRUw"] = 999

        kruw, err = _parse_float(raw_kruw, "KRUw")
        if err:
            errors.append(err)
        else:
            if uo is not None and uun is not None and uo > 0 and uun > 0:
                if kruw != 999 and not (0 <= kruw <= 7):
                    errors.append("KRUw must be 999 (to calculate from urine data) or between 0 and 7 ml/min")
            else:
                if not (0 <= kruw <= 7):
                    errors.append("When UO=0 or UUN=0, KRUw must be between 0 and 7 ml/min (cannot be 999)")

        if errors:
            out_row["Status"] = "Error: " + "; ".join(errors)
            return out_row

        try:
            calc_inputs = {
                "BUN": bun_factor,
                "PTID": str(ptid).strip(),
                "LABDATE": labdate,
                "NHDWK": nhdwk,
                "PIDI": pidi,
                "BW0": bw0,
                "BWT": bwt,
                "T": t,
                "QB": qb,
                "HDFPRE": hdfpre,
                "HDFPOST": hdfpost,
                "QD": qd,
                "KOAvitro": koavitro,
                "C0": c0,
                "CT": ct,
                "KRUw": kruw,
                "UO": uo,
                "UUN": uun,
            }
            res = ihd_calculation(calc_inputs)
            if not isinstance(res, dict):
                out_row["Status"] = f"Error: {res}"
                return out_row

            # Enrich with simulated spKt/V columns (ektv * 1.128 as in pages/adequacy.py)
            res["spktv_s1"] = res["ektv_s1"] * 1.128
            res["spktv_E1"] = res["ektv_E1"] * 1.128
            res["spktv_s2"] = res["ektv_s2"] * 1.128
            res["spktv_E2"] = res["ektv_E2"] * 1.128
            res["spktv_s3"] = res["ektv_s3"] * 1.128
            res["spktv_E3"] = res["ektv_E3"] * 1.128

            for out_def in config["outputs"]:
                val = res.get(out_def["key"])
                if isinstance(val, float):
                    val = round(val, 2)
                out_row[out_def["col"]] = val
        except Exception as exc:
            out_row["Status"] = f"Error: Calculation failed ({exc})"

        return out_row

    elif tab_key == "assessment":
        ptid = out_row["PTID"]
        if ptid is None or str(ptid).strip() == "":
            errors.append("Missing 'PTID' (Patient Identifier)")

        nhdwk, err = _parse_int(out_row["NHDWK"], "NHDWK")
        if err:
            errors.append(err)
        elif not (1 <= nhdwk <= 3):
            errors.append("NHDWK must be 1, 2, or 3")

        krun, err = _parse_float(out_row["KRUN"], "KRUN")
        if err:
            errors.append(err)
        elif not (0.0 <= krun <= 7.0):
            errors.append("KRUN must be between 0.0 and 7.0")

        ektv, err = _parse_float(out_row["EKTV"], "EKTV")
        if err:
            errors.append(err)
        elif not (0.5 <= ektv <= 2.0):
            errors.append("EKTV must be between 0.5 and 2.0")

        pidi, err = _parse_int(out_row["PIDI"], "PIDI")
        if err:
            errors.append(err)
        elif nhdwk in (1, 2, 3):
            pidi_err = _validate_pidi(nhdwk, pidi)
            if pidi_err:
                errors.append(pidi_err)

        idwg, err = _parse_float(out_row["IDWG"], "IDWG")
        if err:
            errors.append(err)
        elif not (0.0 <= idwg <= 5.0):
            errors.append("IDWG must be between 0.0 and 5.0 kg")

        if errors:
            out_row["Status"] = "Error: " + "; ".join(errors)
            return out_row

        try:
            res = assessment_calculation({
                "nhdwk": nhdwk,
                "krun": krun,
                "ektv": ektv,
                "pidi": pidi,
                "idwg": idwg,
            })
            if not isinstance(res, dict):
                out_row["Status"] = f"Error: {res}"
                return out_row

            for out_def in config["outputs"]:
                val = res.get(out_def["key"])
                if isinstance(val, float):
                    val = round(val, 2)
                out_row[out_def["col"]] = val
        except Exception as exc:
            out_row["Status"] = f"Error: Calculation failed ({exc})"

        return out_row

    elif tab_key == "prescription":
        ptid = out_row["PTID"]
        if ptid is None or str(ptid).strip() == "":
            errors.append("Missing 'PTID' (Patient Identifier)")

        nhdwk, err = _parse_int(out_row["NHDWK"], "NHDWK")
        if err:
            errors.append(err)
        elif not (1 <= nhdwk <= 3):
            errors.append("NHDWK must be 1, 2, or 3")

        krun, err = _parse_float(out_row["KRUN"], "KRUN")
        if err:
            errors.append(err)
        elif not (0.0 <= krun <= 7.0):
            errors.append("KRUN must be between 0.0 and 7.0")

        pidi, err = _parse_int(out_row["PIDI"], "PIDI")
        if err:
            errors.append(err)
        elif nhdwk in (1, 2, 3):
            pidi_err = _validate_pidi(nhdwk, pidi)
            if pidi_err:
                errors.append(pidi_err)

        idwg, err = _parse_float(out_row["IDWG"], "IDWG")
        if err:
            errors.append(err)
        elif not (0.0 <= idwg <= 5.0):
            errors.append("IDWG must be between 0.0 and 5.0 kg")

        if errors:
            out_row["Status"] = "Error: " + "; ".join(errors)
            return out_row

        try:
            res = prescription_calculation({
                "nhdwk": nhdwk,
                "krun": krun,
                "pidi": pidi,
                "idwg": idwg,
            })
            if not isinstance(res, dict):
                out_row["Status"] = f"Error: {res}"
                return out_row

            for out_def in config["outputs"]:
                val = res.get(out_def["key"])
                if isinstance(val, float):
                    val = round(val, 2)
                out_row[out_def["col"]] = val
        except Exception as exc:
            out_row["Status"] = f"Error: Calculation failed ({exc})"

        return out_row

    elif tab_key == "clearance":
        ptid = out_row["PTID"]
        if ptid is None or str(ptid).strip() == "":
            errors.append("Missing 'PTID' (Patient Identifier)")

        date_val = _format_date_value(out_row["DATE"])
        if not date_val:
            errors.append("Missing 'DATE'")
        else:
            out_row["DATE"] = date_val

        vdp, err = _parse_float(out_row["VDP"], "VDP")
        if err:
            errors.append(err)
        elif not (20.0 <= vdp <= 50.0):
            errors.append("VDP must be between 20 and 50 L")

        uf, err = _parse_float(out_row["UF"], "UF")
        if err:
            errors.append(err)
        elif not (0.1 <= uf <= 5.0):
            errors.append("UF must be between 0.1 and 5.0 L")

        raw_koa = out_row.get("KOAvitro")
        if (raw_koa is None or str(raw_koa).strip() == "") and dialyzers_lookup:
            manuf = str(out_row.get("Manufacturer") or "").strip().lower()
            model = str(out_row.get("Model") or "").strip().lower()
            if (manuf, model) in dialyzers_lookup:
                raw_koa = dialyzers_lookup[(manuf, model)]
                out_row["KOAvitro"] = raw_koa

        koavitro, err = _parse_float(raw_koa, "KOAvitro")
        if err:
            errors.append("Missing 'KOAvitro' (provide KOAvitro or a valid Manufacturer & Model)")
        elif not (500 <= koavitro <= 2400):
            errors.append("KOAvitro must be between 500 and 2400 ml/min")

        hdfpre, err = _parse_float(out_row["HDFPRE"], "HDFPRE")
        if err:
            errors.append(err)
        elif not (0 <= hdfpre <= 250):
            errors.append("HDFPRE must be between 0 and 250 ml/min")

        hdfpost, err = _parse_float(out_row["HDFPOST"], "HDFPOST")
        if err:
            errors.append(err)
        elif not (0 <= hdfpost <= 150):
            errors.append("HDFPOST must be between 0 and 150 ml/min")

        qd, err = _parse_float(out_row["QD"], "QD")
        if err:
            errors.append(err)
        elif not (301 <= qd <= 800):
            errors.append("QD must be between 301 and 800 ml/min")

        t, err = _parse_float(out_row["T"], "T")
        if err:
            errors.append(err)
        elif not (60 <= t <= 480):
            errors.append("T must be between 60 and 480 min")

        ekvt, err = _parse_float(out_row["EKVT"], "EKVT")
        if err:
            errors.append(err)
        elif not (0.3 <= ekvt <= 2.0):
            errors.append("EKVT must be between 0.3 and 2.0")

        if errors:
            out_row["Status"] = "Error: " + "; ".join(errors)
            return out_row

        try:
            res = calculate_kdn_qbwn(vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt)
            if not isinstance(res, dict):
                out_row["Status"] = str(res)
                return out_row

            kdn_val = round(res["kdn"], 1)
            qbn_val = round(res["qbn"], 1)
            out_row["kdn"] = kdn_val
            out_row["qbn"] = qbn_val
            out_row["Warning"] = (
                "Blood flow requirement too high. It is recommended to increase KOA and/or reduce eKt/V"
                if res["qbn"] > 400
                else ""
            )
        except Exception as exc:
            out_row["Status"] = f"Error: Calculation failed ({exc})"

        return out_row

    elif tab_key == "koa":
        qb, err = _parse_float(out_row["QB"], "QB")
        if err:
            errors.append(err)
        elif not (100 <= qb <= 300):
            errors.append("QB must be between 100 and 300 ml/min")

        qd, err = _parse_float(out_row["QD"], "QD")
        if err:
            errors.append(err)
        elif not (100 <= qd <= 1000):
            errors.append("QD must be between 100 and 1000 ml/min")

        qf, err = _parse_float(out_row["QF"], "QF")
        if err:
            errors.append(err)
        elif not (0 <= qf <= 30):
            errors.append("QF must be between 0 and 30 ml/min")

        kd, err = _parse_float(out_row["KD"], "KD")
        if err:
            errors.append(err)
        elif not (100 <= kd <= 350):
            errors.append("KD must be between 100 and 350 ml/min")

        if errors:
            out_row["Status"] = "Error: " + "; ".join(errors)
            return out_row

        try:
            res = koa(qb=qb, qd=qd, qf=qf, kd=kd)
            if isinstance(res, str):
                out_row["Status"] = res
                return out_row
            kdif_result, koa_result = res
            if kdif_result is None or koa_result is None:
                out_row["Status"] = "Error: Division by zero or invalid clearance ratio encountered."
                return out_row
            out_row["kdif"] = round(kdif_result, 1)
            out_row["koa"] = round(koa_result, 1)
        except Exception as exc:
            out_row["Status"] = f"Error: Calculation failed ({exc})"

        return out_row


# ---------------------------------------------------------------------------
# Batch Processing & Output Excel Generation
# ---------------------------------------------------------------------------

def generate_excel_output(tab_key, result_rows):
    """
    Generates an Excel (.xlsx) output file as bytes from the processed result_rows.

    Sheets included:
    1. 'Results': All input columns + 'Status' + all calculated output columns.
    2. 'Output_Legend': Legend of all output parameters, symbols, and units.
    3. 'Input_Legend': Legend of all input parameters, symbols, units, and rules.
    """
    if tab_key not in TAB_CONFIGS:
        raise ValueError(f"Unknown tab_key '{tab_key}'")

    config = TAB_CONFIGS[tab_key]
    input_cols = [inp["col"] for inp in config["inputs"]]
    output_cols = [out["col"] for out in config["outputs"]]
    all_cols = input_cols + ["Status"] + output_cols

    rows_2d = [all_cols]
    for r in result_rows:
        rows_2d.append([r.get(col, "") for col in all_cols])

    input_legend_sheet = _build_legend_sheet_rows(config)
    input_legend_sheet["name"] = "Input_Legend"

    sheets = [
        {
            "name": "Results",
            "rows": rows_2d,
            "header_rows": {0},
            "banner_rows": set(),
        },
        _build_output_legend_sheet_rows(config),
        input_legend_sheet,
    ]
    return write_xlsx_workbook(sheets)


def process_excel_batch(tab_key, file_or_records, progress_callback=None):
    """
    Processes a batch of rows for the specified tab_key, iterating over each row
    and invoking progress_callback after each row is processed.

    Args:
        tab_key: One of 'adequacy', 'assessment', 'prescription', 'clearance', 'koa'.
        file_or_records: Either bytes / BytesIO / file path of an .xlsx file,
                         or a list of row dicts.
        progress_callback: Optional callable with signature:
            progress_callback(
                processed_rows=int,
                remaining_rows=int,
                total_rows=int,
                valid_rows=int,
                missing_or_invalid_rows=int,
                current_row_result=dict,
            )

    Returns:
        dict with keys:
            - 'results': list of dicts (each row's inputs, Status, and outputs)
            - 'columns': list of column names in order
            - 'total_rows': int
            - 'processed_rows': int
            - 'remaining_rows': int (0 when finished)
            - 'valid_rows': int
            - 'missing_or_invalid_rows': int (rows that had missing fields or validation errors)
            - 'output_excel_bytes': bytes of the generated .xlsx output workbook
    """
    if tab_key not in TAB_CONFIGS:
        raise ValueError(f"Unknown tab_key '{tab_key}'")

    config = TAB_CONFIGS[tab_key]
    if isinstance(file_or_records, list):
        records = file_or_records
    else:
        _, records = read_xlsx_sheet_rows(file_or_records, preferred_sheet_name="Inputs")

    dialyzers_lookup = build_dialyzer_lookup() if config.get("include_dialyzers_sheet") else None

    total_rows = len(records)
    processed_rows = 0
    valid_rows = 0
    missing_or_invalid_rows = 0
    results = []

    for row_dict in records:
        res_row = validate_and_compute_row(tab_key, row_dict, dialyzers_lookup=dialyzers_lookup)
        results.append(res_row)
        processed_rows += 1
        remaining_rows = total_rows - processed_rows

        if res_row.get("Status") == "OK":
            valid_rows += 1
        else:
            missing_or_invalid_rows += 1

        if progress_callback is not None:
            progress_callback(
                processed_rows=processed_rows,
                remaining_rows=remaining_rows,
                total_rows=total_rows,
                valid_rows=valid_rows,
                missing_or_invalid_rows=missing_or_invalid_rows,
                current_row_result=res_row,
            )

    input_cols = [inp["col"] for inp in config["inputs"]]
    output_cols = [out["col"] for out in config["outputs"]]
    all_cols = input_cols + ["Status"] + output_cols

    output_excel_bytes = generate_excel_output(tab_key, results)

    return {
        "results": results,
        "columns": all_cols,
        "total_rows": total_rows,
        "processed_rows": processed_rows,
        "remaining_rows": 0,
        "valid_rows": valid_rows,
        "missing_or_invalid_rows": missing_or_invalid_rows,
        "output_excel_bytes": output_excel_bytes,
    }


def save_all_templates_to_directory(directory_path=None):
    """
    Generates and saves the .xlsx templates for all 5 tabs into directory_path
    (defaults to `<repo_root>/templates`).
    Returns a dict mapping tab_key -> absolute file path.
    """
    if directory_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        directory_path = os.path.join(base_dir, "templates")

    os.makedirs(directory_path, exist_ok=True)
    saved_paths = {}
    for tab_key, config in TAB_CONFIGS.items():
        xlsx_bytes = generate_excel_template(tab_key, include_sample_rows=True)
        out_path = os.path.join(directory_path, config["template_filename"])
        with open(out_path, "wb") as f:
            f.write(xlsx_bytes)
        saved_paths[tab_key] = out_path
    return saved_paths
