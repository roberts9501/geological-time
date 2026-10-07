import unittest
from decimal import Decimal

from geological_time import GeologicalTime, format_scientific, parse_scientific


class TestFromHuman(unittest.TestCase):
    def test_millions(self):
        gt = GeologicalTime.from_human("2.5 Ma")
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_billions(self):
        gt = GeologicalTime.from_human("4.54 Ga")
        self.assertEqual(gt.years, Decimal("4540000000"))

    def test_thousands(self):
        gt = GeologicalTime.from_human("12 ka")
        self.assertEqual(gt.years, Decimal("12000"))

    def test_fractional_thousands(self):
        gt = GeologicalTime.from_human("0.5 ka")
        self.assertEqual(gt.years, Decimal("500"))

    def test_no_space(self):
        gt = GeologicalTime.from_human("2.5Ma")
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_with_ago(self):
        gt = GeologicalTime.from_human("2.5 Ma ago")
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_lowercase_unit(self):
        # "ma" should parse as Ma because we normalize case.
        gt = GeologicalTime.from_human("2.5 ma")
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_unknown_unit_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime.from_human("2.5 Ta")

    def test_missing_unit_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime.from_human("2.5")

    def test_garbage_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime.from_human("not a date at all")


class TestFromScientific(unittest.TestCase):
    def test_basic(self):
        gt = GeologicalTime.from_scientific("2.5e6 years")
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_bare(self):
        gt = GeologicalTime.from_scientific("2.5e6")
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_uppercase_e(self):
        gt = GeologicalTime.from_scientific("4.54E9")
        self.assertEqual(gt.years, Decimal("4540000000"))

    def test_yr_unit(self):
        gt = GeologicalTime.from_scientific("1e3 yr")
        self.assertEqual(gt.years, Decimal("1000"))

    def test_negative(self):
        gt = GeologicalTime.from_scientific("-1e6")
        self.assertEqual(gt.years, Decimal("-1000000"))

    def test_zero(self):
        gt = GeologicalTime.from_scientific("0e0")
        self.assertEqual(gt.years, Decimal("0"))

    def test_garbage_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime.from_scientific("2.5 Ma")

    def test_not_a_number_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime.from_scientific("abc")


class TestToHuman(unittest.TestCase):
    def test_auto_billions(self):
        gt = GeologicalTime(Decimal("4540000000"))
        self.assertEqual(gt.to_human(), "4.54 Ga")

    def test_auto_millions(self):
        gt = GeologicalTime(Decimal("2500000"))
        self.assertEqual(gt.to_human(), "2.5 Ma")

    def test_auto_thousands(self):
        gt = GeologicalTime(Decimal("12000"))
        self.assertEqual(gt.to_human(), "12 ka")

    def test_auto_sub_thousand(self):
        gt = GeologicalTime(Decimal("500"))
        self.assertEqual(gt.to_human(), "0.5 ka")

    def test_explicit_unit(self):
        gt = GeologicalTime(Decimal("1000000"))
        self.assertEqual(gt.to_human(unit="k"), "1000 ka")

    def test_explicit_unit_m(self):
        gt = GeologicalTime(Decimal("2500000"))
        self.assertEqual(gt.to_human(unit="M"), "2.5 Ma")

    def test_bad_unit(self):
        gt = GeologicalTime(Decimal("1000"))
        with self.assertRaises(ValueError):
            gt.to_human(unit="T")

    def test_zero(self):
        gt = GeologicalTime(Decimal("0"))
        self.assertEqual(gt.to_human(), "0 ka")

    def test_negative(self):
        gt = GeologicalTime(Decimal("-2500000"))
        self.assertEqual(gt.to_human(), "-2.5 Ma")


class TestToScientific(unittest.TestCase):
    def test_millions(self):
        gt = GeologicalTime(Decimal("2500000"))
        self.assertEqual(gt.to_scientific(), "2.5e6 years")

    def test_billions(self):
        gt = GeologicalTime(Decimal("4540000000"))
        self.assertEqual(gt.to_scientific(), "4.54e9 years")

    def test_zero(self):
        gt = GeologicalTime(Decimal("0"))
        self.assertEqual(gt.to_scientific(), "0e0 years")

    def test_negative(self):
        gt = GeologicalTime(Decimal("-1000000"))
        self.assertEqual(gt.to_scientific(), "-1e6 years")

    def test_small_fraction(self):
        gt = GeologicalTime(Decimal("0.000001"))
        self.assertEqual(gt.to_scientific(), "1e-6 years")


class TestRoundTrip(unittest.TestCase):
    def test_ga_roundtrip(self):
        original = "4.54 Ga"
        gt = GeologicalTime.from_human(original)
        sci = gt.to_scientific()
        gt2 = GeologicalTime.from_scientific(sci)
        self.assertEqual(gt, gt2)

    def test_ma_roundtrip(self):
        original = "2.5 Ma"
        gt = GeologicalTime.from_human(original)
        sci = gt.to_scientific()
        gt2 = GeologicalTime.from_scientific(sci)
        self.assertEqual(gt, gt2)

    def test_ka_roundtrip(self):
        original = "12 ka"
        gt = GeologicalTime.from_human(original)
        sci = gt.to_scientific()
        gt2 = GeologicalTime.from_scientific(sci)
        self.assertEqual(gt, gt2)


class TestConvenienceFunctions(unittest.TestCase):
    def test_format_scientific(self):
        self.assertEqual(format_scientific(2500000), "2.5e6 years")

    def test_format_scientific_decimal(self):
        self.assertEqual(format_scientific(Decimal("4540000000")), "4.54e9 years")

    def test_parse_scientific(self):
        self.assertEqual(parse_scientific("2.5e6 years"), Decimal("2500000"))

    def test_parse_scientific_bare(self):
        self.assertEqual(parse_scientific("4.54e9"), Decimal("4540000000"))


class TestConstruction(unittest.TestCase):
    def test_int(self):
        gt = GeologicalTime(1000)
        self.assertEqual(gt.years, Decimal("1000"))

    def test_float(self):
        # float 2500000.0 becomes Decimal via str, no binary garbage.
        gt = GeologicalTime(2500000.0)
        self.assertEqual(gt.years, Decimal("2500000"))

    def test_str(self):
        gt = GeologicalTime("4540000000")
        self.assertEqual(gt.years, Decimal("4540000000"))

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime("not a number")

    def test_none_raises(self):
        with self.assertRaises(ValueError):
            GeologicalTime(None)

    def test_equality(self):
        a = GeologicalTime(1000)
        b = GeologicalTime(1000)
        self.assertEqual(a, b)

    def test_inequality(self):
        a = GeologicalTime(1000)
        b = GeologicalTime(2000)
        self.assertNotEqual(a, b)

    def test_hashable(self):
        a = GeologicalTime(1000)
        b = GeologicalTime(1000)
        self.assertEqual(hash(a), hash(b))

    def test_repr(self):
        gt = GeologicalTime(1000)
        self.assertEqual(repr(gt), "GeologicalTime(years=1000)")


if __name__ == "__main__":
    unittest.main()
