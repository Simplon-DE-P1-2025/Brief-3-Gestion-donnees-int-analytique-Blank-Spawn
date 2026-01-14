import os
import sys
from unittest.mock import patch, MagicMock
from pandera.errors import SchemaErrors
import pandas as pd
import pytest

# ensure project root and src are on path so imports in src.main (and top-level packages) resolve
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, PROJECT_ROOT)
if os.path.isdir(SRC_PATH):
    sys.path.insert(0, SRC_PATH)

from src.main import (
    load_raw_data,
    clean_operations,
    clean_flotteurs,
    clean_resultats,
    save_clean_data,
    validate_df,
)


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
        mock_makedirs.assert_called_with("data", exist_ok=True)
        assert mock_to_csv.call_count == 3


def test_validate_df_success_and_failure():
    df = pd.DataFrame({"col": [1, 2, 3]})
    mock_schema = MagicMock()
    mock_schema.validate.return_value = df
    res = validate_df(df, mock_schema, "test_schema")
    assert res.equals(df)
    mock_schema.validate.assert_called_once()

    mock_schema_fail = MagicMock()
    mock_schema_fail.validate.side_effect = SchemaErrors(
        "error", pd.DataFrame({"col": ["error_detail"]})
    )
    with patch("logging.error") as mock_log_error:
        with pytest.raises(RuntimeError):
            validate_df(df, mock_schema_fail, "test_schema")
        assert mock_log_error.called


import os
import sys
from unittest.mock import patch, MagicMock
from pandera.errors import SchemaErrors
import pandas as pd
import pytest

# ensure project root and src are on path so imports in src.main (and top-level packages) resolve
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, PROJECT_ROOT)
if os.path.isdir(SRC_PATH):
    sys.path.insert(0, SRC_PATH)

from src.main import (
    load_raw_data,
    clean_operations,
    clean_flotteurs,
    clean_resultats,
    save_clean_data,
    validate_df,
)


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
        mock_makedirs.assert_called_with("data", exist_ok=True)
        assert mock_to_csv.call_count == 3


def test_validate_df_success_and_failure():
    df = pd.DataFrame({"col": [1, 2, 3]})
    mock_schema = MagicMock()
    mock_schema.validate.return_value = df
    res = validate_df(df, mock_schema, "test_schema")
    assert res.equals(df)
    mock_schema.validate.assert_called_once()

    mock_schema_fail = MagicMock()
    mock_schema_fail.validate.side_effect = SchemaErrors(
        "error", pd.DataFrame({"col": ["error_detail"]})
    )
    with patch("logging.error") as mock_log_error:
        with pytest.raises(RuntimeError):
            validate_df(df, mock_schema_fail, "test_schema")
        assert mock_log_error.called