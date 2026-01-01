
from __future__ import annotations
import streamlit as st
from components import inject_premium_css, top_navbar



inject_premium_css()
top_navbar(active="Dashboard")


import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
from pathlib import Path


# -----------------------------
# Config
# -----------------------------
DEFAULT_DB = "../data/offers.sqlite"   # adapte si besoin
TABLE = "offers"

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )
}
from dotenv import load_dotenv

load_dotenv()
# -----------------------------
# Utils
# -----------------------------
def sha1_uid(source: str, url: str) -> str:
    s = f"{source}::{url}".encode("utf-8", errors="ignore")
    return hashlib.sha1(s).hexdigest()


def clean_ws(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s or None


def now_sql() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def db_connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def table_columns(con: sqlite3.Connection, table: str) -> List[str]:
    rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    return [r["name"] for r in rows]


def upsert_offer(con: sqlite3.Connection, table: str, record: Dict[str, Any]) -> Tuple[bool, str]:
    """
    UPSERT by uid. Returns (inserted_or_updated, uid).
    We only keep keys that exist in table columns.
    """
    cols = set(table_columns(con, table))
    rec = {k: v for k, v in record.items() if k in cols}

    if "uid" not in rec or not rec["uid"]:
        raise ValueError("uid manquant")
    if "created_at" in cols and not rec.get("created_at"):
        rec["created_at"] = now_sql()

    keys = list(rec.keys())
    placeholders = ",".join(["?"] * len(keys))
    col_list = ",".join(keys)

    # update everything except uid
    update_cols = [k for k in keys if k != "uid"]
    set_clause = ", ".join([f"{k}=excluded.{k}" for k in update_cols]) if update_cols else ""

    sql = f"""
    INSERT INTO {table} ({col_list})
    VALUES ({placeholders})
    ON CONFLICT(uid) DO UPDATE SET {set_clause}
    """

    con.execute(sql, [rec[k] for k in keys])
    con.commit()
    return True, rec["uid"]


def count_offers(con: sqlite3.Connection, table: str) -> int:
    return int(con.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])


# -----------------------------
# France Travail API (simplified)
# -----------------------------
FT_TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
FT_SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
FT_DETAIL_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/"  # + id


def ft_get_token() -> str:
    client_id = os.getenv("FT_CLIENT_ID")
    client_secret = os.getenv("FT_CLIENT_SECRET")
    scope = os.getenv("FRANCE_TRAVAIL_SCOPE", "api_offresdemploiv2")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Variables d'env manquantes: FT_CLIENT_ID / FT_CLIENT_SECRET "
            "(optionnel: FRANCE_TRAVAIL_SCOPE)."
        )

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
    }
    r = requests.post(FT_TOKEN_URL, data=data, headers=UA, timeout=30)
    r.raise_for_status()
    js = r.json()
    return js["access_token"]


