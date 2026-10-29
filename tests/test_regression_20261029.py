from guardian.core import parse_data, validate

def test_classic_mac_newlines_and_quoted_carriage_returns():
    rows = parse_data('name,note\rAda,"first\rsecond"\rBob,ok\r', 'csv')
    assert rows == [{'name': 'Ada', 'note': 'first\rsecond'}, {'name': 'Bob', 'note': 'ok'}]
    assert validate({'fields': {'name': {'type': 'string'}, 'note': {'type': 'string'}}}, rows, csv_mode=True)['valid']
