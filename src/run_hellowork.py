import argparse
from hellowork_html import scrape_hellowork


DEFAULT_KEYWORDS = [
    # métiers data
    "data scientist",
    "data analyst",
    "data engineer",
    "data architect",
    "business intelligence",
    "bi developer",
    "analyste décisionnel",
    "statisticien",
    "statistician",
    "quant",
    # IA / ML
    "machine learning",
    "machine learning engineer",
    "ml engineer",
    "deep learning",
    "computer vision",
    "nlp",
    "ingénieur ia",
    "ingenieur ia",
    "ai engineer",
]


def main():
    parser = argparse.ArgumentParser(description="Scrape HelloWork jobs and save raw offers (HTML).")

    parser.add_argument(
        "--keywords",
        nargs="+",
        default=DEFAULT_KEYWORDS,
        help="Liste de métiers/mots-clés. Si non fourni, utilise la liste par défaut (data/IA).",
    )

    parser.add_argument("--city", type=str, default=None, help="Ville (ex: Paris). Optionnel.")
    parser.add_argument("--postal", type=str, default=None, help="Code postal (ex: 75000). Optionnel.")
    parser.add_argument("--all_france", action="store_true", help="Ignore city/postal et scrape France entière.")

    parser.add_argument("--mode", type=str, default="emploi", choices=["emploi", "stage", "alternance"])
    parser.add_argument("--max_pages", type=int, default=30)
    parser.add_argument("--max_urls", type=int, default=2000)
    parser.add_argument("--sleep_s", type=float, default=0.3)
    parser.add_argument("--out_dir", type=str, default="../data")

    args = parser.parse_args()

    if args.all_france:
        args.city = None
        args.postal = None

    res = scrape_hellowork(
        keywords=args.keywords,
        city=args.city,
        postal=args.postal,
        mode=args.mode,
        max_pages=args.max_pages,
        max_urls=args.max_urls,
        sleep_s=args.sleep_s,
        out_dir=args.out_dir,
    )

    print("Done:", res)


if __name__ == "__main__":
    main()
