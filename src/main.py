import pandas as pd
import pandera as pa
from pandera.errors import SchemaError, SchemaErrors
import logging
import os
from schemas.schema_pandera import OperationsSchema, FlotteursSchema, ResultatsHumainSchema
from utils.db_utils import get_engine, insert_dataframe

# ============================
# 1. Chargement des données brutes
# ============================

def load_raw_data():
    operations = pd.read_csv("data/operations.csv")
    flotteurs = pd.read_csv("data/flotteurs.csv")
    resultats = pd.read_csv("data/resultats_humain.csv")
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

    os.makedirs("data", exist_ok=True)

    ops.to_csv("data/operations_clean.csv", index=False)
    flot.to_csv("data/flotteurs_clean.csv", index=False)
    res.to_csv("data/resultats_humain_clean.csv", index=False)

    print("✔ Données nettoyées enregistrées dans data/")


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
        logging.error(e.failure_cases)

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

    ops_clean = pd.read_csv("data/operations_clean.csv")

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
            pd.read_csv("data/flotteurs_clean.csv"),
            FlotteursSchema,
            "flotteurs"
        ),
        "resultats_humain": (
            pd.read_csv("data/resultats_humain_clean.csv"),
            ResultatsHumainSchema,
            "resultats_humain"
        )
    }

    supa_engine = get_engine()

    for name, (df, schema, table_name) in schema_mapping.items():
        df_valid = validate_df(df, schema=schema, schema_name=name)
    
        # Chargement en base de données
        insert_dataframe(
            df,
            table_name,
            supa_engine,
            schema=schema
        )