"""
Interface Streamlit EcoSort-Search.
Responsable : Denis (Frontend)

Flux : mot-cle -> scraping Jumia CI -> clic sur un produit -> prediction IA -> ecran colore.
Navigation (Accueil / Categories / Conseils / A propos) et etat de recherche portes par l'URL.

Lancer : streamlit run app/main.py
"""

import os
import sys
import requests
from io import BytesIO
from urllib.parse import quote
from PIL import Image
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping.jumia import rechercher_produits
from model.predict import predire_categorie, est_d3e, categorie_d3e

st.set_page_config(page_title="EcoSort-Search", page_icon="♻️", layout="wide")

STYLE = {
    "JAUNE": {"fg": "#3A2E00", "icon": "🟡", "color": "#F4C20D", "sub": "Emballages & plastiques",
              "card": "linear-gradient(150deg,#F7CE3E,#C99000)", "title": "Poubelle JAUNE",
              "consigne": "Emballages recyclables : plastique, métal, carton.",
              "detail": "Cet emballage est recyclable. Déposez-le dans le bac jaune avec les plastiques, métaux et cartons.",
              "tip": "Pensez à vider et aplatir vos emballages avant de les jeter pour faciliter le recyclage."},
    "VERTE": {"fg": "#FFFFFF", "icon": "🟢", "color": "#2E9E52", "sub": "Verre",
              "card": "linear-gradient(150deg,#37B45F,#1B5E20)", "title": "Poubelle VERTE",
              "consigne": "Verre uniquement : bouteilles et bocaux.",
              "detail": "C'est du verre d'emballage. Déposez-le dans le bac vert, sans bouchon ni couvercle.",
              "tip": "La vaisselle et les vitres cassées ne vont PAS avec le verre d'emballage."},
    "BLEUE": {"fg": "#FFFFFF", "icon": "🔵", "color": "#2196F3", "sub": "Papiers",
              "card": "linear-gradient(150deg,#3AA0F5,#0D47A1)", "title": "Poubelle BLEUE",
              "consigne": "Papiers, journaux et magazines.",
              "detail": "C'est du papier. Déposez-le dans le bac bleu, propre et sec.",
              "tip": "Retirez les films plastiques et agrafes avant de jeter vos papiers."},
    "MARRON / NOIRE": {"fg": "#FFFFFF", "icon": "⚫", "color": "#6D4C41", "sub": "Résiduels",
                       "card": "linear-gradient(150deg,#7A5548,#3E2723)", "title": "Poubelle MARRON",
                       "consigne": "Déchets non recyclables.",
                       "detail": "Ce déchet n'est pas recyclable : direction le bac marron / noir des ordures résiduelles.",
                       "tip": "Compostez ce qui peut l'être pour réduire ce type de déchets."},
    "D3E / ELECTRONIQUE": {"fg": "#FFFFFF", "icon": "🔌", "color": "#78909C", "sub": "Électroniques",
                           "card": "linear-gradient(150deg,#8A9BA5,#37474F)", "title": "Bac D3E",
                           "consigne": "Appareils électriques et électroniques.",
                           "detail": "C'est un appareil électronique. Ne le jetez jamais à la poubelle : rapportez-le en point de collecte D3E.",
                           "tip": "Piles, chargeurs et téléphones se recyclent en magasin ou en déchetterie."},
}
ORDER = ["JAUNE", "VERTE", "BLEUE", "D3E / ELECTRONIQUE", "MARRON / NOIRE"]
SHORT = {"JAUNE": "Jaune", "VERTE": "Verte", "BLEUE": "Bleue",
         "D3E / ELECTRONIQUE": "Grise", "MARRON / NOIRE": "Marron"}
CLASSE_LABEL = {"plastic": "Plastique (PET)", "metal": "Métal", "cardboard": "Carton",
                "glass": "Verre", "paper": "Papier", "trash": "Déchet résiduel",
                "electronique": "Appareil électronique"}
DEFAULT = {"grad": "linear-gradient(-45deg,#05231b,#0a3a2b,#0e5540,#083f4e)", "fg": "#EAF4F0"}

