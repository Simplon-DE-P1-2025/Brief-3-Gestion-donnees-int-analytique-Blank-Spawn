import os
from typing import List, Dict, Optional, Any

from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client() -> Client:
    """
    Initialise et retourne un client Supabase.
    Connexion via l'API Supabase (PostgREST).
    """

    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY manquant dans le .env"
        )

    return create_client(url, key)



def fetch_data(
    table_name: str,
    columns: str = "*",
    limit: Optional[int] = None,
) -> List[Dict]:
    """
    Récupère des données depuis une table Supabase.

    Args:
        table_name: nom de la table
        columns: colonnes à sélectionner (par défaut *)
        limit: limite optionnelle de lignes

    Returns:
        Liste de dictionnaires (rows)
    """

    supabase = get_supabase_client()

    query = supabase.table(table_name).select(columns)

    if limit is not None:
        query = query.limit(limit)

    response = query.execute()

    if response.error:
        raise RuntimeError(
            f"Supabase fetch error ({table_name}): {response.error}"
        )

    return response.data
def insert_row(
    table_name: str,
    data: Dict,
) -> Dict:
    """
    Insère une ligne dans une table Supabase.

    Args:
        table_name: nom de la table
        data: dictionnaire {colonne: valeur}

    Returns:
        Ligne insérée (dict)
    """

    supabase = get_supabase_client()

    response = (
        supabase
        .table(table_name)
        .insert(data)
        .execute()
    )

    if response.error:
        raise RuntimeError(
            f"Supabase insert error ({table_name}): {response.error}"
        )

    # Supabase retourne une liste
    return response.data[0]
def update_row(
    table_name: str,
    row_id: Any,
    data: Dict,
    id_column: str = "id",
) -> Dict:
    """
    Met à jour une ligne dans une table Supabase.

    Args:
        table_name: nom de la table
        row_id: valeur de l'identifiant
        data: colonnes à mettre à jour
        id_column: nom de la colonne identifiante (par défaut 'id')

    Returns:
        Ligne mise à jour (dict)
    """

    supabase = get_supabase_client()

    response = (
        supabase
        .table(table_name)
        .update(data)
        .eq(id_column, row_id)
        .execute()
    )

    if response.error:
        raise RuntimeError(
            f"Supabase update error ({table_name}): {response.error}"
        )

    return response.data[0]


def delete_row(
    table_name: str,
    row_id,
    id_column: str = "id",
):
    """
    Supprime une ligne d'une table Supabase.

    Args:
        table_name: nom de la table
        row_id: valeur de l'identifiant de la ligne à supprimer
        id_column: nom de la colonne identifiante (par défaut "id")

    Returns:
        Liste contenant la ligne supprimée (dict), selon le comportement Supabase
    """

    supabase = get_supabase_client()

    response = (
        supabase
        .table(table_name)
        .delete()
        .eq(id_column, row_id)
        .execute()
    )

    if response.error:
        raise RuntimeError(
            f"Supabase delete error ({table_name}): {response.error}"
        )

    return response.data
