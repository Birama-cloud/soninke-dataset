"""Connecteur des contributions : transforme les lots traduits en paires.

Usage, depuis la racine du projet :
    python connectors/contributions.py

Deux formats de lots dans le dossier contributions/ :
  - lot_*.txt   lots traduits par le responsable du projet (lignes « fr: » / « snk: ») ;
  - lot_*.xlsx  lots traduits par des contributeurs (nom, parler et accord dans le fichier).

Produit : clean/contributions_parallel.jsonl
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOTS = ROOT / "contributions"
OUT = ROOT / "clean" / "contributions_parallel.jsonl"

# Pour les lots .txt : à renseigner une fois.
CONTRIBUTEUR = "Birama"
VARIANTE = "Gadiaga"   # ton parler, par exemple « Gadiaga », « Guidimakha »
LICENCE = "CC BY 4.0"


def clean_text(value) -> str:
    return " ".join(str(value or "").split())


def make_row(lot: str, number: int, count: int, fr: str, snk: str,
             contributor: str, variant: str) -> dict:
    return {
        "id": f"contrib-{lot}-{number:03d}-{count}",
        "snk": None,  # rempli à l'étape 4 (normalisation)
        "snk_original": snk,
        "fr": fr,
        "source": f"contributions/{lot}",
        "licence": LICENCE,
        "contributeur": contributor,
        "variante": variant,
        "domaine": "quotidien",
        "origine": "locuteur",
        "validation": "validée" if contributor == CONTRIBUTEUR else "non relue",
    }


def read_txt(path: Path) -> tuple[list[dict], int]:
    """Renvoie les paires d'un lot .txt et le nombre de phrases encore à traduire."""
    rows, todo, fr, number, count = [], 0, None, 0, 0
    for line in path.read_text(encoding="utf-8").splitlines() + ["fr:"]:
        line = line.strip()
        if line.startswith("fr:"):
            if fr and count == 0:
                todo += 1
            fr, number, count = clean_text(line[3:]), number + 1, 0
        elif line.startswith("snk:") and fr:
            snk = clean_text(line[4:])
            if snk:
                count += 1
                rows.append(make_row(path.stem, number, count, fr, snk, CONTRIBUTEUR, VARIANTE))
    return rows, todo


def read_xlsx(path: Path) -> tuple[list[dict], int]:
    """Renvoie les paires d'un lot .xlsx rempli par un contributeur."""
    import openpyxl

    sheet = openpyxl.load_workbook(path, data_only=True).active
    contributor = clean_text(sheet["C3"].value) or "anonyme"
    variant = clean_text(sheet["C4"].value) or "inconnue"
    if not clean_text(sheet["C5"].value).lower().startswith("oui"):
        print(f"  ! {path.name} ignoré : l'accord de publication n'est pas « OUI »")
        return [], 0
    rows, todo = [], 0
    for number, fr, snk in sheet.iter_rows(min_row=10, max_col=3, values_only=True):
        fr, snk = clean_text(fr), clean_text(snk)
        if not fr or not isinstance(number, (int, float)):  # saute la ligne « Exemple »
            continue
        if snk:
            rows.append(make_row(path.stem, int(number), 1, fr, snk, contributor, variant))
        else:
            todo += 1
    return rows, todo


def main() -> None:
    rows, todo = [], 0
    readers = {".txt": read_txt, ".xlsx": read_xlsx}
    for path in sorted(LOTS.glob("lot_*")):
        if path.suffix not in readers or path.name.startswith("~$"):
            continue
        lot_rows, lot_todo = readers[path.suffix](path)
        print(f"{path.name}: {len(lot_rows)} traductions, {lot_todo} phrases à traduire")
        rows += lot_rows
        todo += lot_todo
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Total : {len(rows)} paires -> {OUT.relative_to(ROOT)} ({todo} phrases en attente)")


if __name__ == "__main__":
    main()
