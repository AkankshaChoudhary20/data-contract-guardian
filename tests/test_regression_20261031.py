import unittest
from guardian.core import compare

class EnumOrderTests(unittest.TestCase):
    def contract(self, values):
        return {'fields': {'status': {'type': 'string', 'enum': values}}}

    def test_reordering_and_duplicate_options_do_not_change_contract(self):
        self.assertEqual(compare(self.contract(['open', 'closed']), self.contract(['closed', 'open', 'open'])), {'breaking': False, 'changes': []})

    def test_removing_option_remains_breaking(self):
        self.assertTrue(compare(self.contract(['open', 'closed']), self.contract(['open']))['breaking'])

    def test_expanding_options_remains_nonbreaking(self):
        result = compare(self.contract(['open']), self.contract(['open', 'closed']))
        self.assertFalse(result['breaking'])
        self.assertEqual(len(result['changes']), 1)

    def test_boolean_and_integer_options_are_still_distinct(self):
        before = {'fields': {'flag': {'type': 'integer', 'enum': [1]}}}
        after = {'fields': {'flag': {'type': 'integer', 'enum': [True]}}}
        self.assertTrue(compare(before, after)['breaking'])
