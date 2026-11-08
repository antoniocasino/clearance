"""
Unit tests for the 5 core calculation modules:
1. Adequacy (components.adequacy.ihd_calculation)
2. stdKt/V & EKRU (components.assessment_calculator.assessment_calculation)
3. Dose Calculator (components.prescription_calculator.prescription_calculation)
4. Kd&Qb (components.kdn_calculator.calculate_kdn_qbwn)
5. KoA (components.koa_calculator.koa)
"""

import unittest

from components.adequacy import ihd_calculation
from components.assessment_calculator import assessment_calculation
from components.prescription_calculator import prescription_calculation
from components.kdn_calculator import calculate_kdn_qbwn
from components.koa_calculator import koa


class TestAdequacyCalculator(unittest.TestCase):
    """Tests for Module 1: Adequacy (ihd_calculation)."""

    def test_reference_example_1hd_wk(self):
        """Matches Table 1 reference example from key_information.py."""
        inputs = {
            "BUN": 1.0,
            "PTID": "N.N.",
            "LABDATE": "03/02/2025",
            "NHDWK": 1,
            "PIDI": 7,
            "BW0": 71.0,
            "BWT": 70.0,
            "T": 240,
            "QB": 300,
            "HDFPRE": 0,
            "HDFPOST": 0,
            "QD": 500,
            "KOAvitro": 977,
            "C0": 80.0,
            "CT": 25.0,
            "UO": 1000,
            "UUN": 300.0,
            "KRUw": 999,
        }
        res = ihd_calculation(inputs)
        self.assertIsInstance(res, dict)
        self.assertAlmostEqual(round(res["KTOT"], 2), 205.11, places=2)
        self.assertAlmostEqual(round(res["SPKTV"], 2), 1.24, places=2)
        self.assertAlmostEqual(round(res["EKTV"], 2), 1.10, places=2)
        self.assertAlmostEqual(round(res["VDP"], 2), 39.34, places=2)
        self.assertAlmostEqual(round(res["PCRN"], 2), 0.68, places=2)
        self.assertAlmostEqual(round(res["Kru"], 2), 2.42, places=2)
        self.assertIn(res["AdeqEKR"], ("Yes", "No"))
        self.assertIn(res["AdeqStdKTV"], ("Yes", "No"))
        self.assertEqual(res["AdeqUFR"], "Yes")

        # Simulated prescriptions present
        for key in ("ektv_s1", "ektv_E1", "ektv_s2", "ektv_E2", "ektv_s3", "ektv_E3"):
            self.assertIn(key, res)
            self.assertIsInstance(res[key], float)

    def test_2hd_and_3hd_schedules_and_direct_kru(self):
        """Tests 2 HD/wk (PIDI 3 & 4) and 3 HD/wk (PIDI 2 & 3) and direct KRUw."""
        base = {
            "BUN": 1.0,
            "PTID": "P2",
            "LABDATE": "10/02/2025",
            "BW0": 75.0,
            "BWT": 73.0,
            "T": 240,
            "QB": 320,
            "HDFPRE": 50,
            "HDFPOST": 0,
            "QD": 600,
            "KOAvitro": 1200,
            "C0": 75.0,
            "CT": 25.0,
            "UO": 0,
            "UUN": 0.0,
            "KRUw": 2.5,
        }
        for nhdwk, pidi in [(2, 3), (2, 4), (3, 2), (3, 3)]:
            inp = dict(base, NHDWK=nhdwk, PIDI=pidi)
            res = ihd_calculation(inp)
            self.assertEqual(res["Kru"], 2.5)
            self.assertGreater(res["STDKTV"], 0)
            self.assertGreater(res["ekrun"], 0)
            self.assertGreater(res["PCRN"], 0)

    def test_equal_pre_and_post_weights(self):
        """Verifies bw0 == bwt adjustment avoids zero UF issues."""
        inputs = {
            "BUN": 2.14,
            "PTID": "P3",
            "LABDATE": "01/03/2025",
            "NHDWK": 2,
            "PIDI": 4,
            "BW0": 70.0,
            "BWT": 70.0,
            "T": 240,
            "QB": 300,
            "HDFPRE": 0,
            "HDFPOST": 30,
            "QD": 400,
            "KOAvitro": 1000,
            "C0": 150.0,
            "CT": 50.0,
            "UO": 500,
            "UUN": 400.0,
            "KRUw": 999,
        }
        res = ihd_calculation(inputs)
        self.assertGreater(res["KTOT"], 0)
        self.assertGreater(res["UFR"], 0)


