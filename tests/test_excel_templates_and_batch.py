"""
Unit and integration tests for Excel template generation, legend sheets,
row validation, batch iteration with progress bar updates, and output Excel
generation across all 5 tabs:
- adequacy ("Adequacy")
- assessment ("stdKt/V & EKRU")
- prescription ("Dose Calculator")
- clearance ("Kd&Qb")
- koa ("KoA")
"""

import os
import tempfile
import unittest

from components.excel_handler import (
    TAB_CONFIGS,
    build_dialyzer_lookup,
    generate_excel_output,
    generate_excel_template,
    load_dialyzers_list,
    process_excel_batch,
    read_all_sheets_from_xlsx,
    read_xlsx_sheet_rows,
    save_all_templates_to_directory,
    validate_and_compute_row,
    write_xlsx_workbook,
)


class TestExcelTemplatesAndLegends(unittest.TestCase):
    """Tests Excel template structure and legends for all 5 tabs."""

    def test_all_five_tabs_configured(self):
        expected_keys = {"adequacy", "assessment", "prescription", "clearance", "koa"}
        self.assertEqual(set(TAB_CONFIGS.keys()), expected_keys)

    def test_generate_templates_for_all_tabs(self):
        for tab_key, config in TAB_CONFIGS.items():
            with self.subTest(tab=tab_key):
                xlsx_bytes = generate_excel_template(tab_key, include_sample_rows=True)
                self.assertIsInstance(xlsx_bytes, bytes)
                self.assertGreater(len(xlsx_bytes), 1000)

                sheets = read_all_sheets_from_xlsx(xlsx_bytes)
                self.assertIn("Inputs", sheets)
                self.assertIn("Legend", sheets)
                self.assertIn("Output_Legend", sheets)
                if config.get("include_dialyzers_sheet"):
                    self.assertIn("Dialyzers", sheets)
                    self.assertGreater(len(sheets["Dialyzers"]), 100)

                # Verify 'Inputs' sheet headers match configured input columns
                expected_headers = [inp["col"] for inp in config["inputs"]]
                self.assertEqual(sheets["Inputs"][0], expected_headers)
                # Verify sample rows exist
                self.assertEqual(len(sheets["Inputs"]) - 1, len(config["sample_rows"]))

                # Verify 'Legend' sheet contains every input column name and description
                legend_flat_text = " ".join(
                    str(cell) for row in sheets["Legend"] for cell in row if cell is not None
                )
                for inp in config["inputs"]:
                    self.assertIn(inp["col"], legend_flat_text)
                    self.assertIn(inp["label"], legend_flat_text)

                # Verify 'Output_Legend' sheet contains every output column name
                out_legend_flat_text = " ".join(
                    str(cell) for row in sheets["Output_Legend"] for cell in row if cell is not None
                )
                for out in config["outputs"]:
                    self.assertIn(out["col"], out_legend_flat_text)

    def test_save_all_templates_to_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = save_all_templates_to_directory(tmpdir)
            self.assertEqual(set(saved.keys()), set(TAB_CONFIGS.keys()))
            for tab_key, path in saved.items():
                self.assertTrue(os.path.exists(path))
                headers, rows = read_xlsx_sheet_rows(path)
                self.assertEqual(headers, [inp["col"] for inp in TAB_CONFIGS[tab_key]["inputs"]])
                self.assertGreaterEqual(len(rows), 2)


