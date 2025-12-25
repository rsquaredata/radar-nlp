from pathlib import Path

APP_TITLE = "Job Market Explorer"
DB_PATH = Path("../data/offers.sqlite")   # ajuste si besoin
DEFAULT_TABLE = "offers_enriched"         # view créée avant
MAX_ROWS_TABLE = 5000                    # pour éviter de charger 18k dans un tableau sans filtre
