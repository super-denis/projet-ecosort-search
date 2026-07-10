"""
Interface Streamlit EcoSort-Search.
Responsable : Denis (Frontend)

Flux : mot-cle -> scraping Jumia -> choix produit -> prediction IA -> ecran colore.
Lancer : streamlit run app/main.py
"""

import sys, os
import requests
from io import BytesIO
from PIL import Image
import streamlit as st

# Permet d'importer les modules des autres dossiers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping.jumia import rechercher_produits
from model.predict import predire_categorie, est_d3e, categorie_d3e

st.set_page_config(page_title="EcoSort-Search", page_icon="♻️", layout="wide")


def colorer_ecran(couleur_hex: str):
    """Injecte du CSS pour colorer le fond de la page."""
    st.markdown(
        f"<style>.stApp {{ background-color: {couleur_hex}; }}</style>",
        unsafe_allow_html=True,
    )


def charger_image(url: str) -> Image.Image:
    r = requests.get(url, timeout=10)
    return Image.open(BytesIO(r.content))


st.title("♻️ EcoSort-Search")
st.write("Tape le nom d'un produit pour connaitre sa poubelle.")

mot_cle = st.text_input("Produit", placeholder="ex: bouteille d'eau, chargeur, journal...")

if st.button("Rechercher") and mot_cle:
    st.session_state["produits"] = rechercher_produits(mot_cle)

produits = st.session_state.get("produits", [])

if produits:
    st.subheader("Resultats")
    cols = st.columns(len(produits))
    for i, (col, p) in enumerate(zip(cols, produits)):
        with col:
            if p["url_image"]:
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
        image = charger_image(choix["url_image"])
        res = predire_categorie(image)

    colorer_ecran(res["couleur_hex"])
    st.markdown(f"## Poubelle : {res['categorie']}")
    st.write(f"Matiere detectee : {res['classe_brute']} "
             f"(confiance {res['confiance']:.0%})")
