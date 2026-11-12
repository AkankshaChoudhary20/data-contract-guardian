from guardian.core import convert, validate

def test_csv_number_conversion_overflow_reports_type_issue():
    huge = 10 ** 1000
    assert convert(huge, 'number', True) == (False, huge)
    result = validate({'fields': {'amount': {'type':'number'}}}, [{'amount':huge}], csv_mode=True)
    assert result['issues'][0]['code'] == 'type'
