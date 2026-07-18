from pykiwoom_rest.cli.field_map import remap, remap_keep_all


def test_remap_preserves_unknown_values_and_resolves_conflicting_aliases():
    mapped = remap(
        {"first": 1, "second": 2, "raw": 3, "second_raw": 4},
        {"first": "value", "second": "value"},
    )

    assert mapped == {"value": 1, "second": 2, "raw": 3, "second_raw": 4}


def test_remap_ignores_duplicate_alias_with_identical_value_and_keep_all_delegates():
    data = {"first": 1, "second": 1, "unknown": 3}
    field_map = {"first": "value", "second": "value"}

    assert remap(data, field_map) == {"value": 1, "unknown": 3}
    assert remap_keep_all(data, field_map) == {"value": 1, "unknown": 3}


def test_remap_disambiguates_conflict_key_already_present_in_result():
    assert remap(
        {"pre": 0, "pre_raw": 9, "first": 1, "second": 2},
        {
            "pre": "second",
            "pre_raw": "second_raw",
            "first": "value",
            "second": "value",
        },
    ) == {"second": 0, "second_raw": 9, "value": 1, "second_raw_raw": 2}
