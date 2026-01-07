import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def normalize_france_travail(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        lieu = r.get("lieu", {})
        ent = r.get("entreprise", {})
        out.append({
            "id_offre": f"FT_{r.get('id')}",
            "source": "France Travail",
            "titre": r.get("intitule"),
            "description": r.get("description"),
            "date_publication": r.get("dateCreation"),
            "lieu_nom": lieu.get("libelle"),
            "code_postal": lieu.get("codePostal"),
            "entreprise": ent.get("nom"),
            "type_contrat": r.get("typeContrat"),
            "url": None
        })
    return out

def normalize_emploi_territorial(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        out.append({
            "id_offre": f"ET_{r.get('job_id')}",
            "source": "Emploi Territorial",
            "titre": r.get("keyword"),
            "description": r.get("content"),
            "date_publication": r.get("scraped_at"),
            "lieu_nom": None,
            "code_postal": r.get("dept"),
            "entreprise": None,
            "type_contrat": None,
            "url": r.get("url")
        })
    return out

def normalize_hellowork(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        out.append({
            "id_offre": f"HW_{r.get('id')}",
            "source": "HelloWork",
            "titre": r.get("title"),
            "description": r.get("description"),
            "date_publication": r.get("date"),
            "lieu_nom": r.get("city"),
            "code_postal": r.get("cp"),
            "entreprise": r.get("company"),
            "type_contrat": r.get("contract_type"),
            "url": r.get("link")
        })
    return out