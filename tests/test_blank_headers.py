import unittest
from guardian.core import parse_data

class BlankCSVHeaders(unittest.TestCase):
    def test_whitespace_headers_are_rejected(self):
        for header in (' ', '\t', '   '):
            with self.subTest(header=header), self.assertRaises(ValueError):
                parse_data(f'id,{header}\n1,value\n', 'csv')

    def test_nonblank_header_spacing_is_preserved(self):
        self.assertEqual(parse_data('id, display name \n1,Ada\n', 'csv'),
                         [{'id': '1', ' display name ': 'Ada'}])
