
import sqlite3
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from logique import get_movie_details, API_KEY


# =====================================================
# CONFIGURATION
# =====================================================

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

DB_PATH = Path(__file__).resolve().parent / "data" / "tmdb.db"

st.set_page_config(
    page_title="MovieDataBase",
    page_icon="🎬",
    layout="wide"
)


# =====================================================
# STYLE
# =====================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 1250px;
    }

    h1, h2, h3 {
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
        padding: 15px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🎬 MovieDataBase")
st.caption(
    "Explore, découvre et compare des films grâce à TMDB et SQLite."
)


# =====================================================
# DONNEES SQLITE
# =====================================================

@st.cache_data(show_spinner="Chargement des films...")
def charger_films_populaires():
    """
    Charge les films les plus populaires depuis SQLite.
    Utilisés pour les listes intelligentes.
    """

    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as connexion:
        df = pd.read_sql_query(
            """
            SELECT id, original_title, popularity
            FROM films
            WHERE original_title IS NOT NULL
              AND TRIM(original_title) != ''
            ORDER BY popularity DESC
            LIMIT 10000
            """,
            connexion
        )

    return df.to_dict("records")


def nom_film(film):
    """Texte affiché dans les listes déroulantes."""

    if film is None:
        return ""

    return f"{film['original_title']} (ID : {film['id']})"


# =====================================================
# API TMDB
# =====================================================

@st.cache_data(ttl=3600)
def rechercher_films(texte):
    """Recherche un film dans l'API TMDB."""

    reponse = requests.get(
        f"{BASE_URL}/search/movie",
        params={
            "api_key": API_KEY,
            "query": texte,
            "language": "fr-FR"
        },
        timeout=15
    )

    reponse.raise_for_status()

    return reponse.json().get("results", [])


@st.cache_data(ttl=3600)
def details_film(movie_id):
    """
    Récupère les détails d'un film
    ainsi que son affiche.
    """

    film = get_movie_details(int(movie_id))

    if film is None:
        return None

    reponse = requests.get(
        f"{BASE_URL}/movie/{movie_id}",
        params={
            "api_key": API_KEY,
            "language": "fr-FR"
        },
        timeout=15
    )

    if reponse.status_code == 404:
        return None

    reponse.raise_for_status()

    data = reponse.json()

    film["affiche"] = (
        IMAGE_URL + data["poster_path"]
        if data.get("poster_path")
        else None
    )

    film["description"] = data.get("overview") or (
        "Aucun synopsis disponible."
    )

    film["duree"] = data.get("runtime")

    return film


# =====================================================
# AFFICHAGE D'UN FILM
# =====================================================

def afficher_film(film):

    if film is None:
        st.warning("Film introuvable.")
        return

    col_affiche, col_infos = st.columns([1, 2])

    with col_affiche:
        if film.get("affiche"):
            st.image(
                film["affiche"],
                use_container_width=True
            )
        else:
            st.info("Aucune affiche disponible.")

    with col_infos:

        st.subheader(film.get("titre", "Titre inconnu"))

        st.write(
            "📅 **Date de sortie :**",
            film.get("date_sortie") or "Inconnue"
        )

        st.write(
            "🎭 **Genres :**",
            ", ".join(film.get("genres", []))
            or "Non renseignés"
        )

        if film.get("duree"):
            st.write(
                "⏱️ **Durée :**",
                f"{film['duree']} minutes"
            )

        note = film.get("note_moyenne") or 0
        popularite = film.get("popularite") or 0

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "⭐ Note moyenne",
                f"{note:.1f}/10"
            )

        with c2:
            st.metric(
                "🔥 Popularité",
                f"{popularite:.2f}"
            )

        st.markdown("#### 📖 Synopsis")
        st.write(film.get("description") or "Non disponible.")


# =====================================================
# LISTE INTELLIGENTE
# =====================================================

def selection_film(label, key):
    """
    Un seul champ avec recherche intégrée.
    L'utilisateur tape directement dans la liste.
    """

    films = charger_films_populaires()

    if not films:
        st.warning(
            "Aucune donnée locale disponible. "
            "Lance d'abord python exports.py."
        )
        return None

    return st.selectbox(
        label,
        options=films,
        index=None,
        placeholder="🔍 Tape le nom d'un film...",
        format_func=nom_film,
        key=key
    )


# =====================================================
# ONGLETS
# =====================================================

tab_recherche, tab_comparer, tab_base = st.tabs(
    [
        "🔎 Rechercher",
        "⚖️ Comparer",
        "🗃️ Base SQLite"
    ]
)