class TestAssessmentCalculator(unittest.TestCase):
    """Tests for Module 2: stdKt/V & EKRU (assessment_calculation)."""

    def test_table2a_example_1hd_wk(self):
        """Matches Table 2a example in key_information.py (1 HD/wk)."""
        res = assessment_calculation({
            "nhdwk": 1,
            "krun": 4.0,
            "ektv": 1.2,
            "pidi": 7,
            "idwg": 1.0,
        })
        self.assertAlmostEqual(round(res["ufwk"], 2), 1.00, places=2)
        self.assertAlmostEqual(round(res["stdktv"], 2), 1.90, places=2)
        self.assertAlmostEqual(round(res["ekrun"], 2), 7.41, places=2)
        self.assertAlmostEqual(round(res["12_minus_krun"], 2), 8.00, places=2)
        self.assertAlmostEqual(round(res["10_minus_1.5_krun"], 2), 4.00, places=2)

    def test_table2b_example_2hd_wk(self):
        """Matches Table 2b example in key_information.py (2 HD/wk)."""
        res = assessment_calculation({
            "nhdwk": 2,
            "krun": 3.0,
            "ektv": 1.0,
            "pidi": 4,
            "idwg": 1.0,
        })
        self.assertAlmostEqual(round(res["ufwk"], 2), 1.75, places=2)
        self.assertAlmostEqual(round(res["stdktv"], 2), 2.12, places=2)
        self.assertAlmostEqual(round(res["ekrun"], 1), 9.1, places=1)
        self.assertAlmostEqual(round(res["12_minus_krun"], 1), 9.0, places=1)
        self.assertAlmostEqual(round(res["10_minus_1.5_krun"], 1), 5.5, places=1)

    def test_3hd_wk(self):
        """Tests 3 HD/wk schedule in assessment_calculation."""
        res = assessment_calculation({
            "nhdwk": 3,
            "krun": 1.0,
            "ektv": 1.2,
            "pidi": 2,
            "idwg": 2.0,
        })
        self.assertAlmostEqual(res["ufwk"], 7.0, places=2)
        self.assertGreater(res["stdktv"], 2.0)
        self.assertGreater(res["ekrun"], 10.0)


class TestPrescriptionCalculator(unittest.TestCase):
    """Tests for Module 3: Dose Calculator (prescription_calculation)."""

    def test_table3_example_2hd_wk(self):
        """Matches Table 3 example in key_information.py."""
        res = prescription_calculation({
            "nhdwk": 2,
            "krun": 3.0,
            "pidi": 4,
            "idwg": 1.0,
        })
        self.assertAlmostEqual(round(res["ufwk"], 2), 1.75, places=2)
        self.assertAlmostEqual(round(res["ektv_ekru"], 2), 0.98, places=2)
        self.assertAlmostEqual(round(res["ektv_stdktv"], 2), 1.21, delta=0.05)

    def test_1hd_and_3hd_schedules(self):
        """Tests 1 HD/wk and 3 HD/wk schedules in prescription_calculation."""
        res1 = prescription_calculation({"nhdwk": 1, "krun": 4.0, "pidi": 7, "idwg": 1.0})
        self.assertGreater(res1["ektv_ekru"], 1.0)
        self.assertGreater(res1["ektv_stdktv"], 1.0)

        res3 = prescription_calculation({"nhdwk": 3, "krun": 1.0, "pidi": 3, "idwg": 1.5})
        self.assertGreater(res3["ektv_ekru"], 0.5)
        self.assertGreater(res3["ektv_stdktv"], 0.5)


class TestKdnCalculator(unittest.TestCase):
    """Tests for Module 4: Kd&Qb (calculate_kdn_qbwn)."""

    def test_table4_reference_example(self):
        """Matches Table 4 reference example in key_information.py."""
        res = calculate_kdn_qbwn(
            vdp=35,
            uf=2.0,
            koavitro=900,
            hdfpre=0,
            hdfpost=0,
            qd=500,
            t=210,
            ekvt=1.2,
        )
        self.assertIsInstance(res, dict)
        self.assertAlmostEqual(round(res["kdn"], 1), 232.0, places=1)
        self.assertAlmostEqual(round(res["qbn"], 1), 428.9, places=1)

    def test_input_validation_errors(self):
        """Verifies out-of-range parameters return error messages."""
        self.assertTrue(str(calculate_kdn_qbwn(10, 2, 900, 0, 0, 500, 210, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 0, 900, 0, 0, 500, 210, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 2, 300, 0, 0, 500, 210, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 2, 900, 300, 0, 500, 210, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 2, 900, 0, 200, 500, 210, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 2, 900, 0, 0, 200, 210, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 2, 900, 0, 0, 500, 30, 1.2)).startswith("Error"))
        self.assertTrue(str(calculate_kdn_qbwn(35, 2, 900, 0, 0, 500, 210, 2.5)).startswith("Error"))


class TestKoaCalculator(unittest.TestCase):
    """Tests for Module 5: KoA (koa)."""

    def test_table5_reference_example(self):
        """Matches Table 5 reference example in key_information.py."""
        kdif, koa_val = koa(qb=300, qd=500, qf=0, kd=250)
        self.assertAlmostEqual(round(kdif, 1), 250.0, places=1)
        self.assertAlmostEqual(round(koa_val, 0), 824, places=0)

    def test_input_validation_and_zero_division(self):
        """Tests validation bounds and zero division handling in koa."""
        self.assertTrue(str(koa(50, 500, 0, 250)).startswith("Error"))
        self.assertTrue(str(koa(300, 50, 0, 250)).startswith("Error"))
        self.assertTrue(str(koa(300, 500, 40, 250)).startswith("Error"))
        self.assertTrue(str(koa(300, 500, 0, 50)).startswith("Error"))
        # Zero division when qb == qd
        kdif, koa_val = koa(qb=300, qd=300, qf=0, kd=200)
        self.assertIsNone(kdif)
        self.assertIsNone(koa_val)


if __name__ == "__main__":
    unittest.main()
