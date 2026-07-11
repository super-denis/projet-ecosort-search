"""
Scraping Jumia CI : recherche de produits a partir d'un mot-cle.
Responsable : Aristide (ATEBA)

Expose la fonction du contrat :
    rechercher_produits(mot_cle) -> list[dict]
        chaque dict = {"titre": str, "url_image": str, "lien": str}
        renvoyer 3 a 5 produits.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    # Indispensable : sans User-Agent, Jumia bloque souvent la requete.
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0 Safari/537.36"),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def rechercher_produits(mot_cle: str, n: int = 5) -> list[dict]:
    """Renvoie jusqu'a n produits Jumia CI correspondant au mot-cle."""
    url = f"https://www.jumia.ci/catalog/?q={quote_plus(mot_cle)}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print("Erreur scraping :", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    produits = []
    for carte in soup.select("article.prd")[:n]:
        titre_el = carte.select_one("h3.name")
        img_el = carte.select_one("img.img")
        lien_el = carte.select_one("a.core")
        if not (titre_el and lien_el):
            continue

        produits.append({
            "titre": titre_el.get_text(strip=True),
            "url_image": (img_el.get("data-src") or img_el.get("src")) if img_el else "",
            "lien": "https://www.jumia.ci" + lien_el.get("href", ""),
        })

    return produits


if __name__ == "__main__":
    # Test rapide en ligne de commande
    for p in rechercher_produits("telephone"):
        print(p)