_BIN_COLORS = [("#F4C20D", "#C99A00"), ("#2E9E52", "#1B7D3C"), ("#2196F3", "#1565C0"),
               ("#78909C", "#546E7A"), ("#6D4C41", "#4E342E")]
_bins = "".join(
    f'<div class="tbin"><div class="lid" style="background:{lid}"></div>'
    f'<div class="tbody" style="background:{c}">♻</div></div>'
    for c, lid in _BIN_COLORS
)
BINS = f'<div class="hero-art"><div class="globe">🌍</div><div class="binrow">{_bins}</div></div>'


@st.cache_data(show_spinner=False)
def cached_search(kw: str):
    return rechercher_produits(kw)


@st.cache_data(show_spinner=False)
def predire(url: str, titre: str):
    if est_d3e(titre):
        return categorie_d3e()
    r = requests.get(url, timeout=10)
    return predire_categorie(Image.open(BytesIO(r.content)))


def inject_css(glow=None):
    fg = DEFAULT["fg"]
    if glow:
        grad = (f"radial-gradient(1100px circle at 50% -6%, {glow}55, transparent 52%),"
                f"linear-gradient(160deg,#07271e,#05201a 55%,#04171d)")
        anim = "none"
    else:
        grad = DEFAULT["grad"]
        anim = "bgshift 22s ease infinite"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    .stApp {{ background:{grad}; background-size:400% 400%; animation:{anim};
             font-family:'Plus Jakarta Sans',sans-serif; color:{fg}; }}
    @keyframes bgshift {{0%{{background-position:0 50%}}50%{{background-position:100% 50%}}100%{{background-position:0 50%}}}}
    html, body, [class*="css"], .stApp, .stApp p, .stApp span, .stApp div, .stApp label,
    .stApp input, .stApp button {{ font-family:'Plus Jakarta Sans',sans-serif; }}
    .hero-title, .page-title, .rc-title, .nav-logo, .rhead, h1, h2, h3
        {{ font-family:'Sora','Plus Jakarta Sans',sans-serif !important; }}
    .stApp p,.stApp label,.stApp span,.stApp li,.stApp h1,.stApp h2,.stApp h3 {{ color:{fg}; }}
    #MainMenu, header, footer {{ visibility:hidden; }}
    .block-container {{ padding-top:1.2rem; max-width:1200px; }}

    .nav {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; flex-wrap:wrap; }}
    .nav-logo {{ font-size:1.6rem; font-weight:900; text-decoration:none; color:{fg}; }}
    .nav-logo small {{ display:block; font-size:.72rem; font-weight:400; opacity:.7; }}
    .nav-link {{ margin-left:26px; font-weight:600; opacity:.8; text-decoration:none; color:{fg}; }}
    .nav-link:hover {{ opacity:1; }}
    .nav-link.active {{ opacity:1; border-bottom:2px solid #26d07c; padding-bottom:3px; }}

    .hero {{ display:flex; gap:20px; align-items:center; margin:10px 0 4px; flex-wrap:wrap; }}
    .hero-l {{ flex:1 1 46%; }} .hero-r {{ flex:1 1 46%; }}
    .hero-title {{ font-size:3.6rem; font-weight:900; line-height:1.05; letter-spacing:-1.5px; margin:0; animation:fadeUp .7s ease both; }}
    .hero-title b {{ background:linear-gradient(90deg,#7CF5A0,#4DD0E1); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
    .hero-desc {{ font-size:1.15rem; font-weight:300; opacity:.9; max-width:460px; margin-top:14px; animation:fadeUp .7s .15s ease both; }}
    .hero-art {{ text-align:center; }}
    .globe {{ font-size:3.4rem; filter:drop-shadow(0 0 22px rgba(38,208,124,.6)); }}
    .binrow {{ display:flex; gap:14px; justify-content:center; align-items:flex-end; margin-top:6px; }}
    .tbin {{ width:64px; animation:floaty 3.6s ease-in-out infinite; }}
    .tbin:nth-child(2){{animation-delay:.15s}} .tbin:nth-child(3){{animation-delay:.3s}}
    .tbin:nth-child(4){{animation-delay:.45s}} .tbin:nth-child(5){{animation-delay:.6s}}
    .tbin .lid {{ height:12px; border-radius:6px; margin-bottom:3px; }}
    .tbin .tbody {{ height:90px; border-radius:8px 8px 16px 16px; display:flex; align-items:center;
        justify-content:center; font-size:1.7rem; color:#fff; box-shadow:0 10px 24px rgba(0,0,0,.35); }}
    @keyframes floaty {{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}

    .stats {{ display:flex; gap:14px; flex-wrap:wrap; margin:14px 0; }}
    .stat {{ flex:1 1 0; min-width:150px; padding:16px 18px; border-radius:16px; background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.14); backdrop-filter:blur(8px); animation:fadeUp .7s .3s ease both; }}
    .stat b {{ font-size:1.7rem; font-weight:800; }} .stat span {{ display:block; font-size:.9rem; opacity:.8; }}

    .stTextInput input {{ font-size:1.2rem; padding:.9rem 1.1rem; border-radius:16px; background:rgba(255,255,255,.1);
        color:{fg}; border:1px solid rgba(255,255,255,.25); }}
    .stTextInput input::placeholder {{ color:rgba(255,255,255,.5); }}
    .stButton>button {{ border-radius:14px; font-weight:700; font-family:'Plus Jakarta Sans',sans-serif;
        border:1px solid rgba(255,255,255,.2); transition:transform .12s; }}
    .stButton>button:hover {{ transform:translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background:linear-gradient(135deg,#00C853,#00897B); color:#fff; border:none;
        box-shadow:0 6px 20px rgba(0,200,83,.35); font-size:1.05rem; padding:.7rem; }}
    .stButton>button[kind="secondary"] {{ background:rgba(255,255,255,.1); color:{fg}; }}

    .pgrid {{ display:flex; gap:16px; flex-wrap:wrap; margin:10px 0; }}
    .pcard {{ flex:1 1 0; min-width:175px; max-width:230px; text-decoration:none; background:#fff; border-radius:18px;
        padding:12px; border:3px solid transparent; box-shadow:0 6px 20px rgba(0,0,0,.25); display:flex; flex-direction:column;
        transition:transform .16s,box-shadow .16s; animation:cardIn .5s ease both; }}
    .pcard:hover {{ transform:translateY(-8px) scale(1.03); box-shadow:0 16px 34px rgba(0,0,0,.36); }}
    .pcard.selected {{ border-color:#00C853; box-shadow:0 0 0 4px rgba(0,200,83,.3),0 10px 26px rgba(0,0,0,.3); }}
    .pcard img {{ height:170px; object-fit:contain; border-radius:12px; background:#fff; }}
    .pname {{ margin-top:8px; font-size:.92rem; font-weight:600; color:#1a1a1a !important; line-height:1.25; }}
    .pbadge {{ margin-top:auto; padding-top:8px; font-size:.72rem; font-weight:800; color:#F68B1E !important; }}

    .rhead {{ font-size:1.6rem; font-weight:800; margin:18px 0 0; }}
    .rsub {{ opacity:.75; margin-bottom:10px; }}
    .result-card {{ display:flex; gap:30px; align-items:center; border-radius:28px; padding:30px 34px;
        border:1px solid rgba(255,255,255,.25); flex-wrap:wrap;
        animation:popIn .45s cubic-bezier(.2,.9,.3,1.3) both; }}
    .rc-visual {{ display:flex; align-items:flex-end; justify-content:center; min-width:210px; }}
    .bigbin {{ width:110px; animation:floaty 3.6s ease-in-out infinite; }}
    .bigbin .lid {{ height:18px; border-radius:8px; margin-bottom:5px; }}
    .bigbin .body {{ height:138px; border-radius:12px 12px 22px 22px; display:flex; align-items:center;
        justify-content:center; font-size:3rem; color:#fff; box-shadow:0 10px 24px rgba(0,0,0,.3); }}
    .rc-prodimg {{ height:118px; object-fit:contain; margin-left:-22px; background:#fff; border-radius:14px;
        padding:8px; box-shadow:0 12px 24px rgba(0,0,0,.4); }}
    .rc-info {{ flex:1 1 300px; }}
    .rc-title {{ font-size:2.3rem; font-weight:900; line-height:1.1; }}
    .rc-sub2 {{ font-size:1.1rem; opacity:.9; margin-bottom:14px; }}
    .box-mat {{ background:rgba(0,0,0,.30); border-radius:16px; padding:15px 18px; margin-bottom:12px;
        border-left:4px solid rgba(255,255,255,.65); }}
    .box-mat b {{ font-size:1.15rem; }}
    .box-tip {{ background:#FBF6E9; border-radius:16px; padding:15px 18px; }}
    .box-tip b {{ color:#2E7D32; font-size:1.1rem; }}

    .bins {{ display:flex; gap:12px; flex-wrap:wrap; margin:14px 0 4px; }}
    .bin-ind {{ flex:1 1 0; min-width:120px; text-align:center; padding:14px 8px; border-radius:16px;
        background:rgba(255,255,255,.06); border:2px solid rgba(255,255,255,.12); }}
    .bin-ind.on {{ border-color:#fff; box-shadow:0 0 0 3px rgba(255,255,255,.25); }}
    .bin-ind .bi {{ font-size:1.6rem; }} .bin-ind .bn {{ font-weight:800; }} .bin-ind .bs {{ font-size:.78rem; opacity:.75; }}

    /* Pages Categories / Conseils / A propos */
    .page-title {{ font-size:2.4rem; font-weight:900; margin:6px 0; }}
    .page-intro {{ font-size:1.15rem; opacity:.9; max-width:760px; margin-bottom:12px; }}
    .catgrid {{ display:flex; gap:16px; flex-wrap:wrap; }}
    .catcard {{ flex:1 1 0; min-width:230px; border-radius:20px; padding:22px; background:rgba(255,255,255,.08);
        border:1px solid rgba(255,255,255,.16); backdrop-filter:blur(8px); }}
    .catcard .bar {{ height:8px; border-radius:6px; margin-bottom:12px; }}
    .catcard h3 {{ margin:2px 0; font-size:1.4rem; font-weight:800; }}
    .catcard .cs {{ opacity:.8; font-weight:600; }} .catcard p {{ opacity:.9; margin:8px 0 0; }}
    .tipcard {{ border-radius:18px; padding:20px 22px; margin-bottom:14px; background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.14); border-left:4px solid #7CF5A0; }}
    .tipcard b {{ font-size:1.15rem; }}
    .team {{ display:flex; gap:16px; flex-wrap:wrap; margin-top:10px; }}
    .member {{ flex:1 1 0; min-width:200px; border-radius:18px; padding:20px; background:rgba(255,255,255,.08);
        border:1px solid rgba(255,255,255,.16); }}
    .member b {{ font-size:1.15rem; }} .member span {{ opacity:.8; }}

    @keyframes fadeUp {{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
    @keyframes cardIn {{from{{opacity:0;transform:translateY(24px) scale(.96)}}to{{opacity:1;transform:none}}}}
    @keyframes popIn {{from{{opacity:0;transform:scale(.85)}}to{{opacity:1;transform:scale(1)}}}}
    @keyframes grow {{from{{width:0}}}}
    @keyframes spinpulse {{0%,100%{{transform:rotate(0) scale(1)}}50%{{transform:rotate(180deg) scale(1.12)}}}}
    </style>
    """, unsafe_allow_html=True)


def do_search(kw: str):
    st.query_params["page"] = "accueil"
    st.query_params["q"] = kw
    if "choix" in st.query_params:
        del st.query_params["choix"]
    st.rerun()


def render_nav(page):
    items = [("accueil", "Accueil"), ("categories", "Catégories"), ("apropos", "À propos")]
    links = "".join(
        f'<a class="nav-link {"active" if page == pid else ""}" href="?page={pid}" target="_self">{label}</a>'
        for pid, label in items)
    st.markdown(
        f'<div class="nav"><a class="nav-logo" href="?page=accueil" target="_self">♻️ EcoSort'
        f'<small>Votre guide intelligent du tri</small></a>'
        f'<div class="nav-links">{links}</div></div>', unsafe_allow_html=True)


# =================== ROUTAGE ===================
page = st.query_params.get("page", "accueil")

# --- Etat de recherche (uniquement sur l'accueil) ---
produits = choix = res = erreur = None
style = None
if page == "accueil":
    q = st.query_params.get("q", "")
    choix_idx = st.query_params.get("choix")
    if q:
        with st.spinner("Recherche sur Jumia CI…"):
            produits = cached_search(q)
    if produits and choix_idx is not None:
        try:
            ci = int(choix_idx)
            if 0 <= ci < len(produits):
                choix = produits[ci]
        except ValueError:
            pass
    if choix:
        try:
            with st.spinner("🔎 Analyse du produit en cours…"):
                res = predire(choix["url_image"], choix["titre"])
        except Exception as e:
            erreur = f"Impossible d'analyser l'image ({e})."
    style = STYLE.get(res["categorie"]) if res else None

inject_css(style["color"] if style else None)
render_nav(page)


# =================== PAGE ACCUEIL ===================
if page == "accueil":
    if produits is None:
        st.markdown(f"""
        <div class="hero">
          <div class="hero-l">
            <h1 class="hero-title">Triez juste,<br><b>préservez demain</b> 🌍</h1>
            <p class="hero-desc">Vous ne savez pas dans quelle poubelle jeter un produit ?
            Recherchez-le, cliquez dessus, et notre intelligence artificielle vous indique
            instantanément la bonne poubelle.</p>
          </div>
          <div class="hero-r">{BINS}</div>
        </div>
        """, unsafe_allow_html=True)

    saisie = st.text_input("Produit", value=st.query_params.get("q", ""),
                           placeholder="Rechercher un produit…  ex : bouteille, chargeur, journal",
                           label_visibility="collapsed")
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🔍 Rechercher", type="primary", use_container_width=True) and saisie:
            do_search(saisie)

    st.write("Recherches populaires :")
    chips = st.columns(6)
    for col, ex in zip(chips, ["bouteille", "chargeur", "journal", "canette", "bocal", "smartphone"]):
        if col.button(ex, use_container_width=True):
            do_search(ex)

    if produits is None:
        st.markdown("""
        <div class="stats">
          <div class="stat"><b>5</b><span>Catégories de tri</span></div>
          <div class="stat"><b>6</b><span>Matières reconnues par l'IA</span></div>
          <div class="stat"><b>~90%</b><span>Précision du modèle</span></div>
          <div class="stat"><b>Jumia CI</b><span>Catalogue en temps réel</span></div>
        </div>
        """, unsafe_allow_html=True)

    if res:
        pct = int(res["confiance"] * 100)
        lbl = CLASSE_LABEL.get(res["classe_brute"], res["classe_brute"])
        st.markdown("<div class='rhead'>✨ Résultat de l'analyse</div>"
                    "<div class='rsub'>Voici la consigne de tri pour ce produit</div>",
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="result-card" style="background:{style['card']}; color:{style['fg']};
             box-shadow:0 24px 60px {style['color']}66;">
          <div class="rc-visual">
            <div class="bigbin">
              <div class="lid" style="background:rgba(0,0,0,.28)"></div>
              <div class="body" style="background:rgba(255,255,255,.20)">♻</div>
            </div>
            <img class="rc-prodimg" src="{choix['url_image']}"/>
          </div>
          <div class="rc-info">
            <div class="rc-title" style="color:{style['fg']}">{style['icon']} {style['title']}</div>
            <div class="rc-sub2" style="color:{style['fg']}">{style['sub']}</div>
            <div class="box-mat">
              <b style="color:#fff">♻ {lbl}</b>
              <div style="color:#f2f2f2">{style['detail']}</div>
              <div style="color:#f2f2f2;opacity:.75;margin-top:6px;font-size:.88rem">
                  Produit : {choix['titre']} — confiance du modèle : {pct}%</div>
            </div>
            <div class="box-tip">
              <b>🌱 Conseil éco-responsable</b>
              <div style="color:#3a3a2a">{style['tip']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        bins = '<div class="bins">'
        for cat in ORDER:
            s = STYLE[cat]
            on = "on" if cat == res["categorie"] else ""
            chk = " ✅" if cat == res["categorie"] else ""
            bins += (f'<div class="bin-ind {on}"><div class="bi">{s["icon"]}</div>'
                     f'<div class="bn">{SHORT[cat]}{chk}</div><div class="bs">{s["sub"]}</div></div>')
        bins += '</div>'
        st.markdown(bins, unsafe_allow_html=True)
    elif erreur:
        st.error(erreur)

    if produits is not None:
        if len(produits) == 0:
            st.warning("Aucun produit trouvé. Essayez un autre mot-clé.")
        else:
            st.markdown(f"<div class='rhead'>🛍️ Résultats pour « {q} » — cliquez sur un produit</div>",
                        unsafe_allow_html=True)
            qq = quote(q)
            cards = '<div class="pgrid">'
            for i, p in enumerate(produits):
                sel = "selected" if (choix and choix.get("lien") == p.get("lien")) else ""
                cards += (
                    f'<a class="pcard {sel}" style="animation-delay:{i*0.07}s" '
                    f'href="?page=accueil&q={qq}&choix={i}" target="_self">'
                    f'<img src="{p.get("url_image","")}"/>'
                    f'<div class="pname">{p["titre"]}</div>'
                    f'<div class="pbadge">JUMIA CI</div></a>'
                )
            cards += '</div>'
            st.markdown(cards, unsafe_allow_html=True)

# =================== PAGE CATEGORIES ===================
elif page == "categories":
    st.markdown("<div class='page-title'>🗂️ Les 5 catégories de tri</div>", unsafe_allow_html=True)
    st.markdown("<p class='page-intro'>EcoSort classe chaque produit dans l'une de ces cinq poubelles, "
                "selon la matière détectée par l'intelligence artificielle.</p>", unsafe_allow_html=True)
    cats = '<div class="catgrid">'
    for cat in ORDER:
        s = STYLE[cat]
        cats += (f'<div class="catcard"><div class="bar" style="background:{s["color"]}"></div>'
                 f'<h3>{s["icon"]} Poubelle {SHORT[cat]}</h3><div class="cs">{s["sub"]}</div>'
                 f'<p>{s["consigne"]}</p><p>🌱 {s["tip"]}</p></div>')
    cats += '</div>'
    st.markdown(cats, unsafe_allow_html=True)

# =================== PAGE A PROPOS ===================
elif page == "apropos":
    st.markdown("<div class='page-title'>ℹ️ À propos d'EcoSort</div>", unsafe_allow_html=True)
    st.markdown("<p class='page-intro'>EcoSort-Search est une application d'aide au tri sélectif. "
                "Vous cherchez un produit sur le catalogue Jumia CI, et une intelligence artificielle "
                "(réseau de neurones) analyse son image pour déterminer la bonne poubelle.</p>",
                unsafe_allow_html=True)
    st.markdown("""
    <div class="catgrid">
      <div class="catcard"><h3>🔍 1. Recherche</h3><p>Le nom saisi interroge en direct le catalogue Jumia Côte d'Ivoire (scraping).</p></div>
      <div class="catcard"><h3>🧠 2. Analyse IA</h3><p>Un modèle MobileNetV2 (Transfer Learning) reconnaît la matière du produit choisi.</p></div>
      <div class="catcard"><h3>♻️ 3. Consigne</h3><p>L'écran se colore à la couleur de la bonne poubelle avec la consigne de tri.</p></div>
    </div>
    <br>
    <p class="page-intro"><b>Technologies :</b> Python, TensorFlow/Keras, BeautifulSoup, Streamlit, Docker.</p>
    <div class="team">
      <div class="member"><b>ATOUKOUVI Komi Dénis</b><br><span>IA &amp; Frontend</span></div>
      <div class="member"><b>ATEBA Aristide</b><br><span>Scraping / Backend</span></div>
      <div class="member"><b>FOGAING Franck Noël</b><br><span>DevOps / Docker</span></div>
    </div>
    """, unsafe_allow_html=True)
