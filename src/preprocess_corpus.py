from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path
from typing import List

import pandas as pd


# Stopwords FR+EN (léger, suffisant pour ton projet)
STOPWORDS_FR = {
    "alors","au","aucuns","aussi","autre","avant","avec","avoir","bon","car","ce","cela","ces","ceux","chaque","ci",
    "comme","comment","dans","des","du","dedans","dehors","depuis","devrait","doit","donc","dos","début","elle","elles",
    "en","encore","essai","est","et","eu","fait","faites","fois","font","force","haut","hors","ici","il","ils","je",
    "juste","la","le","les","leur","là","ma","maintenant","mais","mes","mine","moins","mon","mot","même","ni","nommés",
    "notre","nous","nouveaux","ou","où","par","parce","parole","pas","personnes","peut","peu","pièce","plupart","pour",
    "pourquoi","quand","que","quel","quelle","quelles","quels","qui","sa","sans","ses","seulement","si","sien","son",
    "sont","sous","soyez","sur","ta","tandis","tellement","tels","tes","ton","tous","tout","trop","très","tu","valeur",
    "voie","voient","vont","votre","vous","vu","ça","étaient","état","étions","été","être"
}

STOPWORDS_EN = {
    "a","about","above","after","again","against","all","am","an","and","any","are","as","at","be","because","been",
    "before","being","below","between","both","but","by","could","did","do","does","doing","down","during","each",
    "few","for","from","further","had","has","have","having","he","her","here","hers","herself","him","himself","his",
    "how","i","if","in","into","is","it","its","itself","just","me","more","most","my","myself","no","nor","not",
    "now","of","off","on","once","only","or","other","our","ours","ourselves","out","over","own","s","same","she",
    "should","so","some","such","t","than","that","the","their","theirs","them","themselves","then","there","these",
    "they","this","those","through","to","too","under","until","up","very","was","we","were","what","when","where",
    "which","while","who","whom","why","will","with","you","your","yours","yourself","yourselves"
}

STOPWORDS = STOPWORDS_FR | STOPWORDS_EN


def normalize_text(s: str) -> str:
    s = s or ""
    # minuscules + accents
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))

    # URLs / mails / chiffres
    s = re.sub(r"http\S+|www\.\S+", " ", s)
    s = re.sub(r"\S+@\S+\.\S+", " ", s)
    s = re.sub(r"\d+", " ", s)

    # ponctuation -> espaces
    s = re.sub(r"[^a-z\s\-\+/#]", " ", s)  # garde un peu de symboles utiles
    s = re.sub(r"[\-_/#+]", " ", s)

    # espaces multiples
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(s: str) -> List[str]:
    toks = s.split()
    # enlever stopwords + tokens trop courts
    toks = [t for t in toks if len(t) >= 2 and t not in STOPWORDS]
    return toks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--text_col", default="raw_text")
    ap.add_argument("--min_tokens", type=int, default=5)
    ap.add_argument("--max_tokens", type=int, default=2000)
    args = ap.parse_args()

    in_csv = Path(args.in_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_csv, encoding="utf-8", low_memory=False)

    if args.text_col not in df.columns:
        raise RuntimeError(f"Colonne texte introuvable: {args.text_col}. Colonnes: {list(df.columns)}")

    texts = df[args.text_col].fillna("").astype(str)

    clean_texts = []
    token_counts = []

    for s in texts:
        s2 = normalize_text(s)
        toks = tokenize(s2)
        # filtre longueur
        if len(toks) < args.min_tokens:
            clean_texts.append("")
            token_counts.append(0)
            continue
        if len(toks) > args.max_tokens:
            toks = toks[: args.max_tokens]
        clean_texts.append(" ".join(toks))
        token_counts.append(len(toks))

    df["clean_text"] = clean_texts
    df["n_tokens"] = token_counts

    # supprime les lignes vides après nettoyage
    df2 = df[df["n_tokens"] > 0].copy()

    out_csv = out_dir / "corpus_clean.csv"
    df2.to_csv(out_csv, index=False, encoding="utf-8")

    print(f"✅ Input: {len(df)} docs")
    print(f"✅ Output: {len(df2)} docs (after cleaning)")
    print(f"✅ Saved: {out_csv}")


if __name__ == "__main__":
    main()
