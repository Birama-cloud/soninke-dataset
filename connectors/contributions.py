"""Connecteur des contributions : transforme contributions/lot_*.txt en paires.

Usage, depuis la racine du projet :
    python connectors/contributions.py

Format d'un lot :
    fr: phrase française
    snk: traduction soninké
    snk: autre traduction possible (facultatif)

Produit : clean/contributions_parallel.jsonl
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOTS = ROOT / "contributions"
OUT = ROOT / "clean" / "contributions_parallel.jsonl"

# À renseigner une fois : ton parler (par exemple « Gadiaga », « Guidimakha »).
VARIANTE = "GADIAGA"
LICENCE = "CC BY 4.0"


def read_lot(path: Path) -> tuple[list[dict], int]:
    """Renvoie les paires d'un lot et le nombre de phrases encore à traduire."""
    rows, todo, fr, number, count = [], 0, None, 0, 0

    def close():
        nonlocal todo
        if fr is not None and count == 0:
            todo += 1

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("fr:"):
            close()
            fr, number, count = " ".join(line[3:].split()), number + 1, 0
        elif line.startswith("snk:") and fr:
            snk = " ".join(line[4:].split())
            if not snk:
                continue
            count += 1
            rows.append({
                "id": f"contrib-{path.stem}-{number:03d}-{count}",
                "snk": None,  # rempli à l'étape 4 (normalisation)
                "snk_original": snk,
                "fr": fr,
                "source": f"contributions/{path.stem}",
                "licence": LICENCE,
                "variante": VARIANTE,
                "domaine": "quotidien",
                "origine": "locuteur",
                "validation": "validée",
            })
    close()
    return rows, todo


def main() -> None:
    rows, todo = [], 0
    for path in sorted(LOTS.glob("lot_*.txt")):
        lot_rows, lot_todo = read_lot(path)
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
