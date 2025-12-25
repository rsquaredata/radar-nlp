# enrich_geo_sqlite.py
from __future__ import annotations

import argparse
import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from http_utils import RobustSession

BAN_URL = "https://api-adresse.data.gouv.fr/search/"

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
}

# --- Dept -> Region (France, codes officiels) ---
# Remarque: mapping "département" -> "région" (nom lisible)
# On inclut métropole + quelques DROM courants.
DEPT_TO_REGION: Dict[str, str] = {
    # Auvergne-Rhône-Alpes
    "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
    "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
    "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
    "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",
    # Bourgogne-Franche-Comté
    "21": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté", "39": "Bourgogne-Franche-Comté",
    "58": "Bourgogne-Franche-Comté", "70": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
    "89": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",
    # Bretagne
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    # Centre-Val de Loire
    "18": "Centre-Val de Loire", "28": "Centre-Val de Loire", "36": "Centre-Val de Loire",
    "37": "Centre-Val de Loire", "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",
    # Corse
    "2A": "Corse", "2B": "Corse",
    # Grand Est
    "08": "Grand Est", "10": "Grand Est", "51": "Grand Est", "52": "Grand Est", "54": "Grand Est",
    "55": "Grand Est", "57": "Grand Est", "67": "Grand Est", "68": "Grand Est", "88": "Grand Est",
    # Hauts-de-France
    "02": "Hauts-de-France", "59": "Hauts-de-France", "60": "Hauts-de-France", "62": "Hauts-de-France",
    "80": "Hauts-de-France",
    # Île-de-France
    "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France", "91": "Île-de-France",
    "92": "Île-de-France", "93": "Île-de-France", "94": "Île-de-France", "95": "Île-de-France",
    # Normandie
    "14": "Normandie", "27": "Normandie", "50": "Normandie", "61": "Normandie", "76": "Normandie",
    # Nouvelle-Aquitaine
    "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine", "23": "Nouvelle-Aquitaine",
    "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine", "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine",
    "64": "Nouvelle-Aquitaine", "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",
    # Occitanie
    "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie", "31": "Occitanie",
    "32": "Occitanie", "34": "Occitanie", "46": "Occitanie", "48": "Occitanie", "65": "Occitanie",
    "66": "Occitanie", "81": "Occitanie", "82": "Occitanie",
    # Pays de la Loire
    "44": "Pays de la Loire", "49": "Pays de la Loire", "53": "Pays de la Loire", "72": "Pays de la Loire",
    "85": "Pays de la Loire",
    # Provence-Alpes-Côte d'Azur
    "04": "Provence-Alpes-Côte d'Azur", "05": "Provence-Alpes-Côte d'Azur", "06": "Provence-Alpes-Côte d'Azur",
    "13": "Provence-Alpes-Côte d'Azur", "83": "Provence-Alpes-Côte d'Azur", "84": "Provence-Alpes-Côte d'Azur",
    # DROM (à minima)
    "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion", "976": "Mayotte",
}


@dataclass
class Geo:
    city: Optional[str] = None
    postcode: Optional[str] = None
    dept_code: Optional[str] = None
    region: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    score: Optional[float] = None
    source: Optional[str] = None  # "ban" ou "heuristic"


def ensure_geo_columns(db_path: str) -> None:
    """Ajoute les colonnes géo si elles n'existent pas."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("PRAGMA table_info(offers)")
    existing = {row[1] for row in cur.fetchall()}

    cols = [
        ("city", "TEXT"),
        ("postcode", "TEXT"),
        ("dept_code", "TEXT"),
        ("region", "TEXT"),
        ("lat", "REAL"),
        ("lon", "REAL"),
        ("geo_score", "REAL"),
        ("geo_source", "TEXT"),
    ]

    for name, typ in cols:
        if name not in existing:
            cur.execute(f"ALTER TABLE offers ADD COLUMN {name} {typ}")

    con.commit()
    con.close()


def normalize_dept_code(x: str) -> Optional[str]:
    x = (x or "").strip()
    if not x:
        return None
    x = x.upper()
    # Ex: "59" -> "59", "2A" -> "2A", "971" -> "971"
    if re.fullmatch(r"\d{2}", x):
        return x
    if re.fullmatch(r"2A|2B", x):
        return x
    if re.fullmatch(r"\d{3}", x):
        return x
    return None


def dept_to_region(dept: Optional[str]) -> Optional[str]:
    if not dept:
        return None
    return DEPT_TO_REGION.get(dept)


def parse_location(loc: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Retourne (dept_code, city, region_guess) avec heuristiques.
    Exemples:
      "59 - Mons-en-Barœul" => ("59", "Mons-en-Barœul", "Hauts-de-France")
      "Paris (75)" => ("75", "Paris", "Île-de-France")
      "Lyon - 69" => ("69", "Lyon", "Auvergne-Rhône-Alpes")
      "Remote" => (None, None, None)
    """
    if not loc:
        return None, None, None

    s = loc.strip()
    if not s:
        return None, None, None

    # Cas "XX - Ville"
    m = re.match(r"^\s*(\d{2}|2A|2B|\d{3})\s*[-–]\s*(.+?)\s*$", s, flags=re.IGNORECASE)
    if m:
        dept = normalize_dept_code(m.group(1))
        city = m.group(2).strip() or None
        return dept, city, dept_to_region(dept)

    # Cas "Ville - XX"
    m = re.match(r"^\s*(.+?)\s*[-–]\s*(\d{2}|2A|2B|\d{3})\s*$", s, flags=re.IGNORECASE)
    if m:
        city = m.group(1).strip() or None
        dept = normalize_dept_code(m.group(2))
        return dept, city, dept_to_region(dept)

    # Cas "Ville (XX)"
    m = re.match(r"^\s*(.+?)\s*\(\s*(\d{2}|2A|2B|\d{3})\s*\)\s*$", s, flags=re.IGNORECASE)
    if m:
        city = m.group(1).strip() or None
        dept = normalize_dept_code(m.group(2))
        return dept, city, dept_to_region(dept)

    # Cas "Département XX" / "Dept. 59" etc.
    m = re.search(r"\b(2A|2B|\d{2}|\d{3})\b", s.upper())
    dept = normalize_dept_code(m.group(1)) if m else None

    # City guess = tout ce qui n’est pas code
    city = None
    if dept:
        city_guess = re.sub(rf"\b{re.escape(dept)}\b", " ", s, flags=re.IGNORECASE)
        city_guess = re.sub(r"[-–(),]", " ", city_guess)
        city_guess = re.sub(r"\s+", " ", city_guess).strip()
        city = city_guess or None

    return dept, city, dept_to_region(dept)


