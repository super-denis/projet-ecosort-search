"""
Interface Streamlit EcoSort-Search.
Responsable : Denis (Frontend)

Flux : mot-cle -> scraping Jumia -> choix produit -> prediction IA -> ecran colore.

Un MODE DEMO (case a cocher dans la barre laterale) permet de tester toute
l'interface SANS Jumia : de faux produits piochent de vraies images dans
dataset/, donc le modele predit pour de vrai. Pratique tant que le scraping
n'est pas pret.

Lancer : streamlit run app/main.py
"""

import os
import sys
import glob
import random
import requests
from io import BytesIO
from PIL import Image
import streamlit as st

# Permet d'importer les modules des autres dossiers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping.jumia import rechercher_produits
from model.predict import predire_categorie, est_d3e, categorie_d3e

st.set_page_config(page_title="EcoSort-Search", page_icon="♻️", layout="wide")


# ---------- Utilitaires ----------
def colorer_ecran(couleur_hex: str):
    """Injecte du CSS pour colorer le fond de la page."""
    st.markdown(
        f"<style>.stApp {{ background-color: {couleur_hex}; }}</style>",
        unsafe_allow_html=True,
    )


def charger_image_url(url: str) -> Image.Image:
    r = requests.get(url, timeout=10)
    return Image.open(BytesIO(r.content))


# ---------- Mode demo ----------
# (titre affiche, classe du dataset ou piocher une image ; None = cas D3E par titre)
DEMO_SPECS = [
    ("Bouteille d'eau 1.5L en plastique", "plastic"),
    ("Journal quotidien du matin", "paper"),
    ("Bocal en verre pour confiture", "glass"),
    ("Canette de soda", "metal"),
    ("Chargeur USB pour smartphone", None),  # -> D3E via mot-cle du titre
]


def _sample_image(classe: str):
    files = glob.glob(os.path.join("dataset", classe, "*"))
    if not files:
        return None
    return Image.open(random.choice(files)).convert("RGB")


def produits_demo():
    prods = []
    for titre, classe in DEMO_SPECS:
        img = _sample_image(classe or "metal")  # image quelconque pour le cas D3E
        if img is not None:
            prods.append({"titre": titre, "image": img, "lien": None})
    return prods


# ---------- Interface ----------
st.title("♻️ EcoSort-Search")
st.write("Tape le nom d'un produit pour connaitre sa poubelle.")

mode_demo = st.sidebar.checkbox("Mode demo (sans Jumia)", value=True)
st.sidebar.caption(
    "En mode demo, de faux produits utilisent des images du dataset pour "
    "tester le modele et l'affichage sans dependre du scraping."
)

if mode_demo:
    if st.button("Charger des produits de demonstration"):
        st.session_state["produits"] = produits_demo()
        st.session_state.pop("choix", None)
else:
    mot_cle = st.text_input("Produit", placeholder="ex: bouteille d'eau, chargeur, journal...")
    if st.button("Rechercher") and mot_cle:
        st.session_state["produits"] = rechercher_produits(mot_cle)
        st.session_state.pop("choix", None)

produits = st.session_state.get("produits", [])

if produits:
    st.subheader("Resultats")
    cols = st.columns(len(produits))
    for i, (col, p) in enumerate(zip(cols, produits)):
        with col:
            if p.get("image") is not None:
                st.image(p["image"], use_column_width=True)
            elif p.get("url_image"):
                st.image(p["url_image"], use_column_width=True)
            st.caption(p["titre"])
            if st.button("Choisir", key=f"choix_{i}"):
                st.session_state["choix"] = p

choix = st.session_state.get("choix")
if choix:
    st.divider()
    st.write(f"**Produit choisi :** {choix['titre']}")

    # 1) D3E d'abord (mots-cles sur le titre)
    if est_d3e(choix["titre"]):
        res = categorie_d3e()
    else:
        # 2) sinon on classe l'image via le modele
        if choix.get("image") is not None:
            image = choix["image"]
        else:
            image = charger_image_url(choix["url_image"])
        res = predire_categorie(image)

    colorer_ecran(res["couleur_hex"])
    st.markdown(f"## Poubelle : {res['categorie']}")
    st.write(f"Matiere detectee : {res['classe_brute']} "
             f"(confiance {res['confiance']:.0%})")
