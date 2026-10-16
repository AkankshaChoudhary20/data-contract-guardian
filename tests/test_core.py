import unittest
from guardian.core import validate,parse_data,compare
class CoreTests(unittest.TestCase):
    def setUp(self): self.schema={'fields':{'id':{'type':'integer','unique':True},'score':{'type':'number','min':0}}}
    def test_types_uniqueness_bounds(self):
        r=validate(self.schema,[{'id':1,'score':2},{'id':1,'score':-1},{'id':True,'score':1}])
        self.assertEqual(r['issue_count'],3);self.assertEqual(r['invalid_rows'],2)
    def test_csv_conversion(self):
        self.assertTrue(validate(self.schema,parse_data('id,score\n1,2.5','csv'),True)['valid'])
    def test_extra_missing_and_nullable(self):
        self.assertEqual(validate(self.schema,[{'extra':1}])['issue_count'],3)
        self.assertFalse(validate(self.schema,[{'id':None,'score':0}])['valid'])
    def test_malformed_csv(self):
        for data in ['a,a\n1,2','a,b\n1,2,3','a,b\n1']:
            with self.assertRaises(ValueError): parse_data(data,'csv')
    def test_json_strings_are_not_numbers(self):
        self.assertFalse(validate(self.schema,[{'id':'1','score':2}])['valid'])
    def test_narrowing_and_relaxing(self):
        new={'fields':{'id':{'type':'integer','unique':True},'score':{'type':'number','min':5}}}
        self.assertTrue(compare(self.schema,new)['breaking']);self.assertFalse(compare(new,self.schema)['breaking'])
    def test_required_addition(self):
        self.assertTrue(compare(self.schema,{'fields':{**self.schema['fields'],'name':{'type':'string'}}})['breaking'])
    def test_truncation(self):
        r=validate(self.schema,[{}]*600);self.assertEqual(len(r['issues']),500);self.assertEqual(r['issue_count'],1200)
    def test_enum_comparison_matches_validation_type_semantics(self):
        old = {'fields': {'value': {'type': 'number', 'enum': [1]}}}
        new = {'fields': {'value': {'type': 'number', 'enum': [1.0]}}}
        self.assertTrue(validate(old, [{'value': 1}])['valid'])
        self.assertFalse(validate(new, [{'value': 1}])['valid'])
        self.assertTrue(compare(old, new)['breaking'])
        relaxed = {'fields': {'value': {'type': 'number', 'enum': [1, 1.0]}}}
        self.assertFalse(compare(old, relaxed)['breaking'])

    def test_json_duplicate_fields_cannot_hide_invalid_values(self):
        for content in ['[{"id":"bad","id":1}]', '[{"id":1,"nested":{"a":1,"a":2}}]']:
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, 'Duplicate JSON field'):
                parse_data(content, 'json')
        self.assertEqual(parse_data('[{"id":1},{"id":2}]', 'json'), [{'id':1}, {'id':2}])

if __name__=='__main__':unittest.main()
