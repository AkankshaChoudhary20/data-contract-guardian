import unittest
from guardian.core import check_contract

class ContractRuleTests(unittest.TestCase):
    def test_malformed_rules_raise_validation_errors(self):
        for name, rule in [('x', {'type': []}), ('x', {'type': {}}), (1, {'type': 'string'}), ('  ', {'type': 'string'})]:
            with self.subTest(name=name, rule=rule), self.assertRaises(ValueError):
                check_contract({'fields': {name: rule}})

    def test_valid_field_rule_is_preserved(self):
        contract = {'fields': {'name': {'type': 'string'}}}
        self.assertIs(check_contract(contract), contract)
