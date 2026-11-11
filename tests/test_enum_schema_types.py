import pytest
from guardian.core import check_contract

@pytest.mark.parametrize("option", [float("inf"), float("nan"), {}, []])
def test_nonscalar_and_nonfinite_enum_choices_are_rejected(option):
    with pytest.raises(ValueError, match="enum"):
        check_contract({"fields": {"value": {"type": "number", "enum": [option]}}})

def test_nullable_and_numeric_enums_remain_supported():
    check_contract({"fields": {"value": {"type": "number", "nullable": True, "enum": [1, 2.5, None]}}})
