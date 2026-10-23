import unittest

from guardian.core import parse_data


class CsvQuotingTests(unittest.TestCase):
    def test_malformed_quotes_raise_value_error(self):
        for content in ('name\n"unclosed', 'name\n"closed"garbage', '"unclosed\nvalue'):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, 'Malformed CSV'):
                parse_data(content, 'csv')

    def test_valid_quotes_multiline_and_crlf_are_preserved(self):
        content = 'id,name\r\n1,"hello, ""world"""\r\n2,"two\nlines"\r\n'
        self.assertEqual(parse_data(content, 'csv'), [
            {'id': '1', 'name': 'hello, "world"'}, {'id': '2', 'name': 'two\nlines'}
        ])
