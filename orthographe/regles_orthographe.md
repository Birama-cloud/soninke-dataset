# Convention d'orthographe du dataset

Cible : l'alphabet officiel du soninké (Sénégal), sans accents, avec ñ, ŋ et x.
Le texte d'origine est toujours conservé dans la colonne `snk_original`.

## Règles automatiques (scripts/normalize.py)

| N° | Règle | Exemple |
|---|---|---|
| 1 | Pas d'accents sur les voyelles | télé -> tele |
| 2 | g au lieu de gu devant e, i | guiri -> giri |
| 3 | s simple | xalissi -> xalisi |
| 4 | ñ au lieu de gn (et de ɲ) | gnimé -> ñime |
| 5 | j au lieu de dj, c au lieu de tch, u au lieu de ou | dji -> ji |
| 6 | n' et m' en début de mot s'écrivent séparés | n'toxo -> n toxo |
| 7 | Majuscule en début de phrase, ponctuation à la fin | |

## Règles par mot (orthographe/mots_reference.txt)

Un script ne peut pas deviner : le son ñ écrit « ni », le son ŋ écrit « ng »,
le son j écrit « di », la longueur des voyelles, la coupure des mots.
Ces cas se règlent mot par mot, validés par un locuteur.

## Points encore ouverts

- `m'paba` devient pour l'instant `m paba`. À comparer avec l'usage d'Asawan.
- Le « n » de liaison (`jii n'ki`, `xalissi n'ti`) : rattaché à quel mot ?
- Coupure des mots : `anmoxo` ou `an moxo`, `kotasu` ou `koota su`.
