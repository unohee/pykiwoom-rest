import json

import pytest

from pykiwoom_rest.cli import schema
from pykiwoom_rest.cli.formatters import (
    MAX_TABLE_CELL_WIDTH,
    MAX_TABLE_ROWS,
    _truncate_cell,
    json_output,
    table_output,
)


def test_truncate_and_json_output_cover_serialization_modes():
    long_text = "x" * (MAX_TABLE_CELL_WIDTH + 1)
    assert _truncate_cell("short") == "short"
    assert _truncate_cell(long_text) == "x" * (MAX_TABLE_CELL_WIDTH - 1) + "…"
    assert json.loads(json_output({"name": "삼성"})) == {"name": "삼성"}
    assert '  "name": "삼성"' in json_output({"name": "삼성"}, pretty=True)
    assert json.loads(json_output({"value": object()}))["value"]


def test_table_output_covers_empty_dict_scalar_and_dict_rows():
    assert table_output({}) == "(empty)"
    assert table_output({"name": "삼성", "price": 100}) == "  name   삼성\n  price  100"
    assert table_output(None) == "(empty)"
    assert table_output([]) == "(empty)"
    assert table_output(["a", 2]) == "a\n2"

    output = table_output([{"name": "삼성", "price": 100}, {"name": "SK", "volume": 20}])
    assert output.splitlines() == [
        "name  price  volume",
        "----  -----  ------",
        "삼성    100          ",
        "SK           20    ",
    ]


def test_table_output_caps_rows_for_scalar_and_mapping_data():
    scalar_output = table_output(list(range(MAX_TABLE_ROWS + 1)))
    assert scalar_output.endswith("... (1 more rows)")

    mapping_output = table_output([{"value": number} for number in range(MAX_TABLE_ROWS + 1)])
    assert mapping_output.endswith("... (1 more rows)")


def test_schema_covers_full_sdl_scalar_and_invalid_description(monkeypatch):
    assert schema.get_schema().startswith('"""키움증권 REST API')
    assert schema.get_schema("JSON") == "scalar JSON"

    monkeypatch.setattr(schema, "SCHEMA_SDL", 'type Broken {\n  """ unterminated\n}')
    with pytest.raises(ValueError, match="Unterminated SDL description"):
        schema.validate_schema_sdl()
