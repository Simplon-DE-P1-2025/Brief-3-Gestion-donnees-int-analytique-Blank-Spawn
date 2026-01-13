import pandera as pa
from pandera import Column, DataFrameSchema, Check
import pandas as pd


# ============================
# 1. Schéma OPERATIONS
# ============================

OperationsSchema = DataFrameSchema({

    # Identifiant
    "operation_id": Column(int, nullable=False),

    # Colonnes texte
    "type_operation": Column(pa.String, nullable=True),
    "pourquoi_alerte": Column(pa.String, nullable=True),
    "moyen_alerte": Column(pa.String, nullable=True),
    "qui_alerte": Column(pa.String, nullable=True),
    "categorie_qui_alerte": Column(pa.String, nullable=True),
    "cross": Column(pa.String, nullable=True),
    "departement": Column(pa.String, nullable=True),
    "evenement": Column(pa.String, nullable=True),
    "categorie_evenement": Column(pa.String, nullable=True),
    "autorite": Column(pa.String, nullable=True),
    "seconde_autorite": Column(pa.String, nullable=True),
    "zone_responsabilite": Column(pa.String, nullable=True),
    "vent_direction_categorie": Column(pa.String, nullable=True),
    "cross_sitrep": Column(pa.String, nullable=True),
    "fuseau_horaire": Column(pa.String, nullable=True),
    "systeme_source": Column(pa.String, nullable=True),

    # Colonnes numériques
    "latitude": Column(float, nullable=True, checks=Check.in_range(-90, 90)),
    "longitude": Column(float, nullable=True, checks=Check.in_range(-180, 180)),
    "vent_direction": Column(float, nullable=True, checks=Check.in_range(0, 360)),
    "vent_force": Column(float, nullable=True, checks=Check.ge(0)),
    "mer_force": Column(float, nullable=True, checks=Check.ge(0)),

    # Dates
    "date_heure_reception_alerte": Column(pa.DateTime, nullable=True),
    "date_heure_fin_operation": Column(pa.DateTime, nullable=True),

    # Autres
    "numero_sitrep": Column(pa.String, nullable=True),
    "cross_sitrep": Column(pa.String, nullable=True),
})


# ============================
# 2. Schéma FLOTTEURS
# ============================

FlotteursSchema = DataFrameSchema({

    "operation_id": Column(int, nullable=False),
    "numero_ordre": Column(float, nullable=True),

    "pavillon": Column(pa.String, nullable=True),
    "resultat_flotteur": Column(pa.String, nullable=True),
    "type_flotteur": Column(pa.String, nullable=True),
    "categorie_flotteur": Column(pa.String, nullable=True),
    "numero_immatriculation": Column(pa.String, nullable=True),
})


# ============================
# 3. Schéma RESULTATS HUMAIN
# ============================

ResultatsHumainSchema = DataFrameSchema({

    "operation_id": Column(int, nullable=False),
    "resultat_flotteur": Column(pa.String, nullable=True),
})
