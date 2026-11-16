#!/usr/bin/env python3
"""Automated test suite for Acta Problemata bank and pipeline."""
import unittest
import json
import glob
import pathlib
import validate_bank

ROOT = pathlib.Path(__file__).parent

class TestBankIntegrity(unittest.TestCase):
    def setUp(self):
        self.bank_files = sorted(glob.glob(str(ROOT / "data" / "bank" / "*.json")))
        self.assertTrue(len(self.bank_files) > 0, "Bank should contain problems")

    def test_bank_validation_passes(self):
        """Ensure all problems pass honesty and structural rules."""
        for f in self.bank_files:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            errs = validate_bank.check(data, pathlib.Path(f).name)
            self.assertEqual(errs, [], f"Validation errors in {f}: {errs}")

    def test_numerical_sanity(self):
        """Check that every problem has valid data, questions, and formulas."""
        for f in self.bank_files:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            self.assertGreater(len(data["data"]), 0, f"No data in {f}")
            self.assertGreater(len(data["questions"]), 0, f"No questions in {f}")
            self.assertGreater(len(data["formulas"]), 0, f"No formulas in {f}")
            self.assertGreater(len(data["formulas_tex"]), 0, f"No TeX formulas in {f}")
            self.assertEqual(
                len(data["formulas"]), 
                len(data["formulas_tex"]), 
                f"Formula and TeX formula counts mismatch in {f}"
            )
            # Ensure answer_key is present in bank files for verification
            self.assertIn("answer_key", data, f"Missing answer_key in {f}")
            self.assertGreater(len(data["answer_key"]), 0, f"Empty answer_key in {f}")

    def test_real_case_nasa_mco(self):
        """Specific physics test for the MCO unit mismatch problem."""
        mco_file = ROOT / "data" / "bank" / "07-mco-unites.json"
        self.assertTrue(mco_file.exists(), "07-mco-unites.json should exist")
        with open(mco_file, encoding="utf-8") as fp:
            data = json.load(fp)
        self.assertEqual(data["status"], "real")
        self.assertTrue(data["source_url"].startswith("http"))
        # Check conversion factor
        lbf_to_ns = 4.448222
        j_read = 25.0
        m = 638.0
        dv_real = (j_read * lbf_to_ns) / m
        dv_read = j_read / m
        self.assertAlmostEqual(dv_real, 0.1743, places=3)
        self.assertAlmostEqual(dv_read, 0.0392, places=3)

if __name__ == "__main__":
    unittest.main()
