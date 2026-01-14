import os
import sys
from unittest.mock import patch, MagicMock
from pandera.errors import SchemaErrors
import pandas as pd
import pytest

# ensure project root and src are on path so imports in src.main (and top-level packages) resolve
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PIPELINE_PATH = os.path.join(PROJECT_ROOT, "pipeline")
sys.path.insert(0, PROJECT_ROOT)
if os.path.isdir(PIPELINE_PATH):
    sys.path.insert(0, PIPELINE_PATH)

from pipeline.main import (
    load_raw_data,
    clean_operations,
    clean_flotteurs,
    clean_resultats,
    save_clean_data,
    validate_df,
)

import inspect
import textwrap
import pipeline.main as main_mod


def test_load_raw_data_reads_three_files():
    mock_df = pd.DataFrame({"col": [1, 2, 3]})
    with patch("pandas.read_csv", return_value=mock_df) as mock_read_csv:
        ops, flot, res = load_raw_data()
        assert mock_read_csv.call_count == 3
        assert isinstance(ops, pd.DataFrame)


def test_clean_operations_dates_numeric_text():
    df = pd.DataFrame({
        "date_heure_reception_alerte": ["2023-01-01", "invalid"],
        "date_heure_fin_operation": ["2023-01-02", "invalid"],
        "latitude": ["45.5", "invalid"],
        "longitude": ["2.3", "invalid"],
        "vent_direction": ["10", "20"],
        "vent_force": ["5", "6"],
        "mer_force": ["3", "4"],
        "numero_sitrep": ["1", "2"],
        "type_operation": ["SAR", "ASST"],
        "pourquoi_alerte": ["test", "test2"],
    })
    result = clean_operations(df.copy())
    assert pd.api.types.is_datetime64_any_dtype(result["date_heure_reception_alerte"])
    assert pd.api.types.is_datetime64_any_dtype(result["date_heure_fin_operation"])
    assert pd.api.types.is_numeric_dtype(result["latitude"])
    assert pd.api.types.is_numeric_dtype(result["numero_sitrep"])
    assert str(result["type_operation"].dtype) == "string"


def test_clean_flotteurs_duplicates_numeric_text():
    df = pd.DataFrame({
        "numero_ordre": ["1", "2", "1"],
        "pavillon": ["FR", "EN", "FR"],
        "resultat_flotteur": ["rescued", "assisted", "rescued"],
        "type_flotteur": ["boat", "ship", "boat"],
        "categorie_flotteur": ["A", "B", "A"],
        "numero_immatriculation": ["123", "456", "123"],
    })
    result = clean_flotteurs(df.copy())
    assert len(result) == 2
    assert pd.api.types.is_numeric_dtype(result["numero_ordre"])
    assert str(result["pavillon"].dtype) == "string"


def test_clean_resultats_text_and_missing_column():
    df_ok = pd.DataFrame({"resultat_flotteur": ["outcome1", "outcome2"]})
    r_ok = clean_resultats(df_ok)
    assert str(r_ok["resultat_flotteur"].dtype) == "string"

    df_missing = pd.DataFrame({"other_col": [1, 2]})
    r_missing = clean_resultats(df_missing)
    assert len(r_missing) == 2


def test_save_clean_data_calls_makedirs_and_to_csv():
    ops = pd.DataFrame({"col": [1, 2]})
    flot = pd.DataFrame({"col": [3, 4]})
    res = pd.DataFrame({"col": [5, 6]})
    with patch("os.makedirs") as mock_makedirs, patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
        with patch("builtins.print"):
            save_clean_data(ops, flot, res)
        mock_makedirs.assert_called_with("pipeline/data", exist_ok=True)
        assert mock_to_csv.call_count == 3


def test_validate_df_success_and_failure():
    df = pd.DataFrame({"col": [1, 2, 3]})
    mock_schema = MagicMock()
    mock_schema.validate.return_value = df
    res = validate_df(df, mock_schema, "test_schema")
    assert res.equals(df)
    mock_schema.validate.assert_called_once()

    mock_schema_fail = MagicMock()
    # Create a SchemaErrors instance without running its __init__ to avoid internal schema backend calls,
    # then attach the attributes validate_df is expected to log/use.
    err = SchemaErrors.__new__(SchemaErrors)
    err.schema = MagicMock()
    err.schema_errors = pd.DataFrame({"col": ["error_detail"]})
    err.data = pd.DataFrame({"col": [None]})
    mock_schema_fail.validate.side_effect = err

    with patch("logging.error") as mock_log_error:
        with pytest.raises(RuntimeError):
            validate_df(df, mock_schema_fail, "test_schema")
        assert mock_log_error.called