def geocode_ban(rs: RobustSession, query: str, postcode: Optional[str] = None, limit: int = 1) -> Geo:
    # ✅ Correction 1: éviter q="" (sinon 400)
    if not (query or "").strip():
        return Geo()

    params = {"q": query.strip(), "limit": int(limit)}
    if postcode:
        params["postcode"] = postcode

    # ✅ Correction 2: ne PAS passer timeout ici, RobustSession le gère déjà
    r = rs.get(BAN_URL, params=params, headers=UA)
    r.raise_for_status()
    data = r.json()

    feats = data.get("features") or []
    if not feats:
        return Geo()

    f0 = feats[0]
    props = f0.get("properties") or {}
    geom = f0.get("geometry") or {}

    city = props.get("city") or props.get("municipality")
    pc = props.get("postcode")
    score = props.get("score")
    # dept: props can contain "context": "59, Nord, Hauts-de-France"
    dept_code = None
    region = None

    context = props.get("context")
    if isinstance(context, str):
        # "59, Nord, Hauts-de-France"
        parts = [p.strip() for p in context.split(",") if p.strip()]
        if parts:
            dept_code = normalize_dept_code(parts[0])
        if len(parts) >= 3:
            region = parts[2]

    coords = geom.get("coordinates") if isinstance(geom, dict) else None
    lon, lat = None, None
    if isinstance(coords, list) and len(coords) == 2:
        lon, lat = coords[0], coords[1]

    if not region:
        region = dept_to_region(dept_code)

    return Geo(
        city=city,
        postcode=pc,
        dept_code=dept_code,
        region=region,
        lat=float(lat) if lat is not None else None,
        lon=float(lon) if lon is not None else None,
        score=float(score) if score is not None else None,
        source="ban",
    )


def enrich_offers(db_path: str, sleep_s: float = 0.15, max_rows: Optional[int] = None) -> None:
    ensure_geo_columns(db_path)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # On ne traite que les lignes pas encore enrichies
    cur.execute(
        """
        SELECT uid, location, city, dept_code, region, lat, lon
        FROM offers
        WHERE (lat IS NULL OR lon IS NULL OR region IS NULL OR dept_code IS NULL)
        """
    )
    rows = cur.fetchall()
    total = len(rows)
    print(f"✅ Need geo enrichment: {total} offers")

    rs = RobustSession()
    done = 0

    for row in rows:
        uid = row["uid"]
        loc = row["location"]

        dept_guess, city_guess, region_guess = parse_location(loc)

        # ✅ Correction 3: fallback si query vide -> pas d’appel BAN
        query_txt = (city_guess or loc or "").strip()

        if not query_txt:
            final_city = city_guess
            final_dept = dept_guess
            final_region = dept_to_region(final_dept) or region_guess

            cur.execute(
                """
                UPDATE offers
                SET city=?,
                    postcode=COALESCE(postcode, NULL),
                    dept_code=?,
                    region=?,
                    geo_source=COALESCE(geo_source, 'heuristic'),
                    geo_score=COALESCE(geo_score, NULL)
                WHERE uid=?
                """,
                (final_city, final_dept, final_region, uid),
            )
        else:
            geo = geocode_ban(rs, query=query_txt, postcode=None, limit=1)

            # Combine heuristics + BAN
            final_city = geo.city or city_guess
            final_postcode = geo.postcode
            final_dept = geo.dept_code or dept_guess
            final_region = geo.region or dept_to_region(final_dept) or region_guess

            cur.execute(
                """
                UPDATE offers
                SET city=?,
                    postcode=?,
                    dept_code=?,
                    region=?,
                    lat=?,
                    lon=?,
                    geo_score=?,
                    geo_source=?
                WHERE uid=?
                """,
                (
                    final_city,
                    final_postcode,
                    final_dept,
                    final_region,
                    geo.lat,
                    geo.lon,
                    geo.score,
                    geo.source or "heuristic",
                    uid,
                ),
            )

        done += 1

        if done % 100 == 0:
            con.commit()
        if done % 500 == 0:
            print(f"… enriched {done}/{total}")

        if max_rows and done >= max_rows:
            break

        time.sleep(sleep_s)

    con.commit()
    con.close()
    print("✅ Done.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path vers offers.sqlite")
    ap.add_argument("--sleep_s", type=float, default=0.15)
    ap.add_argument("--max_rows", type=int, default=None, help="Limiter le nb de lignes enrichies (debug)")
    args = ap.parse_args()

    enrich_offers(args.db, sleep_s=args.sleep_s, max_rows=args.max_rows)


if __name__ == "__main__":
    main()
