import unittest
from guardian.core import check_contract,validate

class NumericValidationTests(unittest.TestCase):
    def test_unhashable_type_values_are_validation_errors(self):
        for kind in [[],{},None,42]:
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                check_contract({'fields':{'id':{'type':kind}}})
    def test_large_integers_do_not_overflow_finite_checks(self):
        value=10**400
        for kind in ['integer','number']:
            self.assertTrue(validate({'fields':{'id':{'type':kind,'min':value}}},[{'id':value}])['valid'])
    def test_nonfinite_numbers_are_still_rejected(self):
        for value in [float('nan'),float('inf'),float('-inf')]:
            self.assertFalse(validate({'fields':{'value':{'type':'number'}}},[{'value':value}])['valid'])
