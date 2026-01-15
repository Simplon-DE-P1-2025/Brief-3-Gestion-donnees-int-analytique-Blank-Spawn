import pandas as pd
import logging
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.schemas.schema_pandera import OperationsSchema, FlotteursSchema, ResultatsHumainSchema
from pipeline.utils.data_types import operations_dtypes, flotteurs_dtypes, resultats_humain_dtypes
from pipeline.utils.db_utils import get_engine, insert_dataframe
from pandera.errors import SchemaErrors
import pandera as pa

# ============================
# 1. Chargement des données brutes
# ============================

def load_raw_data():
    operations = pd.read_csv("pipeline/data/operations.csv")
    flotteurs = pd.read_csv("pipeline/data/flotteurs.csv")
    resultats = pd.read_csv("pipeline/data/resultats_humain.csv")
    return operations, flotteurs, resultats


# ============================
# 2. Nettoyage OPERATIONS
# ============================

def clean_operations(df):

    # Convertir les dates avec gestion des dates aberrantes
    df['date_heure_reception_alerte'] = pd.to_datetime(
        df['date_heure_reception_alerte'], errors='coerce'
    )

    df['date_heure_fin_operation'] = pd.to_datetime(
        df['date_heure_fin_operation'], errors='coerce'
    )

    # Colonnes numériques
    numeric_cols = [
        'latitude', 'longitude',
        'vent_direction', 'vent_force', 'mer_force'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    #  Conversion spécifique pour numero_sitrep
    if 'numero_sitrep' in df.columns:
        df['numero_sitrep'] = pd.to_numeric(df['numero_sitrep'], errors='coerce')

    # Colonnes texte
    text_cols = [
        'type_operation', 'pourquoi_alerte', 'moyen_alerte', 'qui_alerte',
        'categorie_qui_alerte', 'cross', 'departement', 'evenement',
        'categorie_evenement', 'autorite', 'seconde_autorite',
        'zone_responsabilite', 'vent_direction_categorie',
        'cross_sitrep', 'fuseau_horaire', 'systeme_source'
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype('string')

    return df



# ============================
# 3. Nettoyage FLOTTEURS
# ============================

def clean_flotteurs(df):

    # Supprimer les doublons
    df = df.drop_duplicates()

    # Convertir numero_ordre en numérique
    if 'numero_ordre' in df.columns:
        df['numero_ordre'] = pd.to_numeric(df['numero_ordre'], errors='coerce')

    # Colonnes texte
    text_cols = [
        'pavillon', 'resultat_flotteur', 'type_flotteur',
        'categorie_flotteur', 'numero_immatriculation'
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype('string')

    return df


# ============================
# 4. Nettoyage RESULTATS_HUMAIN
# ============================

def clean_resultats(df):

    # Harmoniser les types texte
    if 'resultat_flotteur' in df.columns:
        df['resultat_flotteur'] = df['resultat_flotteur'].astype('string')

    return df


# ============================
# 5. Sauvegarde des données nettoyées
# ============================

def save_clean_data(ops, flot, res):
    os.makedirs("pipeline/data", exist_ok=True)

    ops.to_csv("pipeline/data/operations_clean.csv", index=False)
    flot.to_csv("pipeline/data/flotteurs_clean.csv", index=False)
    res.to_csv("pipeline/data/resultats_humain_clean.csv", index=False)

    print("✔ Données nettoyées enregistrées dans pipeline/data/")


# ============================
# 6. Validation des dataframes
# ============================

def validate_df(
    df: pd.DataFrame,
    schema,
    schema_name: str
) -> pd.DataFrame:
    try:
        return schema.validate(df, lazy=True)

    except SchemaErrors as e:
        logging.error(f"❌ Validation échouée pour le schéma : {schema_name}")
        logging.error("➡️ Détails des erreurs Pandera :")

        # Pandera may expose different attributes depending on version
        if hasattr(e, "failure_cases"):
            logging.error(e.failure_cases)
        elif hasattr(e, "schema_errors"):
            logging.error(e.schema_errors)
        else:
            logging.error(str(e))

        raise RuntimeError(
            f"Validation Pandera échouée pour le schéma '{schema_name}'"
        ) from e


# ============================
# Pipeline principal
# ============================

if __name__ == "__main__":
    # Extraction des données
    ops, flot, res = load_raw_data()

    # Nettoyage
    ops = clean_operations(ops)
    flot = clean_flotteurs(flot)
    res = clean_resultats(res)
    save_clean_data(ops, flot, res)

    # Ré-hydrater les données (car repasser par un CSV nous fait perdre certains types de données)
    date_cols_ops = [
        "date_heure_reception_alerte",
        "date_heure_fin_operation"
    ]

    ops_clean = pd.read_csv(
        "pipeline/data/operations_clean.csv",
        dtype=operations_dtypes,
        parse_dates=date_cols_ops,
        date_parser=lambda col: pd.to_datetime(col, utc=True)
    )

    # reconvertir les dates AVANT validation
    ops_clean["date_heure_reception_alerte"] = pd.to_datetime(ops_clean["date_heure_reception_alerte"], errors="coerce")
    ops_clean["date_heure_fin_operation"] = pd.to_datetime(ops_clean["date_heure_fin_operation"], errors="coerce")

    ops_clean["date_heure_reception_alerte"] = pd.to_datetime(
        ops_clean["date_heure_reception_alerte"],
        errors="coerce",
        utc=True
    )

    ops_clean["date_heure_fin_operation"] = pd.to_datetime(
        ops_clean["date_heure_fin_operation"],
        errors="coerce",
        utc=True
    )

    # Check intégrité Pandera avec nom de schéma
    schema_mapping = {
        "operations": (ops_clean, OperationsSchema, "operation"),
        "flotteurs": (
            pd.read_csv(
                "pipeline/data/flotteurs_clean.csv",
                dtype=flotteurs_dtypes
            ),
            FlotteursSchema,
            "flotteurs"
        ),
        "resultats_humain": (
            pd.read_csv(
                "pipeline/data/resultats_humain_clean.csv",
                dtype=resultats_humain_dtypes
            ),
            ResultatsHumainSchema,
            "resultats_humain"
        )
    }

    supa_engine = get_engine()

    for name, (df, schema, table_name) in schema_mapping.items():
        df_valid = validate_df(df, schema=schema, schema_name=name)
    
        # Chargement en base de données
        if table_name == 'operation':
            conflict_cols = ['operation_id']
            conflict_constraint = None
        elif table_name == 'flotteurs':
            conflict_cols = ['operation_id', 'numero_ordre']
            conflict_constraint = None
        elif table_name == 'resultats_humain':
            conflict_cols = None
            conflict_constraint = 'resultats_humain_unique'
        else:
            conflict_cols = None
            conflict_constraint = None
        insert_dataframe(
            df,
            table_name,
            supa_engine,
            conflict_cols=conflict_cols,
            conflict_constraint=conflict_constraint
        )