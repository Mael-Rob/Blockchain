# Blockchain de possession d'œuvres numériques

## Équipe

Ce projet a été réalisé dans le cadre du module `<Blockchain>` par :

- `<Maël ROBERTO>`
- `<Baptiste BEAUDEL>`
- `<Adrien ROUSSELLE>`
- `<Victor PIROTH>`

## Description du sujet

L’objectif du projet est de modéliser et d’implémenter une **blockchain de possession d’œuvres numériques** (images, films, musiques, etc.).

L’idée de départ est la suivante :
- une œuvre numérique est **facilement copiable**, donc on ne peut pas contrôler techniquement la duplication du fichier ;
- en revanche, on peut définir et enregistrer sur une blockchain **qui est le “propriétaire officiel”** de chaque œuvre, à un instant donné ;
- la blockchain sert alors de **registre de référence** pour la possession : elle garde l’historique des créations et des transferts de propriété.

Concrètement, nous voulions :
- modéliser la notion de **possession d’une œuvre** dans un système où les fichiers restent copiables ;
- définir un ensemble de **règles précises** (création d’œuvre, transfert de propriété, validation des transactions) ;
- implémenter en Python un **prototype de blockchain** permettant de :
  - créer des œuvres,
  - les transférer entre utilisateurs,
  - retrouver à tout moment le propriétaire officiel d’une œuvre et l'origine de l'oeuvre.

## Ce que nous voulions réaliser

Au début du projet, notre cahier des charges était de :

1. **Aspect conceptuel**
   - Clarifier ce que signifie “posséder une œuvre numérique” dans notre système :
     - différencier la copie du fichier et la possession officielle ;
     - définir la possession comme un **statut inscrit dans la blockchain** (adresse propriétaire).
   - Identifier les **enjeux** :
     - rareté symbolique vs copie technique,
     - rôle de la blockchain comme registre de référence,
     - liens possibles avec les droits d’auteur et la rémunération.

2. **Aspect technique**
   - Concevoir une petite blockchain en Python avec :
     - une structure `Block` (index, précédent hash, liste de transactions, etc.) ;
     - des transactions typées (`CREATE`, `TRANSFER`) ;
     - une logique de validation et de vérification que c'est le bon propriétaire avec des signatures
   - Mettre en place un **état global** permettant de savoir, pour chaque oeuvre, qui en est le propriétaire officiel.
   - Ajouter des fonctionnalités supplémentaires :
     - par exemple des “royalties” à l’artiste lors d’un transfert mais il faudrait changer la structure de la blockchain car pour le moment on gère uniquement le propriétaire
     - ou une interface simple en ligne de commande.

