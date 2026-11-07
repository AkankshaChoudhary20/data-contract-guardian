from guardian.core import compare, validate

def test_integer_to_number_is_a_compatible_widening():
    old = {'fields': {'count': {'type': 'integer'}}}
    new = {'fields': {'count': {'type': 'number'}}}
    assert validate(old, [{'count': 1}])['valid']
    assert validate(new, [{'count': 1}])['valid']
    result = compare(old, new)
    assert result['changes'] and not result['breaking']
    assert compare(new, old)['breaking']
