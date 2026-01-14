import pandera as pa
import pandas as pd
from pandera import DataFrameSchema, Check


# ============================
# 1. Schéma OPERATIONS
# ============================

OperationsSchema = DataFrameSchema({

    "operation_id": pa.Column(int, nullable=False),

    "type_operation": pa.Column(pa.String, nullable=True),
    "pourquoi_alerte": pa.Column(pa.String, nullable=True),
    "moyen_alerte": pa.Column(pa.String, nullable=True),
    "qui_alerte": pa.Column(pa.String, nullable=True),
    "categorie_qui_alerte": pa.Column(pa.String, nullable=True),
    "cross_type": pa.Column(pa.String, nullable=True),
    "departement": pa.Column(pa.String, nullable=True),
    "evenement": pa.Column(pa.String, nullable=True),
    "categorie_evenement": pa.Column(pa.String, nullable=True),
    "autorite": pa.Column(pa.String, nullable=True),
    "seconde_autorite": pa.Column(pa.String, nullable=True),
    "zone_responsabilite": pa.Column(pa.String, nullable=True),
    "vent_direction_categorie": pa.Column(pa.String, nullable=True),
    "cross_sitrep": pa.Column(pa.String, nullable=True),
    "fuseau_horaire": pa.Column(pa.String, nullable=True),
    "systeme_source": pa.Column(pa.String, nullable=True),

    "latitude": pa.Column(float, nullable=True, checks=Check.in_range(-90, 90)),
    "longitude": pa.Column(float, nullable=True, checks=Check.in_range(-180, 180)),
    "vent_direction": pa.Column(float, nullable=True, checks=Check.in_range(0, 360)),
    "vent_force": pa.Column(float, nullable=True, checks=Check.ge(0)),
    "mer_force": pa.Column(float, nullable=True, checks=Check.ge(0)),

    "date_heure_reception_alerte": pa.Column(
        pd.DatetimeTZDtype(tz="UTC"),
        nullable=True
    ),
    "date_heure_fin_operation": pa.Column(
        pd.DatetimeTZDtype(tz="UTC"),
        nullable=True
    ),

    "numero_sitrep": pa.Column(pa.Int, nullable=True),
})


# ============================
# 2. Schéma FLOTTEURS
# ============================

FlotteursSchema = DataFrameSchema({

    "operation_id": pa.Column(int, nullable=False),
    "numero_ordre": pa.Column(float, nullable=True),

    "pavillon": pa.Column(pa.String, nullable=True),
    "resultat_flotteur": pa.Column(pa.String, nullable=True),
    "type_flotteur": pa.Column(pa.String, nullable=True),
    "categorie_flotteur": pa.Column(pa.String, nullable=True),
    "numero_immatriculation": pa.Column(pa.String, nullable=True),
})


# ============================
# 3. Schéma RESULTATS HUMAIN
# ============================

ResultatsHumainSchema = DataFrameSchema({

    "operation_id": pa.Column(int, nullable=False),

    "categorie_personne": pa.Column(pa.String, nullable=True),
    "resultat_humain": pa.Column(pa.String, nullable=True),

    "nombre": pa.Column(int, nullable=True),
    "dont_nombre_blesse": pa.Column(int, nullable=True),

})