# --- from tests/test_main_extra.py: tests for additional validate_df branches
def _make_schema_error_with_attr(attr_name, value):
    err = SchemaErrors.__new__(SchemaErrors)
    setattr(err, attr_name, value)
    return err


def test_validate_df_logs_failure_cases_branch():
    df = pd.DataFrame({"a": [1]})
    mock_schema = MagicMock()

    err = _make_schema_error_with_attr("failure_cases", pd.DataFrame({"col": ["fc"]}))
    mock_schema.validate.side_effect = err

    with patch("logging.error") as mock_log:
        with pytest.raises(RuntimeError):
            validate_df(df, mock_schema, "ops")

        # should log multiple times and include a DataFrame object (failure_cases)
        assert mock_log.call_count >= 3
        assert any(isinstance(call.args[0], pd.DataFrame) for call in mock_log.call_args_list)


def test_validate_df_logs_str_when_no_failure_attrs():
    df = pd.DataFrame({"a": [1]})
    mock_schema = MagicMock()

    # SchemaErrors instance with no failure_cases/schema_errors attributes
    err = SchemaErrors.__new__(SchemaErrors)
    # ensure __str__ on SchemaErrors won't raise (it expects a .message attribute)
    err.message = "synthetic schema error"
    mock_schema.validate.side_effect = err

    with patch("logging.error") as mock_log:
        with pytest.raises(RuntimeError):
            validate_df(df, mock_schema, "ops")

        # should log at least the header messages and a string representation of the exception
        assert mock_log.call_count >= 3
        assert any(isinstance(call.args[0], str) for call in mock_log.call_args_list)


# --- from tests/test_main_run_module.py: integration-like test running module main
def test_run_module_main_executes_pipeline():
    # small dataframes matching minimal expected columns
    ops = pd.DataFrame({
        "date_heure_reception_alerte": ["2023-01-01T00:00:00Z"],
        "date_heure_fin_operation": ["2023-01-02T00:00:00Z"],
        "latitude": [45.0],
        "longitude": [2.0],
    })

    flot = pd.DataFrame({"numero_ordre": [1], "pavillon": ["FR"]})
    res = pd.DataFrame({"resultat_flotteur": ["ok"]})

    def fake_read_csv(path, *args, **kwargs):
        if "operations_clean.csv" in str(path):
            return ops
        if "flotteurs_clean.csv" in str(path):
            return flot
        if "resultats_humain_clean.csv" in str(path):
            return res
        return pd.DataFrame()

    # Read the source and extract the __main__ block
    src_path = main_mod.__file__
    with open(src_path, "r", encoding="utf8") as f:
        lines = f.read().splitlines()

    idx_if = next(i for i, ln in enumerate(lines) if ln.strip().startswith('if __name__') )
    body_lines = lines[idx_if + 1 :]
    body = textwrap.dedent("\n".join(body_lines))
    body_start_line = idx_if + 2

    # Prefix newlines so compiled code maps to the original file line numbers
    prefix = "\n" * (body_start_line - 1)
    exec_src = prefix + body

    # Prepare globals for execution of the main block
    g = {
        "__name__": "__main__",
        "load_raw_data": lambda: (ops, flot, res),
        "clean_operations": main_mod.clean_operations,
        "clean_flotteurs": main_mod.clean_flotteurs,
        "clean_resultats": main_mod.clean_resultats,
        "save_clean_data": lambda a, b, c: None,
        "pd": pd,
        "os": main_mod.os,
        "operations_dtypes": {},
        "flotteurs_dtypes": {},
        "resultats_humain_dtypes": {},
        "OperationsSchema": object,
        "FlotteursSchema": object,
        "ResultatsHumainSchema": object,
        "get_engine": lambda: MagicMock(),
        "insert_dataframe": lambda df, table_name, engine: g.setdefault("_insert_calls", []).append(table_name),
        "validate_df": lambda df, schema, schema_name: df,
    }

    # ensure pd.read_csv used in the exec uses our fake
    g["pd"].read_csv = fake_read_csv

    # compile with filename set to the real module so coverage attributes lines correctly
    code_obj = compile(exec_src, src_path, "exec")
    exec(code_obj, g, g)

    # verify insert_dataframe was called for expected tables
    called = g.get("_insert_calls", [])
    assert "operation" in called
    assert "flotteurs" in called
    assert "resultats_humain" in called
