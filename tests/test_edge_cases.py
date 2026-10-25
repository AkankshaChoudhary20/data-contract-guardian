import pytest
from guardian.core import parse_data

@pytest.mark.parametrize("value", ["1e999", "-1e999"])
def test_json_exponent_overflow_is_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        parse_data('[{"value": ' + value + '}]', 'json')

def test_finite_json_exponents_still_parse():
    assert parse_data('[{"value": 1e3}]', 'json') == [{"value": 1000.0}]
