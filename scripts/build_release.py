"""Étape 7 : assemblage de la version publiable.

Usage, depuis la racine du projet :
    python scripts/build_release.py

Lit    normalized/*.jsonl
Écrit  release/soninke_fr_parallel.jsonl   toutes les paires, un seul fichier
       release/soninke_fr_parallel.csv     les mêmes paires, lisibles dans Excel
       release/soninke_fr_lexicon.jsonl    le lexique
       release/STATS.md                    les chiffres de la version
"""

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

VERSION = "0.1.0"   # à augmenter à chaque publication : 0.1.0, 0.2.0, ...

ROOT = Path(__file__).resolve().parent.parent
NORMALIZED = ROOT / "normalized"
RELEASE = ROOT / "release"

COLUMNS = ["id", "snk", "fr", "snk_original", "source", "licence",
           "contributeur", "variante", "domaine", "origine", "validation"]


def load(pattern: str) -> list[dict]:
    """Charge tous les fichiers qui correspondent au motif, sans doublon exact."""
    rows, seen = [], set()
    for path in sorted(NORMALIZED.glob(pattern)):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = (str(row.get("snk", "")).lower(), str(row.get("fr", "")).lower())
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    # utf-8-sig : pour qu'Excel affiche correctement ñ, ŋ et les accents.
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def table(title: str, counter: Counter) -> list[str]:
    lines = [f"## {title}", "", "| Valeur | Paires |", "|---|---|"]
    lines += [f"| {key} | {count} |" for key, count in counter.most_common()]
    return lines + [""]


def main() -> None:
    parallel = load("*_parallel.jsonl")
    lexicon = load("*_lexicon.jsonl")
    RELEASE.mkdir(exist_ok=True)
    write_jsonl(RELEASE / "soninke_fr_parallel.jsonl", parallel)
    write_csv(RELEASE / "soninke_fr_parallel.csv", parallel)
    write_jsonl(RELEASE / "soninke_fr_lexicon.jsonl", lexicon)

    stats = [f"# Statistiques de la version {VERSION}", "",
             f"Générée le {date.today().isoformat()}.", "",
             f"- Paires français-soninké : **{len(parallel)}**",
             f"- Entrées du lexique : **{len(lexicon)}**", ""]
    stats += table("Par source", Counter(r["source"].split("/")[0] for r in parallel))
    stats += table("Par niveau de validation", Counter(r.get("validation", "?") for r in parallel))
    stats += table("Par origine", Counter(r.get("origine", "?") for r in parallel))
    stats += table("Par variante", Counter(r.get("variante", "?") for r in parallel))
    (RELEASE / "STATS.md").write_text("\n".join(stats), encoding="utf-8")

    print(f"Version {VERSION}")
    print(f"{len(parallel):>5} paires  -> release/soninke_fr_parallel.jsonl et .csv")
    print(f"{len(lexicon):>5} entrées -> release/soninke_fr_lexicon.jsonl")
    print("Statistiques -> release/STATS.md")


if __name__ == "__main__":
    main()
