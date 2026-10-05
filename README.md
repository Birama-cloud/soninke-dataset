# OpenSNK : jeu de données ouvert français-soninké

OpenSNK est le jeu de données du projet Sooninkanxanne. C'est un jeu de données libre pour faire entrer la langue soninké dans le numérique. Il réunit des phrases françaises et leur traduction en soninké, rassemblées, uniformisées et publiées pour que chacun puisse entraîner des outils de traduction ou des assistants.

*English summary: OpenSNK is an open French-Soninke parallel dataset (ISO 639-3: snk), built by native speakers for machine translation and language technology. Data under CC BY 4.0.*

## Pourquoi ce projet

Aucun outil numérique ne sait aujourd'hui traduire ou écrire en soninké, faute de textes pour l'apprendre aux machines. Ce projet rassemble ces textes : sources existantes réutilisables, et traductions produites par des locuteurs bénévoles.

## Contenu

Les chiffres à jour de la dernière version se trouvent dans [`release/STATS.md`](release/STATS.md).

| Fichier | Contenu |
|---|---|
| `release/soninke_fr_parallel.jsonl` | Toutes les paires de phrases français-soninké |
| `release/soninke_fr_parallel.csv` | Les mêmes paires, lisibles dans Excel |
| `release/soninke_fr_lexicon.jsonl` | Lexique français-soninké |

## Charger les données

Avec Python et pandas :

```python
import pandas as pd

url = "https://raw.githubusercontent.com/Birama-cloud/soninke-dataset/main/release/soninke_fr_parallel.jsonl"
df = pd.read_json(url, lines=True)

# Garder seulement les paires relues par un locuteur
valides = df[df["validation"] == "validée"]
```

Sans code : bouton vert **Code**, puis **Download ZIP**, et ouvrir `release/soninke_fr_parallel.csv` dans Excel.

## Format d'une paire

| Colonne | Description |
|---|---|
| `id` | Identifiant unique |
| `snk` | Phrase soninké dans l'orthographe uniformisée |
| `fr` | Traduction française |
| `snk_original` | Phrase soninké telle qu'elle a été écrite ou collectée |
| `source` | Source ou lot d'origine |
| `licence` | Licence de la source |
| `contributeur` | Nom ou pseudonyme du traducteur, pour les contributions |
| `variante` | Village ou région d'origine du traducteur, ou `inconnue` |
| `domaine` | Thème de la phrase |
| `origine` | `locuteur` (phrase écrite par une personne) ou `moteur` (phrase générée par un programme puis relue) |
| `validation` | `validée` (relue par un locuteur du projet) ou `non relue` |

## Orthographe

Le jeu de données vise l'alphabet officiel du soninké : pas d'accents, `ñ`, `ŋ`, `x`, voyelles longues doublées. Les règles sont décrites dans [`orthographe/regles_orthographe.md`](orthographe/regles_orthographe.md). Le texte d'origine est toujours conservé dans `snk_original`, ce qui permet d'appliquer une autre convention si besoin.

## Sources

| Source | Contenu | Licence |
|---|---|---|
| Contributions de locuteurs | Phrases du quotidien traduites par des bénévoles | CC BY 4.0 |
| [snk_engine](https://github.com/oscarmedra/snk_engine) | Phrases et verbes traduits | CC BY 4.0 |

L'inventaire complet des sources envisagées, avec leur statut, se trouve dans [`sources.csv`](sources.csv).

## Organisation du dépôt

```
connectors/       scripts de collecte, un par source
contributions/    lots de phrases traduits par les locuteurs
clean/            phrases extraites, au format commun
normalized/       phrases dans l'orthographe uniformisée
release/          fichiers publiés
orthographe/      règles d'écriture et mots de référence
scripts/          normalisation et assemblage de la version
lots_a_envoyer/   lots vides et guide pour les contributeurs
```

Pour reconstruire le jeu de données :

```bash
pip install openpyxl
python connectors/snk_engine.py
python connectors/contributions.py
python scripts/normalize.py
python scripts/build_release.py
```

## Contribuer

Vous parlez soninké ? Votre aide compte, quel que soit votre village. Il suffit de traduire un lot de 25 phrases, en 20 minutes environ. Le guide du contributeur est dans [`lots_a_envoyer/guide_contributeur.pdf`](lots_a_envoyer/guide_contributeur.pdf). Écrivez à l'adresse ci-dessous pour recevoir un lot.

## Limites connues

- Le jeu de données est encore petit. Il ne suffit pas, à ce stade, pour entraîner un traducteur fiable.
- Une partie des phrases de `snk_engine` est générée par un programme : elles sont justes, mais répétitives. La colonne `origine` permet de les filtrer.
- Les traductions des contributeurs ne sont pas toutes relues. La colonne `validation` l'indique.
- La convention d'orthographe est en cours de discussion avec des spécialistes de la langue.

## Citer

```
Birama TOGOLA et les contributeurs du projet Sooninkanxanne (2026).
OpenSNK : jeu de données ouvert français-soninké.
https://github.com/Birama-cloud/soninke-dataset
```

## Licence

Les données sont publiées sous licence [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.fr). Le code est publié sous licence MIT. Voir le fichier [`LICENSE`](LICENSE).

## Contact

Birama TOGOLA, data scientist et locuteur soninké, responsable du projet : togolabirama040@gmail.com
