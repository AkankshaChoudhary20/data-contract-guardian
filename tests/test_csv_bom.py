from guardian.core import parse_data, validate


def test_utf8_bom_does_not_become_part_of_first_header():
    rows = parse_data('\ufeffid,name\r\n1,Ada\r\n', 'csv')
    contract = {'fields': {'id': {'type': 'integer'}, 'name': {'type': 'string'}}}
    assert rows == [{'id': '1', 'name': 'Ada'}]
    assert validate(contract, rows, csv_mode=True)['valid']


def test_bom_inside_cell_is_preserved():
    assert parse_data('name\n\ufeffAda\n', 'csv') == [{'name': '\ufeffAda'}]
