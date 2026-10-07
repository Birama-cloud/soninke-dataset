"""Étape 4 : normalisation orthographique.

Usage, depuis la racine du projet :
    python scripts/normalize.py

Lit    clean/*.jsonl
Écrit  normalized/*.jsonl (colonne « snk » remplie, « snk_original » intacte)
       orthographe/variantes_a_trancher.txt (mots écrits de plusieurs façons)

Deux niveaux de règles :
  1. règles automatiques, sûres, définies dans ce fichier ;
  2. mots de référence validés par un locuteur, dans orthographe/mots_reference.txt.
"""

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "clean"
OUT = ROOT / "normalized"
REFERENCE = ROOT / "orthographe" / "mots_reference.txt"
REPORT = ROOT / "orthographe" / "variantes_a_trancher.txt"
DISTINCT = ROOT / "orthographe" / "mots_distincts.txt"

# Règle 1 : pas d'accents. ñ et ŋ ne sont pas touchés.
ACCENTS = str.maketrans(
    "áàâäéèêëíìîïóòôöúùûüÁÀÂÄÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜ",
    "aaaaeeeeiiiioooouuuuAAAAEEEEIIIIOOOOUUUU",
)
# Le Mali écrit ɲ, le Sénégal ñ : on garde ñ partout.
LETTERS = str.maketrans({"ɲ": "ñ", "Ɲ": "Ñ", "’": "'", "‘": "'"})

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def automatic(text: str) -> str:
    """Règles sûres, appliquées sans intervention humaine."""
    text = unicodedata.normalize("NFC", text).translate(LETTERS).translate(ACCENTS)
    text = re.sub(r"\b([nNmM])'(?=\w)", r"\1 ", text)   # n'toxo -> n toxo
    text = re.sub(r"([gG])u(?=[eiEI])", r"\1", text)     # guiri -> giri
    text = re.sub(r"ss", "s", text)                      # xalissi -> xalisi
    text = re.sub(r"gn", "ñ", text)                      # gnime -> ñime
    text = re.sub(r"dj", "j", text)                      # dji -> ji
    text = re.sub(r"tch", "c", text)                     # tuntchi -> tunci
    text = re.sub(r"\b(?!ou\b)(\w*?)ou", r"\1u", text)   # okou -> oku
    return " ".join(text.split())


def load_reference() -> dict[str, str]:
    """Lit « écrit -> normalisé ». Les lignes finissant par « ? » sont ignorées."""
    reference = {}
    if not REFERENCE.exists():
        return reference
    for line in REFERENCE.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if "->" not in line or line.endswith("?"):
            continue
        written, normal = (part.strip() for part in line.split("->", 1))
        if written and normal:
            reference[written.lower()] = normal
    return reference


def load_distinct() -> set[str]:
    """Mots qui se ressemblent mais sont vraiment différents : à ne pas signaler."""
    words = set()
    if DISTINCT.exists():
        for line in DISTINCT.read_text(encoding="utf-8").splitlines():
            words.update(line.split("#")[0].lower().split())
    return words


def apply_reference(text: str, reference: dict[str, str]) -> str:
    def swap(match: re.Match) -> str:
        word = match.group(0)
        normal = reference.get(word.lower())
        if normal is None:
            return word
        # Garde la majuscule du mot d'origine.
        return normal[0].upper() + normal[1:] if word[0].isupper() else normal
    return WORD.sub(swap, text)


def finish_sentence(text: str) -> str:
    """Majuscule au début, ponctuation à la fin."""
    if not text:
        return text
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".?!…" else text + "."


def skeleton(word: str) -> str:
    """Forme réduite, sans voyelles doubles. Sert à repérer les variantes."""
    return re.sub(r"([aeiou])\1+", r"\1", word.lower())


def main() -> None:
    reference = load_reference()
    print(f"{len(reference)} mots de référence validés")
    OUT.mkdir(exist_ok=True)
    forms = defaultdict(Counter)

    for path in sorted(CLEAN.glob("*.jsonl")):
        is_sentence = "lexicon" not in path.name
        rows = [json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in rows:
            snk = apply_reference(automatic(row["snk_original"]), reference)
            row["snk"] = finish_sentence(snk) if is_sentence else snk
            for word in WORD.findall(row["snk"]):
                forms[skeleton(word)][word.lower()] += 1
        with (OUT / path.name).open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{len(rows):>5} lignes -> normalized/{path.name}")

    distinct = load_distinct()
    variants = {k: v for k, v in forms.items()
                if len(v) > 1 and not set(v) <= distinct}
    lines = ["# Mots écrits de plusieurs façons (nombre d'occurrences entre parenthèses).",
             "# Choisis une forme et ajoute la ligne dans mots_reference.txt.", ""]
    for _, counter in sorted(variants.items(), key=lambda kv: -sum(kv[1].values())):
        lines.append("  ".join(f"{w} ({n})" for w, n in counter.most_common()))
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(variants)} mots à trancher -> orthographe/variantes_a_trancher.txt")


if __name__ == "__main__":
    main()
