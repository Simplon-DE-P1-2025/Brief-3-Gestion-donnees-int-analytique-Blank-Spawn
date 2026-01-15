import os
from typing import List, Dict, Optional, Any, Union

from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client() -> Client:
    """
    Initialise et retourne un client Supabase.
    """
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL ou SUPABASE_KEY manquant dans le .env"
        )

    return create_client(url, key)


def fetch_data(
    table_name: str,
    columns: str = "*",
    limit: Optional[int] = None,
    order_by: Optional[str] = None
) -> List[Dict]:
    """
    Récupère des données avec un tri optionnel pour stabiliser l'affichage.
    """
    supabase = get_supabase_client()
    query = supabase.table(table_name).select(columns)

    if order_by:
        query = query.order(order_by)
    
    if limit is not None:
        query = query.limit(limit)

    response = query.execute()

    if response.data is None:
        raise RuntimeError(f"Supabase fetch error ({table_name})")

    return response.data


def insert_row(table_name: str, data: Dict) -> Dict:
    """
    Insère une ligne dans une table Supabase.
    """
    supabase = get_supabase_client()
    response = supabase.table(table_name).insert(data).execute()

    if not response.data:
        raise RuntimeError(f"Supabase insert error ({table_name})")

    return response.data[0]


def update_row(
    table_name: str,
    row_id: Any,
    data: Dict,
    id_column: Union[str, List[str]] = "id",
) -> Dict:
    """
    Met à jour une ligne. Gère les clés simples (str) et composites (list).
    
    Args:
        row_id: Valeur simple ou dictionnaire {colonne: valeur} pour les clés composites.
        id_column: Nom de la colonne ou liste de noms de colonnes.
    """
    supabase = get_supabase_client()
    query = supabase.table(table_name).update(data)

    # Gestion des filtres (WHERE)
    if isinstance(id_column, list):
        for col in id_column:
            # On cherche la valeur dans le dictionnaire row_id
            val = row_id[col] if isinstance(row_id, dict) else row_id
            query = query.eq(col, val)
    else:
        query = query.eq(id_column, row_id)

    response = query.execute()

    if not response.data:
        raise RuntimeError(f"Supabase update error ({table_name}) - Row not found or error")

    return response.data[0]


def delete_row(
    table_name: str,
    row_id: Any,
    id_column: Union[str, List[str]] = "id",
) -> List[Dict]:
    """
    Supprime une ligne. Gère les clés simples (str) et composites (list).
    """
    supabase = get_supabase_client()
    query = supabase.table(table_name).delete()

    if isinstance(id_column, list):
        for col in id_column:
            val = row_id[col] if isinstance(row_id, dict) else row_id
            query = query.eq(col, val)
    else:
        query = query.eq(id_column, row_id)

    response = query.execute()

    if response.data is None:
        raise RuntimeError(f"Supabase delete error ({table_name})")

    return response.data