class TestRowValidationAndCalculation(unittest.TestCase):
    """Tests single-row validation and computation across all 5 tabs."""

    def setUp(self):
        self.dialyzers_lookup = build_dialyzer_lookup()

    def test_adequacy_valid_and_dialyzer_lookup(self):
        sample = dict(TAB_CONFIGS["adequacy"]["sample_rows"][0])
        # Test auto-lookup of KOAvitro from Manufacturer + Model when KOAvitro is empty
        sample["KOAvitro"] = None
        res = validate_and_compute_row("adequacy", sample, dialyzers_lookup=self.dialyzers_lookup)
        self.assertEqual(res["Status"], "OK")
        self.assertEqual(res["KOAvitro"], 977)
        self.assertAlmostEqual(res["KTOT"], 205.11, places=2)
        self.assertAlmostEqual(res["EKTV"], 1.10, places=2)
        self.assertIsNotNone(res["spktv_s1"])
        self.assertIsNotNone(res["spktv_E3"])

    def test_adequacy_validation_errors(self):
        # Invalid PIDI for NHDWK=1 and CT >= C0
        bad_row = dict(TAB_CONFIGS["adequacy"]["sample_rows"][0])
        bad_row["PIDI"] = 3
        bad_row["CT"] = 90.0
        bad_row["C0"] = 80.0
        res = validate_and_compute_row("adequacy", bad_row, dialyzers_lookup=self.dialyzers_lookup)
        self.assertTrue(res["Status"].startswith("Error:"))
        self.assertIn("PIDI", res["Status"])
        self.assertIn("CT", res["Status"])
        self.assertIsNone(res["KTOT"])

    def test_adequacy_excel_serial_date_and_units(self):
        row = dict(TAB_CONFIGS["adequacy"]["sample_rows"][0])
        row["LABDATE"] = 45691  # Excel serial date for 03/02/2025
        row["UNIT"] = "Urea_mg_dl"
        row["C0"] = 80.0 * 2.14
        row["CT"] = 25.0 * 2.14
        row["UUN"] = 300.0 * 2.14
        res = validate_and_compute_row("adequacy", row, dialyzers_lookup=self.dialyzers_lookup)
        self.assertEqual(res["Status"], "OK")
        self.assertEqual(res["LABDATE"], "03/02/2025")
        self.assertAlmostEqual(res["KTOT"], 205.11, places=2)

    def test_assessment_valid_and_invalid(self):
        valid_row = dict(TAB_CONFIGS["assessment"]["sample_rows"][0])
        res = validate_and_compute_row("assessment", valid_row)
        self.assertEqual(res["Status"], "OK")
        self.assertAlmostEqual(res["stdktv"], 1.90, places=2)
        self.assertAlmostEqual(res["ekrun"], 7.41, places=2)

        invalid_row = dict(valid_row, PIDI=2)
        res_err = validate_and_compute_row("assessment", invalid_row)
        self.assertTrue(res_err["Status"].startswith("Error:"))
        self.assertIsNone(res_err["stdktv"])

    def test_prescription_valid_and_invalid(self):
        valid_row = dict(TAB_CONFIGS["prescription"]["sample_rows"][0])
        res = validate_and_compute_row("prescription", valid_row)
        self.assertEqual(res["Status"], "OK")
        self.assertAlmostEqual(res["ufwk"], 1.75, places=2)
        self.assertAlmostEqual(res["ektv_ekru"], 0.98, places=2)

        invalid_row = dict(valid_row, NHDWK=5)
        res_err = validate_and_compute_row("prescription", invalid_row)
        self.assertTrue(res_err["Status"].startswith("Error:"))
        self.assertIsNone(res_err["ufwk"])

    def test_clearance_valid_high_qbn_warning_and_invalid(self):
        # Row 2 from sample_rows has KOAvitro=1422, T=240, EKVT=1.3 -> qbn < 400 (no warning)
        normal_row = dict(TAB_CONFIGS["clearance"]["sample_rows"][1])
        res_normal = validate_and_compute_row("clearance", normal_row, dialyzers_lookup=self.dialyzers_lookup)
        self.assertEqual(res_normal["Status"], "OK")
        self.assertLess(res_normal["qbn"], 400)
        self.assertEqual(res_normal["Warning"], "")

        # Row 1 from sample_rows has KOAvitro=900, T=210, EKVT=1.2 -> qbn=428.9 > 400 (triggers warning)
        valid_row = dict(TAB_CONFIGS["clearance"]["sample_rows"][0])
        res = validate_and_compute_row("clearance", valid_row, dialyzers_lookup=self.dialyzers_lookup)
        self.assertEqual(res["Status"], "OK")
        self.assertAlmostEqual(res["kdn"], 232.0, places=1)
        self.assertAlmostEqual(res["qbn"], 428.9, places=1)
        self.assertIn("Blood flow requirement too high", res["Warning"])

        # Missing VDP
        invalid_row = dict(valid_row, VDP=None)
        res_err = validate_and_compute_row("clearance", invalid_row)
        self.assertTrue(res_err["Status"].startswith("Error:"))

    def test_koa_valid_and_invalid(self):
        valid_row = dict(TAB_CONFIGS["koa"]["sample_rows"][0])
        res = validate_and_compute_row("koa", valid_row)
        self.assertEqual(res["Status"], "OK")
        self.assertAlmostEqual(res["kdif"], 250.0, places=1)
        self.assertAlmostEqual(res["koa"], 824.1, delta=0.5)

        invalid_row = dict(valid_row, QB=400)
        res_err = validate_and_compute_row("koa", invalid_row)
        self.assertTrue(res_err["Status"].startswith("Error:"))
        self.assertIsNone(res_err["koa"])


