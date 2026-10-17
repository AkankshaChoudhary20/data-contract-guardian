import unittest
from guardian.core import validate
class NumericUniquenessTests(unittest.TestCase):
    def test_equivalent_numeric_representations_are_duplicates(self):
        contract={'fields':{'value':{'type':'number','unique':True}}}
        for values in [(1,1.0),(0,-0.0),(10**400,10**400)]:
            with self.subTest(values=values):
                result=validate(contract,[{'value':v} for v in values])
                self.assertEqual(result['issue_count'],1)
                self.assertEqual(result['issues'][0]['code'],'duplicate')
    def test_distinct_numbers_remain_unique(self):
        self.assertTrue(validate({'fields':{'v':{'type':'number','unique':True}}},[{'v':1},{'v':2}])['valid'])
