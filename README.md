# EcoSort-Search

Application web d'aide au tri selectif. L'utilisateur tape le nom d'un produit,
l'app le recherche sur **Jumia** (scraping), puis une **IA (CNN)** analyse le
produit choisi et affiche la consigne de tri en colorant l'ecran a la couleur de
la bonne poubelle.

## Lancer le projet (evaluation)

```bash
docker build -t ecosort .
docker run -p 8501:8501 ecosort
```
ou
```bash
docker-compose up -d --build
```
Puis ouvrir http://localhost:8501

## Structure

```
projet-ecosort-search/
├── model/          # IA : entrainement + prediction
│   ├── train.py            # script d'entrainement (reproductible)
│   ├── predict.py          # predire_categorie() + mapping
│   └── modele_eco_sort.h5  # modele entraine (pousse sur le repo)
├── scraping/       # Scraping Jumia
│   └── jumia.py            # rechercher_produits()
├── app/            # Interface
│   └── main.py            # application Streamlit
├── dataset/        # Dataset Kaggle (IGNORE par git, local uniquement)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

## Categories de tri

| Classe modele            | Poubelle            | Couleur   |
| :----------------------- | :------------------ | :-------- |
| plastic, metal, cardboard| JAUNE               | `#FFD700` |
| glass                    | VERTE               | `#2E7D32` |
| paper                    | BLEUE               | `#1565C0` |
| trash                    | MARRON / NOIRE      | `#4E342E` |
| *(mots-cles sur le titre)* | D3E / ELECTRONIQUE| `#616161` |

Le D3E n'existe pas dans le dataset : detecte par mots-cles sur le titre du
produit (smartphone, ecouteur, chargeur, batterie, pile, montre...).

## Contrats d'interface (a respecter par tous)

```python
# scraping/jumia.py
def rechercher_produits(mot_cle: str) -> list[dict]:
    # -> [{"titre": str, "url_image": str, "lien": str}, ...]  (3 a 5 items)

# model/predict.py
def predire_categorie(image) -> dict:  # image = objet PIL
    # -> {"categorie": str, "couleur_hex": str, "classe_brute": str, "confiance": float}
```

## Equipe et roles

| Personne              | Role                 | Livrables                                    |
| :-------------------- | :------------------- | :------------------------------------------- |
| ATOUKOUVI Komi Denis  | IA + Frontend (Lead) | model/train.py, predict.py, .h5, app/main.py |
| ATEBA Aristide        | Scraping / Backend   | scraping/jumia.py                            |
| FOGAING Franck Noel   | DevOps / Integration | Dockerfile, docker-compose.yml, requirements |

## Workflow Git

- Branche par personne : `feature/ia-frontend`, `feature/scraping`, `feature/devops`
- **Zero push direct sur `main`** : tout passe par une Pull Request relue.
- Le dataset et les environnements virtuels ne sont jamais pousses (voir `.gitignore`).