class TestBatchProcessingAndProgressBar(unittest.TestCase):
    """Tests multi-row iteration, progress callback tracking, and output Excel files."""

    def test_batch_iteration_and_progress_updates_all_tabs(self):
        for tab_key, config in TAB_CONFIGS.items():
            with self.subTest(tab=tab_key):
                # Build a 4-row dataset: 2 valid rows + 1 row with missing required input + 1 valid row
                row1 = dict(config["sample_rows"][0])
                row2 = dict(config["sample_rows"][1])
                first_col = config["inputs"][0]["col"]
                row3_missing = dict(config["sample_rows"][0])
                row3_missing[first_col] = None  # Trigger missing required field
                row4 = dict(config["sample_rows"][0])

                input_cols = [inp["col"] for inp in config["inputs"]]
                sheet_rows = [input_cols]
                for r in (row1, row2, row3_missing, row4):
                    sheet_rows.append([r.get(c) for c in input_cols])

                uploaded_xlsx = write_xlsx_workbook([
                    {"name": "Inputs", "rows": sheet_rows, "header_rows": {0}}
                ])

                progress_events = []

                def callback(
                    processed_rows,
                    remaining_rows,
                    total_rows,
                    valid_rows,
                    missing_or_invalid_rows,
                    current_row_result,
                ):
                    progress_events.append({
                        "processed": processed_rows,
                        "remaining": remaining_rows,
                        "total": total_rows,
                        "valid": valid_rows,
                        "invalid": missing_or_invalid_rows,
                        "status": current_row_result["Status"],
                    })

                batch_out = process_excel_batch(
                    tab_key=tab_key,
                    file_or_records=uploaded_xlsx,
                    progress_callback=callback,
                )

                self.assertEqual(batch_out["total_rows"], 4)
                self.assertEqual(batch_out["processed_rows"], 4)
                self.assertEqual(batch_out["remaining_rows"], 0)
                self.assertEqual(batch_out["valid_rows"], 3)
                self.assertEqual(batch_out["missing_or_invalid_rows"], 1)

                # Verify progress callback fired 4 times in exact order
                self.assertEqual(len(progress_events), 4)
                self.assertEqual(progress_events[0]["processed"], 1)
                self.assertEqual(progress_events[0]["remaining"], 3)
                self.assertEqual(progress_events[2]["processed"], 3)
                self.assertEqual(progress_events[2]["remaining"], 1)
                self.assertEqual(progress_events[2]["invalid"], 1)
                self.assertEqual(progress_events[3]["processed"], 4)
                self.assertEqual(progress_events[3]["remaining"], 0)

                # Verify generated output Excel file contains 'Results', 'Output_Legend', and 'Input_Legend'
                out_sheets = read_all_sheets_from_xlsx(batch_out["output_excel_bytes"])
                self.assertIn("Results", out_sheets)
                self.assertIn("Output_Legend", out_sheets)
                self.assertIn("Input_Legend", out_sheets)
                self.assertEqual(len(out_sheets["Results"]), 5)  # 1 header + 4 data rows


if __name__ == "__main__":
    unittest.main()