# =====================================================
# ONGLET 1 : RECHERCHER
# =====================================================

with tab_recherche:

    st.header("🔎 Rechercher un film")

    st.write(
        "Commence à écrire dans la liste et sélectionne "
        "directement le film souhaité."
    )

    film_choisi = selection_film(
        "🎬 Choisir un film",
        "recherche_film"
    )

    if film_choisi is not None:

        try:
            with st.spinner("Chargement du film..."):
                film = details_film(film_choisi["id"])

            afficher_film(film)

        except requests.RequestException as erreur:
            st.error(f"Erreur API TMDB : {erreur}")

        except Exception as erreur:
            st.error(f"Erreur : {erreur}")


# =====================================================
# ONGLET 2 : COMPARER
# =====================================================

with tab_comparer:

    st.header("⚖️ Comparer deux films")

    st.write(
        "Sélectionne deux films grâce aux listes intelligentes."
    )

    col1, col2 = st.columns(2)

    with col1:
        film1 = selection_film(
            "🎬 Premier film",
            "comparaison_film1"
        )

    with col2:
        film2 = selection_film(
            "🎬 Deuxième film",
            "comparaison_film2"
        )

    if st.button(
        "⚔️ Comparer les films",
        use_container_width=True
    ):

        if film1 is None or film2 is None:
            st.warning("Sélectionne deux films.")

        elif film1["id"] == film2["id"]:
            st.warning("Choisis deux films différents.")

        else:

            try:
                with st.spinner("Comparaison en cours..."):
                    f1 = details_film(film1["id"])
                    f2 = details_film(film2["id"])

                if f1 is None or f2 is None:
                    st.error("Un des films est introuvable.")

                else:

                    gauche, droite = st.columns(2)

                    with gauche:
                        afficher_film(f1)

                    with droite:
                        afficher_film(f2)

                    st.divider()

                    st.subheader("📊 Comparaison des notes")

                    df = pd.DataFrame({
                        "Film": [
                            f1["titre"],
                            f2["titre"]
                        ],
                        "Note": [
                            f1["note_moyenne"],
                            f2["note_moyenne"]
                        ],
                        "Popularité": [
                            f1["popularite"],
                            f2["popularite"]
                        ]
                    })

                    st.bar_chart(
                        df.set_index("Film")["Note"]
                    )

                    st.subheader("📋 Tableau comparatif")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

            except requests.RequestException as erreur:
                st.error(f"Erreur API TMDB : {erreur}")

            except Exception as erreur:
                st.error(f"Erreur : {erreur}")


# =====================================================
# ONGLET 3 : BASE SQLITE
# =====================================================

with tab_base:

    st.header("🗃️ Base de données SQLite")

    if not DB_PATH.exists():

        st.warning(
            "Base de données introuvable. "
            "Lance python exports.py."
        )

    else:

        try:
            with sqlite3.connect(DB_PATH) as connexion:

                total = connexion.execute(
                    "SELECT COUNT(*) FROM films"
                ).fetchone()[0]

                st.metric(
                    "🎬 Nombre total de films",
                    f"{total:,}".replace(",", " ")
                )

                recherche_sql = st.text_input(
                    "🔍 Rechercher dans la base",
                    placeholder="Tape le titre d'un film...",
                    key="recherche_sql"
                )

                if recherche_sql.strip():

                    df = pd.read_sql_query(
                        """
                        SELECT
                            id,
                            original_title AS titre,
                            popularity AS popularite
                        FROM films
                        WHERE original_title LIKE ?
                        ORDER BY popularity DESC
                        LIMIT 100
                        """,
                        connexion,
                        params=(
                            f"%{recherche_sql.strip()}%",
                        )
                    )

                else:

                    df = pd.read_sql_query(
                        """
                        SELECT
                            id,
                            original_title AS titre,
                            popularity AS popularite
                        FROM films
                        ORDER BY popularity DESC
                        LIMIT 100
                        """,
                        connexion
                    )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Affichage limité aux 100 premiers résultats."
            )

            if df.empty:
                st.info("Aucun film trouvé.")

        except sqlite3.Error as erreur:
            st.error(f"Erreur SQLite : {erreur}")


# =====================================================
# PIED DE PAGE
# =====================================================

st.divider()

st.caption(
    "🎬 MovieDataBase — Mini Projet 1 | "
    "Python • TMDB API • Pandas • SQLite • Streamlit"
)
