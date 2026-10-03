"""Connecteur snk_engine : étapes 2 (collecte) et 3 (extraction, nettoyage).

Source  : https://github.com/oscarmedra/snk_engine
Licence : CC BY 4.0 pour les données (citer l'auteur, voir sources.csv)

Usage, depuis la racine du projet :
    pip install openpyxl
    python connectors/snk_engine.py

Produit :
    raw/snk_engine/snk_engine-main.zip      archive brute, jamais modifiée
    clean/snk_engine_parallel.jsonl         paires soninké-français
    clean/snk_engine_lexicon.jsonl          verbes français-soninké
"""

import io
import json
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

SOURCE = "snk_engine"
URL = "https://github.com/oscarmedra/snk_engine/archive/refs/heads/main.zip"
LICENCE = "CC BY 4.0"

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / SOURCE
CLEAN = ROOT / "clean"
ARCHIVE = RAW / "snk_engine-main.zip"


def collect() -> None:
    """Étape 2 : télécharge l'archive une seule fois et note la date."""
    RAW.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists():
        print(f"Archive déjà présente : {ARCHIVE}")
        return
    print(f"Téléchargement de {URL}")
    urllib.request.urlretrieve(URL, ARCHIVE)
    (RAW / "COLLECTE.txt").write_text(
        f"source: {URL}\ndate: {date.today().isoformat()}\nlicence: {LICENCE}\n",
        encoding="utf-8",
    )


def clean_text(text) -> str:
    """Retire les espaces en trop sans toucher à l'orthographe."""
    return " ".join(str(text or "").split())


def extract_parallel(archive: zipfile.ZipFile) -> list[dict]:
    """Étape 3 : lit corpus/valide/*.jsonl et met chaque paire au format commun."""
    rows, seen = [], set()
    names = sorted(n for n in archive.namelist()
                   if "/corpus/valide/" in n and n.endswith(".jsonl"))
    for name in names:
        stem = Path(name).stem
        for line in archive.read(name).decode("utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            # snk_saisie est la phrase telle que le locuteur l'a écrite.
            snk = clean_text(item.get("snk_saisie") or item.get("snk"))
            fr = clean_text(item.get("fr"))
            if not snk or not fr:
                continue
            key = (snk.lower(), fr.lower())
            if key in seen:  # doublon exact
                continue
            seen.add(key)
            rows.append({
                "id": f"{SOURCE}-{stem}-{item['id']}",
                "snk": None,  # rempli à l'étape 4 (normalisation)
                "snk_original": snk,
                "fr": fr,
                "source": f"{SOURCE}/{stem}",
                "licence": LICENCE,
                "variante": "inconnue",
                "domaine": "quotidien" if stem.startswith("texte_") else "grammaire",
                # « moteur » : phrase générée par un programme puis relue.
                # « locuteur » : phrase écrite directement par un locuteur.
                "origine": item.get("origine") or "locuteur",
                "validation": "non relue",
            })
    return rows


def extract_lexicon(archive: zipfile.ZipFile) -> list[dict]:
    """Étape 3 : lit le tableau des verbes et garde ceux qui ont une traduction."""
    import openpyxl

    name = next(n for n in archive.namelist()
                if n.endswith("data/sources/verbes_francais_soninke.xlsx"))
    sheet = openpyxl.load_workbook(io.BytesIO(archive.read(name)), read_only=True)["Verbes"]
    rows = []
    for num, fr, _groupe, _priorite, snk in sheet.iter_rows(min_row=2, values_only=True):
        fr, snk = clean_text(fr), clean_text(snk)
        if not fr or not snk:
            continue
        rows.append({
            "id": f"{SOURCE}-verbe-{num}",
            "snk": None,
            "snk_original": snk,
            "fr": fr,
            "categorie": "verbe",
            "source": f"{SOURCE}/verbes_francais_soninke",
            "licence": LICENCE,
            "variante": "inconnue",
            "validation": "non relue",
        })
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{len(rows):>5} lignes -> {path.relative_to(ROOT)}")


def main() -> None:
    collect()
    with zipfile.ZipFile(ARCHIVE) as archive:
        write_jsonl(CLEAN / "snk_engine_parallel.jsonl", extract_parallel(archive))
        write_jsonl(CLEAN / "snk_engine_lexicon.jsonl", extract_lexicon(archive))


if __name__ == "__main__":
    main()
