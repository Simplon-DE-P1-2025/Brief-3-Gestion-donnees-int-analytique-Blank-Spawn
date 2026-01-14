# -----------------------------
# Operations
# -----------------------------
operations_dtypes = {
    "operation_id": int,
    "type_operation": str,
    "pourquoi_alerte": str,
    "moyen_alerte": str,
    "qui_alerte": str,
    "categorie_qui_alerte": str,
    "cross": str,
    "departement": str,
    "evenement": str,
    "categorie_evenement": str,
    "autorite": str,
    "seconde_autorite": str,
    "zone_responsabilite": str,
    "vent_direction_categorie": str,
    "cross_sitrep": str,
    "fuseau_horaire": str,
    "systeme_source": str,
    "latitude": float,
    "longitude": float,
    "vent_direction": float,
    "vent_force": float,
    "mer_force": float,
    "numero_sitrep": str
}

# -----------------------------
# Flotteurs
# -----------------------------
flotteurs_dtypes = {
    "operation_id": int,
    "numero_ordre": float,
    "pavillon": str,
    "resultat_flotteur": str,
    "type_flotteur": str,
    "categorie_flotteur": str,
    "numero_immatriculation": str,
}

# -----------------------------
# Resultats Humain
# -----------------------------
resultats_humain_dtypes = {
    "operation_id": int,
    "categorie_personne": str,
    "resultat_humain": str,
    "nombre": "Int64",           # nullable int
    "dont_nombre_blesse": "Int64"  # nullable int
}