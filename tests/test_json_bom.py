from guardian.core import parse_data

def test_json_export_with_utf8_bom():
    assert parse_data('\ufeff[{"name": "café"}]', 'json') == [{'name': 'café'}]