def ft_search_offers(
    token: str,
    keywords: str,
    departement: Optional[str],
    contrat: Optional[str],
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """
    France Travail search (best effort). We fetch in pages of 20.
    """
    headers = {**UA, "Authorization": f"Bearer {token}", "Accept": "application/json"}
    out: List[Dict[str, Any]] = []

    start = 0
    page_size = 20

    while len(out) < max_results:
        params = {
            "motsCles": keywords,
            "range": f"{start}-{start+page_size-1}",
        }
        if departement:
            params["departement"] = departement
        if contrat:
            # FT uses codes sometimes; we leave free text if supported by your account
            params["typeContrat"] = contrat

        r = requests.get(FT_SEARCH_URL, headers=headers, params=params, timeout=30)
        if r.status_code == 204:
            break
        r.raise_for_status()
        js = r.json()

        offres = js.get("resultats") or js.get("offres") or js.get("results") or []
        if not offres:
            break

        for o in offres:
            out.append(o)
            if len(out) >= max_results:
                break

        start += page_size

    return out


def ft_offer_to_record(o: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize minimal fields into your DB schema.
    URL public = candidat.francetravail... (OK for apply link)
    """
    offer_id = o.get("id") or o.get("identifiant") or o.get("numeroOffre")
    title = None
    employer = None
    location = None
    contract_type = None
    salary = None
    published_date = None
    raw_text = None

    # best effort with known FT fields
    title = o.get("intitule") or o.get("titre")
    entreprise = o.get("entreprise") or {}
    if isinstance(entreprise, dict):
        employer = entreprise.get("nom") or entreprise.get("name")

    lieu = o.get("lieuTravail") or {}
    if isinstance(lieu, dict):
        lib = lieu.get("libelle")
        dept = lieu.get("departement")
        location = clean_ws(" - ".join([x for x in [dept, lib] if x]))

    contrat = o.get("typeContratLibelle") or o.get("typeContrat")
    contract_type = clean_ws(contrat)

    salaire = o.get("salaire") or {}
    if isinstance(salaire, dict):
        salary = salaire.get("libelle") or salaire.get("commentaire")
    else:
        salary = salaire if isinstance(salaire, str) else None

    published_date = o.get("dateCreation") or o.get("dateActualisation")

    desc = o.get("description") or ""
    if isinstance(desc, str) and desc.strip():
        raw_text = desc.strip()

    # apply/public URL
    url = None
    if offer_id:
        url = f"https://candidat.francetravail.fr/offres/recherche/detail/{offer_id}"

    return {
        "uid": sha1_uid("france_travail", url or f"france_travail::{offer_id}"),
        "source": "france_travail",
        "offer_id": str(offer_id) if offer_id is not None else None,
        "url": url,
        "title": clean_ws(title),
        "employer": clean_ws(employer),
        "location": clean_ws(location),
        "contract_type": clean_ws(contract_type),
        "salary": clean_ws(salary),
        "remote": "unknown",
        "published_date": clean_ws(published_date),
        "raw_text": (raw_text or "")[:12000],
        "created_at": now_sql(),
    }


# -----------------------------
# Adzuna API (simplified)
# -----------------------------
ADZUNA_SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/fr/search/1"


def adzuna_search(
    keywords: str,
    where: Optional[str],
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError("Variables d'env manquantes: ADZUNA_APP_ID / ADZUNA_APP_KEY")

    out: List[Dict[str, Any]] = []
    page = 1
    page_size = 50  # Adzuna accepts up to ~50

    while len(out) < max_results:
        url = f"https://api.adzuna.com/v1/api/jobs/fr/search/{page}"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": min(page_size, max_results - len(out)),
            "what": keywords,
        }
        if where:
            params["where"] = where

        r = requests.get(url, headers=UA, params=params, timeout=30)
        r.raise_for_status()
        js = r.json()
        results = js.get("results") or []
        if not results:
            break

        out.extend(results)
        page += 1

    return out[:max_results]


def adzuna_offer_to_record(o: Dict[str, Any]) -> Dict[str, Any]:
    title = o.get("title")
    employer = (o.get("company") or {}).get("display_name") if isinstance(o.get("company"), dict) else None
    location = None
    if isinstance(o.get("location"), dict):
        location = o["location"].get("display_name")

    url = o.get("redirect_url") or o.get("adref") or o.get("url")
    offer_id = o.get("id")

    salary = None
    if o.get("salary_min") is not None or o.get("salary_max") is not None:
        salary = f"{o.get('salary_min')} - {o.get('salary_max')}"
    contract_type = o.get("contract_type") or o.get("contract_time")
    published_date = o.get("created") or o.get("created_at")

    desc = o.get("description") or ""
    raw_text = clean_ws(desc) or ""

    return {
        "uid": sha1_uid("adzuna", url or f"adzuna::{offer_id}"),
        "source": "adzuna",
        "offer_id": str(offer_id) if offer_id is not None else None,
        "url": clean_ws(url),
        "title": clean_ws(title),
        "employer": clean_ws(employer),
        "location": clean_ws(location),
        "contract_type": clean_ws(contract_type),
        "salary": clean_ws(salary),
        "remote": "unknown",
        "published_date": clean_ws(published_date),
        "raw_text": raw_text[:12000],
        "created_at": now_sql(),
    }


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Ajouter des offres", page_icon="➕", layout="wide")

st.title("➕ Ajouter des offres d’emploi")
st.caption("Ajout manuel ou via API (France Travail / Adzuna) — avec anti-doublons (UPSERT SQLite).")

db_path = st.sidebar.text_input("Chemin SQLite", value=DEFAULT_DB)
table_name = st.sidebar.text_input("Table", value=TABLE)

with st.sidebar:
    st.markdown("### État DB")
    try:
        con = db_connect(db_path)
        n = count_offers(con, table_name)
        st.success(f"{n:,} offres dans `{table_name}`")
        con.close()
    except Exception as e:
        st.error(f"DB non accessible: {e}")

tabs = st.tabs(["✍️ Ajout manuel", "🇫🇷 France Travail (API)", "🌍 Adzuna (API)"])


# -------- Manual
with tabs[0]:
    st.subheader("✍️ Ajouter une offre manuellement")

    with st.form("manual_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            source = st.selectbox("Source", ["manual"], index=0)
            url = st.text_input("URL (lien pour postuler)", placeholder="https://...")
            offer_id = st.text_input("Offer ID (optionnel)")
        with col2:
            title = st.text_input("Titre")
            employer = st.text_input("Entreprise")
            contract_type = st.text_input("Type de contrat (CDI/CDD/Stage...)")
        with col3:
            location = st.text_input("Localisation (ex: 75 - Paris)")
            salary = st.text_input("Salaire (optionnel)")
            remote = st.selectbox("Télétravail", ["unknown", "yes", "no"], index=0)

        published_date = st.text_input("Date publication (optionnel)", placeholder="2025-12-19T15:58:20Z")
        raw_text = st.text_area("Texte de l’offre (raw_text)", height=180)

        submitted = st.form_submit_button("✅ Insérer / Mettre à jour (UPSERT)")

    if submitted:
        try:
            if not url:
                st.error("URL obligatoire (sert de lien 'postuler' + identifiant anti-doublon).")
            else:
                record = {
                    "uid": sha1_uid(source, url),
                    "source": source,
                    "offer_id": clean_ws(offer_id),
                    "url": clean_ws(url),
                    "title": clean_ws(title),
                    "employer": clean_ws(employer),
                    "location": clean_ws(location),
                    "contract_type": clean_ws(contract_type),
                    "salary": clean_ws(salary),
                    "remote": remote,
                    "published_date": clean_ws(published_date),
                    "raw_text": clean_ws(raw_text)[:12000] if raw_text else "",
                    "created_at": now_sql(),
                }
                con = db_connect(db_path)
                upsert_offer(con, table_name, record)
                st.success("✅ Offre ajoutée / mise à jour !")
                st.json(record)
                con.close()
        except Exception as e:
            st.exception(e)


# -------- France Travail API
with tabs[1]:
    st.subheader("🇫🇷 Ajouter via France Travail API")
    st.info(
        "Nécessite les variables d'environnement : FT_CLIENT_ID, FT_CLIENT_SECRET "
        "(optionnel: FRANCE_TRAVAIL_SCOPE)."
    )

    colA, colB, colC = st.columns([2, 1, 1])
    with colA:
        ft_keywords = st.text_input("Mots-clés", value="data scientist")
    with colB:
        ft_dept = st.text_input("Département (optionnel)", value="", placeholder="ex: 75")
    with colC:
        ft_max = st.number_input("Max résultats", min_value=1, max_value=200, value=30, step=5)

    ft_contrat = st.text_input("Type contrat (optionnel)", value="", placeholder="CDI / CDD / Stage...")

    if st.button("🔎 Rechercher (France Travail)"):
        try:
            token = ft_get_token()
            results = ft_search_offers(
                token=token,
                keywords=ft_keywords,
                departement=ft_dept or None,
                contrat=ft_contrat or None,
                max_results=int(ft_max),
            )

            # petite table de sélection
            rows = []
            for o in results:
                offer_id = o.get("id") or o.get("identifiant") or o.get("numeroOffre")
                title = o.get("intitule") or o.get("titre")
                entreprise = o.get("entreprise") or {}
                employer = entreprise.get("nom") if isinstance(entreprise, dict) else None
                lieu = o.get("lieuTravail") or {}
                loc = lieu.get("libelle") if isinstance(lieu, dict) else None
                rows.append(
                    {
                        "offer_id": offer_id,
                        "title": title,
                        "employer": employer,
                        "location": loc,
                    }
                )

            df = pd.DataFrame(rows)
            st.session_state["ft_results_raw"] = results
            st.dataframe(df, use_container_width=True)

            st.success(f"✅ {len(results)} résultats chargés. Sélectionne ensuite ceux à insérer.")
        except Exception as e:
            st.exception(e)

    if "ft_results_raw" in st.session_state:
        results = st.session_state["ft_results_raw"]
        ids = []
        for o in results:
            oid = o.get("id") or o.get("identifiant") or o.get("numeroOffre")
            if oid is not None:
                ids.append(str(oid))

        selected = st.multiselect("Sélectionner des offer_id à insérer", options=ids, default=ids[: min(10, len(ids))])

        if st.button("✅ Insérer les offres sélectionnées (UPSERT)"):
            try:
                con = db_connect(db_path)
                inserted = 0
                for o in results:
                    oid = o.get("id") or o.get("identifiant") or o.get("numeroOffre")
                    if oid is None:
                        continue
                    if str(oid) not in selected:
                        continue

                    record = ft_offer_to_record(o)
                    upsert_offer(con, table_name, record)
                    inserted += 1

                con.close()
                st.success(f"✅ {inserted} offres France Travail insérées/mises à jour.")
            except Exception as e:
                st.exception(e)


# -------- Adzuna API
with tabs[2]:
    st.subheader("🌍 Ajouter via Adzuna API")
    st.info("Nécessite les variables d'environnement : ADZUNA_APP_ID, ADZUNA_APP_KEY")

    colA, colB, colC = st.columns([2, 2, 1])
    with colA:
        adz_keywords = st.text_input("Mots-clés", value="data engineer")
    with colB:
        adz_where = st.text_input("Lieu (optionnel)", value="France", placeholder="Paris / Lyon / France")
    with colC:
        adz_max = st.number_input("Max résultats", min_value=1, max_value=500, value=50, step=10)

    if st.button("🔎 Rechercher (Adzuna)"):
        try:
            results = adzuna_search(adz_keywords, where=adz_where or None, max_results=int(adz_max))

            rows = []
            for o in results:
                rows.append(
                    {
                        "offer_id": o.get("id"),
                        "title": o.get("title"),
                        "employer": (o.get("company") or {}).get("display_name") if isinstance(o.get("company"), dict) else None,
                        "location": (o.get("location") or {}).get("display_name") if isinstance(o.get("location"), dict) else None,
                        "url": o.get("redirect_url") or o.get("adref"),
                    }
                )

            df = pd.DataFrame(rows)
            st.session_state["adz_results_raw"] = results
            st.dataframe(df, use_container_width=True)
            st.success(f"✅ {len(results)} résultats chargés. Sélectionne ensuite ceux à insérer.")
        except Exception as e:
            st.exception(e)

    if "adz_results_raw" in st.session_state:
        results = st.session_state["adz_results_raw"]
        ids = [str(o.get("id")) for o in results if o.get("id") is not None]

        selected = st.multiselect("Sélectionner des offer_id à insérer", options=ids, default=ids[: min(10, len(ids))])

        if st.button("✅ Insérer les offres sélectionnées (UPSERT)", key="adz_insert"):
            try:
                con = db_connect(db_path)
                inserted = 0
                for o in results:
                    oid = o.get("id")
                    if oid is None:
                        continue
                    if str(oid) not in selected:
                        continue

                    record = adzuna_offer_to_record(o)
                    upsert_offer(con, table_name, record)
                    inserted += 1

                con.close()
                st.success(f"✅ {inserted} offres Adzuna insérées/mises à jour.")
            except Exception as e:
                st.exception(e)
