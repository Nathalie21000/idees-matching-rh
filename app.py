import re

import streamlit as st

from database import (
    init_db,
    enregistrer_cv,
    enregistrer_poste,
    enregistrer_suivi,
    compter_cv,
    compter_postes,
    compter_suivi,
    compter_clients,
    compter_prospects,
    repartition_suivi,
    lister_cv,
    recuperer_cvs_matching,
    recuperer_postes,
    recuperer_poste,
    recuperer_cv,
    lister_suivi,
    modifier_statut_suivi,
    statistiques_par_semaine,
    statistiques_dz,
    supprimer_cv,
    supprimer_poste,
)

from matching import calculer_score

from metiers import (
    METIERS,
    detecter_metier,
    extraire_competences_pro,
    extraire_taches,
    detecter_vip_sir,
)

from utils import (
    extract_text,
    generer_presentation,
    extraire_fiche_poste_ciblee,
)


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ID'EES INTERIM - Assistant IA RH",
    page_icon="logo.png",
    layout="wide",
)


# ============================================================
# IDENTITE VISUELLE ID'EES
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --idees-green: #00A878;
        --idees-green-dark: #008F68;
        --idees-green-light: #E9F7F2;
        --idees-anthracite: #2F3437;
        --idees-grey: #F4F7F6;
        --idees-border: #DCE5E1;
        --idees-white: #FFFFFF;
    }

    /* ===== FOND GENERAL ===== */
    .stApp {
        background: #FFFFFF;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* ===== TYPOGRAPHIE ===== */
    h1, h2, h3, h4 {
        color: var(--idees-anthracite) !important;
        letter-spacing: -0.02em;
    }

    h1 {
        font-weight: 750 !important;
    }

    h2, h3 {
        font-weight: 700 !important;
    }

    p, label, [data-testid="stCaptionContainer"] {
        color: #667078;
    }

    /* ===== SIDEBAR ID'EES INTERIM ===== */
    [data-testid="stSidebar"] {
        background: #263238;
        border-right: none;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }

    /* ===== LOGO ID'EES INTERIM ===== */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 10px 14px;
        margin: 0 auto 1rem auto;
        box-sizing: border-box;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] .stSelectbox > label,
    [data-testid="stSidebar"] .stRadio > label {
        color: #DCE5E1 !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFFFF;
        border: 1px solid #DCE5E1;
        border-radius: 8px;
    }

    /* Navigation radio : apparence plus proche d'un menu */
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.25rem;
    }

    [data-testid="stSidebar"] [role="radio"] {
        border-radius: 8px;
        padding: 0.42rem 0.55rem;
        transition: background 0.15s ease;
    }

    [data-testid="stSidebar"] [role="radio"]:hover {
        background: rgba(0, 168, 120, 0.16);
    }

    [data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
        background: var(--idees-green);
    }

    [data-testid="stSidebar"] [role="radio"][aria-checked="true"] p,
    [data-testid="stSidebar"] [role="radio"][aria-checked="true"] span {
        color: #FFFFFF !important;
        font-weight: 700;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.16);
    }

    /* ===== CARTES METRIQUES ===== */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--idees-border);
        border-left: 4px solid var(--idees-green);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 10px rgba(39, 55, 61, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #657078 !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--idees-anthracite) !important;
        font-weight: 750;
    }

    /* ===== BOUTONS ===== */
    .stButton > button {
        background: var(--idees-green);
        color: #FFFFFF;
        border: 1px solid var(--idees-green);
        border-radius: 8px;
        font-weight: 650;
        min-height: 2.55rem;
        box-shadow: none;
    }

    .stButton > button:hover {
        background: var(--idees-green-dark);
        border-color: var(--idees-green-dark);
        color: #FFFFFF;
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(0,168,120,0.22);
    }

    /* ===== INPUTS / SELECTS ===== */
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div {
        border-color: var(--idees-border);
        border-radius: 8px;
    }

    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] > div:focus-within,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--idees-green);
        box-shadow: 0 0 0 1px var(--idees-green);
    }

    /* ===== EXPANDERS / BLOCS ===== */
    [data-testid="stExpander"] {
        border: 1px solid var(--idees-border);
        border-radius: 10px;
        background: #FFFFFF;
    }

    [data-testid="stExpander"] summary:hover {
        color: var(--idees-green);
    }

    /* ===== PROGRESS ===== */
    [data-testid="stProgressBar"] > div > div {
        background: var(--idees-green);
    }

    /* ===== SEPARATEURS ===== */
    hr {
        border-color: var(--idees-border);
    }

    /* ===== BANDEAUX / ZONES NATIVES STREAMLIT ===== */
    [data-testid="stAlert"] {
        border-radius: 10px;
        background: var(--idees-green-light);
        border-left: 4px solid var(--idees-green);
    }

    /* Barres et en-têtes des zones de recherche / sélection */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input {
        background: #FFFFFF;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stDateInput"] input:focus {
        border-color: var(--idees-green) !important;
        box-shadow: 0 0 0 1px var(--idees-green) !important;
    }

    /* En-têtes de tableaux */
    [data-testid="stDataFrame"] th {
        background: var(--idees-green-light) !important;
        color: var(--idees-anthracite) !important;
    }

    /* Onglets / bandeaux de navigation Streamlit */
    [data-baseweb="tab-list"] {
        background: var(--idees-green-light);
        border-radius: 8px;
        padding: 3px;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--idees-green-dark) !important;
    }

    /* ===== LIENS ===== */
    a {
        color: var(--idees-green-dark);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


AGENCES = [
    "Alençon",
    "Avranches",
    "Dinan",
    "Honfleur",
    "Le Mans",
    "Rennes",
    "Saint-Malo",
]


STATUTS_SUIVI = [
    "Candidature envoyée",
    "Entretien programmé",
    "Recruté",
    "Refusé",
    "Commande non pourvue",
]


init_db()


# ============================================================
# EXTRACTION CANDIDAT
# ============================================================

def extraire_candidat(nom_fichier):

    nom = re.sub(
        r"\.pdf$",
        "",
        nom_fichier,
        flags=re.IGNORECASE,
    )

    nom = re.sub(
        r"\.docx$",
        "",
        nom,
        flags=re.IGNORECASE,
    )

    nom = re.sub(
        r"[_\-]+",
        " ",
        nom,
    )

    nom = re.sub(
        r"\s+",
        " ",
        nom,
    ).strip()

    return nom.title() if nom else "Candidat inconnu"


# ============================================================
# EXTRACTION COMPETENCES
# ============================================================

def extraire_competences(texte):

    trouve = set()

    texte_min = texte.lower()

    for mots in METIERS.values():

        for mot in mots:

            if mot.lower() in texte_min:

                trouve.add(mot)

    for competence in extraire_competences_pro(texte):

        trouve.add(competence)

    return ", ".join(
        sorted(trouve)
    )


# ============================================================
# EXTRACTION CACES
# ============================================================

def extraire_caces(texte):

    resultats = {
        m.upper()
        for m in re.findall(
            r"r4\d{2}",
            texte,
            flags=re.IGNORECASE,
        )
    }

    return ", ".join(
        sorted(resultats)
    )


# ============================================================
# EXTRACTION PERMIS
# ============================================================

def extraire_permis(texte):

    resultats = {
        m.upper()
        for m in re.findall(
            r"permis\s+([a-z]{1,2}\d?)",
            texte,
            flags=re.IGNORECASE,
        )
    }

    return ", ".join(
        sorted(resultats)
    )


# ============================================================
# BARRE LATERALE
# ============================================================

st.sidebar.image(
    "logo.png",
    width=180,
)

st.sidebar.title("ID'EES INTERIM")

agence = st.sidebar.selectbox(
    "Agence",
    AGENCES,
)


page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Tableau de bord",
        "🌐 Tableau de bord DZ",
        "📄 Importer un CV",
        "📂 CVthèque",
        "🏢 Importer une fiche de poste",
        "📁 Postethèque",
        "🔍 Matching",
        "📋 Suivi des candidatures",
        "📈 Statistiques",
    ],
)


st.sidebar.markdown("---")

st.sidebar.caption(
    f"Agence sélectionnée : **{agence}**"
)


# ============================================================
# TABLEAU DE BORD AGENCE
# ============================================================

if page == "📊 Tableau de bord":

    st.title(
        "📊 Tableau de bord"
    )

    st.caption(
        f"Agence : {agence}"
    )

    # --------------------------------------------------------
    # INDICATEURS PRINCIPAUX
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "CV enregistrés",
        compter_cv(agence),
    )

    col2.metric(
        "Postes enregistrés",
        compter_postes(agence),
    )

    col3.metric(
        "Entretiens programmés",
        compter_suivi(
            agence,
            "Entretien programmé",
        ),
    )

    col4.metric(
        "Recrutements",
        compter_suivi(
            agence,
            "Recruté",
        ),
    )

    # --------------------------------------------------------
    # RECUPERATION DES DONNEES DE L'AGENCE
    # --------------------------------------------------------

    cvs_dashboard = lister_cv(
        agence
    )

    suivis_dashboard = lister_suivi(
        agence
    )

    postes_dashboard = recuperer_postes(
        agence
    )

    st.markdown("---")

    # --------------------------------------------------------
    # TAUX DE TRANSFORMATION CLIENTS / PROSPECTS
    # --------------------------------------------------------

    st.subheader(
        "🎯 Taux de transformation"
    )

    candidatures_clients = [
        ligne
        for ligne in suivis_dashboard
        if ligne.get("type_entreprise") == "🟢 Client"
        and ligne.get("candidat")
        and ligne.get("statut") != "Commande non pourvue"
    ]

    candidatures_prospects = [
        ligne
        for ligne in suivis_dashboard
        if ligne.get("type_entreprise") == "🟠 Prospect"
        and ligne.get("candidat")
        and ligne.get("statut") != "Commande non pourvue"
    ]

    recrutes_clients = [
        ligne
        for ligne in candidatures_clients
        if ligne.get("statut") == "Recruté"
    ]

    recrutes_prospects = [
        ligne
        for ligne in candidatures_prospects
        if ligne.get("statut") == "Recruté"
    ]

    taux_clients = (
        len(recrutes_clients) / len(candidatures_clients) * 100
        if candidatures_clients
        else 0
    )

    taux_prospects = (
        len(recrutes_prospects) / len(candidatures_prospects) * 100
        if candidatures_prospects
        else 0
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 🎯 Taux de transformation **clients**"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Envoyés",
            len(candidatures_clients),
        )

        c2.metric(
            "Recrutés",
            len(recrutes_clients),
        )

        c3.metric(
            "Taux",
            f"{taux_clients:.1f} %",
        )

    with col2:

        st.markdown(
            "### 🎯 Taux de transformation **prospects**"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Envoyés",
            len(candidatures_prospects),
        )

        c2.metric(
            "Recrutés",
            len(recrutes_prospects),
        )

        c3.metric(
            "Taux",
            f"{taux_prospects:.1f} %",
        )

    st.caption(
        "Le taux est calculé sur les candidatures envoyées "
        "(hors commandes non pourvues)."
    )

    # --------------------------------------------------------
    # REPARTITION DES PROFILS ENVOYES
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "👤 Répartition des profils envoyés"
    )

    # On relie le candidat du suivi à son CV afin de retrouver
    # le type de profil enregistré : Intérimaire ou Candidat.
    profils_par_candidat = {}

    for cv in cvs_dashboard:

        nom_candidat = (
            cv.get("candidat") or ""
        ).strip().lower()

        if nom_candidat and nom_candidat not in profils_par_candidat:

            profils_par_candidat[nom_candidat] = (
                cv.get("type_profil") or ""
            )

    statistiques_profils = []

    for profil in [
        "🟢 Intérimaire",
        "🟡 Candidat",
    ]:

        lignes_profil = []

        for ligne in suivis_dashboard:

            candidat = (
                ligne.get("candidat") or ""
            ).strip().lower()

            type_entreprise = (
                ligne.get("type_entreprise") or ""
            )

            statut = ligne.get(
                "statut"
            )

            type_profil = profils_par_candidat.get(
                candidat,
                "",
            )

            if (
                candidat
                and type_profil == profil
                and type_entreprise in [
                    "🟢 Client",
                    "🟠 Prospect",
                ]
                and statut != "Commande non pourvue"
            ):

                lignes_profil.append(
                    ligne
                )

        recrutes_profil = [
            ligne
            for ligne in lignes_profil
            if ligne.get("statut") == "Recruté"
        ]

        taux_profil = (
            len(recrutes_profil) / len(lignes_profil) * 100
            if lignes_profil
            else 0
        )

        statistiques_profils.append(
            {
                "Profil": profil,
                "Nombre envoyé": len(lignes_profil),
                "Recruté": len(recrutes_profil),
                "Taux de transformation": (
                    f"{taux_profil:.1f} %"
                ),
            }
        )

    st.dataframe(
        statistiques_profils,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # METIERS PRESENTS DANS LA CVTHEQUE
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "👷 Métiers présents dans la CVthèque"
    )

    compte_metiers = {}

    for cv in cvs_dashboard:

        metier = (
            cv.get("metier") or ""
        ).strip()

        if metier:

            compte_metiers[metier] = (
                compte_metiers.get(metier, 0) + 1
            )

    if compte_metiers:

        compte_metiers = dict(
            sorted(
                compte_metiers.items(),
                key=lambda element: element[1],
                reverse=True,
            )
        )

        st.bar_chart(
            compte_metiers,
            color="#00A878",
        )

    else:

        st.info(
            "Aucun métier renseigné dans la CVthèque."
        )

    # --------------------------------------------------------
    # METIERS RECHERCHES / PRESSENTIS
    # --------------------------------------------------------

    st.subheader(
        "🎯 Métiers recherchés / pressentis"
    )

    compte_metiers_recherches = {}

    for cv in cvs_dashboard:

        valeur = (
            cv.get("metiers_recherches") or ""
        )

        for metier_recherche in valeur.split(","):

            metier_recherche = metier_recherche.strip()

            if metier_recherche:

                compte_metiers_recherches[
                    metier_recherche
                ] = (
                    compte_metiers_recherches.get(
                        metier_recherche,
                        0,
                    ) + 1
                )

    if compte_metiers_recherches:

        compte_metiers_recherches = dict(
            sorted(
                compte_metiers_recherches.items(),
                key=lambda element: element[1],
                reverse=True,
            )
        )

        st.bar_chart(
            compte_metiers_recherches,
            color="#00A878",
        )

    else:

        st.info(
            "Aucun métier recherché / pressenti renseigné."
        )

    # --------------------------------------------------------
    # POSTES LES PLUS DEMANDES
    # --------------------------------------------------------

    st.subheader(
        "🏢 Postes les plus demandés"
    )

    compte_postes_demandes = {}

    for poste in postes_dashboard:

        intitule = (
            poste.get("poste") or ""
        ).strip()

        if intitule:

            compte_postes_demandes[intitule] = (
                compte_postes_demandes.get(
                    intitule,
                    0,
                ) + 1
            )

    if compte_postes_demandes:

        compte_postes_demandes = dict(
            sorted(
                compte_postes_demandes.items(),
                key=lambda element: element[1],
                reverse=True,
            )
        )

        st.bar_chart(
            compte_postes_demandes,
            color="#00A878",
        )

    else:

        st.info(
            "Aucun poste enregistré pour cette agence."
        )

    # --------------------------------------------------------
    # REPARTITION DES CANDIDATURES PAR STATUT
    # --------------------------------------------------------

    st.subheader(
        "📋 Répartition des candidatures par statut"
    )

    compte_statuts = {}

    for ligne in suivis_dashboard:

        statut = (
            ligne.get("statut") or ""
        )

        if statut:

            compte_statuts[statut] = (
                compte_statuts.get(
                    statut,
                    0,
                ) + 1
            )

    if compte_statuts:

        st.bar_chart(
            compte_statuts,
            color="#00A878",
        )

    else:

        st.info(
            "Aucune candidature suivie pour le moment."
        )

# ============================================================
# TABLEAU DE BORD DZ
# ============================================================

elif page == "🌐 Tableau de bord DZ":

    st.title(
        "🌐 Tableau de bord DZ"
    )

    st.caption(
        "Vue régionale — comparaison des agences ID'EES INTERIM"
    )

    st.info(
        "Cette page permet à chaque agence de voir "
        "l'activité des autres agences et de se situer "
        "par rapport au réseau."
    )

    # --------------------------------------------------------
    # Récupération des statistiques
    # --------------------------------------------------------

    try:

        stats_dz = statistiques_dz(
            AGENCES
        )

    except Exception as erreur:

        st.error(
            "Impossible de récupérer les statistiques DZ."
        )

        st.exception(erreur)

        stats_dz = {}

    if stats_dz:

        # ----------------------------------------------------
        # TOTAL DZ
        # ----------------------------------------------------

        total_cv = sum(
            stats["cv"]
            for stats in stats_dz.values()
        )

        total_postes = sum(
            stats["postes"]
            for stats in stats_dz.values()
        )

        total_candidatures = sum(
            stats["candidatures"]
            for stats in stats_dz.values()
        )

        total_entretiens = sum(
            stats["entretiens"]
            for stats in stats_dz.values()
        )

        total_recrutements = sum(
            stats["recrutements"]
            for stats in stats_dz.values()
        )

        total_clients = sum(
            stats["clients"]
            for stats in stats_dz.values()
        )

        total_prospects = sum(
            stats["prospects"]
            for stats in stats_dz.values()
        )

        st.subheader(
            "📊 Activité totale de la DZ"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "CV",
            total_cv,
        )

        col2.metric(
            "Postes",
            total_postes,
        )

        col3.metric(
            "Candidatures",
            total_candidatures,
        )

        col4.metric(
            "Recrutements",
            total_recrutements,
        )

        col5, col6, col7 = st.columns(3)

        col5.metric(
            "Entretiens",
            total_entretiens,
        )

        col6.metric(
            "🟢 Clients",
            total_clients,
        )

        col7.metric(
            "🟠 Prospects",
            total_prospects,
        )

        st.markdown("---")

        # ----------------------------------------------------
        # TABLEAU COMPARATIF
        # ----------------------------------------------------

        st.subheader(
            "🏢 Comparatif des agences"
        )

        tableau_agences = []

        for nom_agence, stats in stats_dz.items():

            # Même définition que dans le tableau de bord agence :
            # recrutement(s) / candidature(s) envoyée(s)
            # pour chaque type d'entreprise.
            suivis_agence_dz = lister_suivi(
                nom_agence
            )

            candidatures_clients = [
                ligne
                for ligne in suivis_agence_dz
                if ligne.get("type_entreprise") == "🟢 Client"
                and ligne.get("candidat")
                and ligne.get("statut") != "Commande non pourvue"
            ]

            candidatures_prospects = [
                ligne
                for ligne in suivis_agence_dz
                if ligne.get("type_entreprise") == "🟠 Prospect"
                and ligne.get("candidat")
                and ligne.get("statut") != "Commande non pourvue"
            ]

            recrutes_clients = [
                ligne
                for ligne in candidatures_clients
                if ligne.get("statut") == "Recruté"
            ]

            recrutes_prospects = [
                ligne
                for ligne in candidatures_prospects
                if ligne.get("statut") == "Recruté"
            ]

            taux_clients = (
                len(recrutes_clients)
                / len(candidatures_clients)
                * 100
                if candidatures_clients
                else 0
            )

            taux_prospects = (
                len(recrutes_prospects)
                / len(candidatures_prospects)
                * 100
                if candidatures_prospects
                else 0
            )

            tableau_agences.append(
                {
                    "Agence": nom_agence,
                    "CV": stats["cv"],
                    "Postes": stats["postes"],
                    "Candidatures": stats["candidatures"],
                    "Entretiens": stats["entretiens"],
                    "Recrutements": stats["recrutements"],
                    "Clients": stats["clients"],
                    "Taux transformation client": f"{taux_clients:.1f} %",
                    "Prospects": stats["prospects"],
                    "Taux transformation prospect": f"{taux_prospects:.1f} %",
                }
            )

        tableau_agences.sort(
            key=lambda ligne: (
                ligne["Recrutements"],
                ligne["Candidatures"],
                ligne["Postes"],
            ),
            reverse=True,
        )

        st.dataframe(
            tableau_agences,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # ----------------------------------------------------
        # CLASSEMENT
        # ----------------------------------------------------

        st.subheader(
            "🏆 Classement des recrutements"
        )

        classement = sorted(
            stats_dz.items(),
            key=lambda element: (
                element[1]["recrutements"],
                element[1]["candidatures"],
                element[1]["postes"],
            ),
            reverse=True,
        )

        for position, (
            nom_agence,
            stats
        ) in enumerate(
            classement,
            start=1
        ):

            if position == 1:
                prefixe = "🥇"

            elif position == 2:
                prefixe = "🥈"

            elif position == 3:
                prefixe = "🥉"

            else:
                prefixe = f"{position}."

            st.write(
                f"**{prefixe} {nom_agence}** — "
                f"{stats['recrutements']} recrutement(s) · "
                f"{stats['candidatures']} candidature(s) · "
                f"{stats['postes']} poste(s)"
            )

        st.markdown("---")

        # ----------------------------------------------------
        # GRAPHIQUES
        # ----------------------------------------------------

        st.subheader(
            "📈 Activité par agence"
        )

        st.write(
            "Nombre de candidatures"
        )

        graphique_candidatures = {
            agence_nom: stats["candidatures"]
            for agence_nom, stats in stats_dz.items()
        }

        st.bar_chart(
            graphique_candidatures,
            color="#00A878",
        )

        st.write(
            "Nombre de recrutements"
        )

        graphique_recrutements = {
            agence_nom: stats["recrutements"]
            for agence_nom, stats in stats_dz.items()
        }

        st.bar_chart(
            graphique_recrutements,
            color="#00A878",
        )

        st.write(
            "Nombre de CV enregistrés"
        )

        graphique_cv = {
            agence_nom: stats["cv"]
            for agence_nom, stats in stats_dz.items()
        }

        st.bar_chart(
            graphique_cv,
            color="#00A878",
        )


# ============================================================
# IMPORT CV
# ============================================================

elif page == "📄 Importer un CV":

    st.title(
        "📄 Importer un CV"
    )

    fichier = st.file_uploader(
        "Sélectionnez un CV (PDF ou Word)",
        type=["pdf", "docx"],
    )

    if fichier is not None:

        texte = extract_text(
            fichier
        )

        if not texte:

            st.error(
                "Impossible d'extraire le texte de ce fichier "
                "(document scanné ou vide ?)."
            )

        else:

            candidat_detecte = extraire_candidat(
                fichier.name
            )

            metier_detecte = detecter_metier(
                texte
            )

            competences_detectees = extraire_competences(
                texte
            )

            taches_detectees = ", ".join(
                extraire_taches(
                    texte
                )
            )

            caces_detectes = extraire_caces(
                texte
            )

            permis_detectes = extraire_permis(
                texte
            )

            st.success(
                "CV analysé avec succès. "
                "Vérifiez les informations avant d'enregistrer."
            )

            with st.form("form_cv"):

                candidat = st.text_input(
                    "Nom du candidat",
                    value=candidat_detecte,
                )

                metier = st.text_input(
                    "Métier détecté",
                    value=metier_detecte,
                )

                metiers_recherches = st.text_input(
                    "Métiers recherchés / métiers pressentis",
                    value="",
                    help=(
                        "Indiquez un ou plusieurs métiers que le candidat "
                        "souhaite exercer, séparés par des virgules."
                    ),
                )

                date_fin_mission = st.date_input(
                    "📅 Fin de mission",
                    value=None,
                )

                date_disponibilite = st.date_input(
                    "📅 Date de disponibilité",
                    value=None,
                )

                competences = st.text_area(
                    "Compétences détectées",
                    value=competences_detectees,
                )

                taches = st.text_area(
                    "Tâches / missions déjà réalisées",
                    value=taches_detectees,
                    help=(
                        "Détectées automatiquement dans le CV. "
                        "Vous pouvez corriger ou compléter."
                    ),
                )

                caces = st.text_input(
                    "CACES détectés",
                    value=caces_detectes,
                )

                permis = st.text_input(
                    "Permis détectés",
                    value=permis_detectes,
                )

                type_profil = st.radio(
                    "Type de profil",
                    [
                        "🟢 Intérimaire",
                        "🟡 Candidat",
                    ],
                    horizontal=True,
                )

                valider = st.form_submit_button(
                    "Enregistrer ce CV"
                )

            if valider:

                try:

                    enregistrer_cv(
                        agence,
                        fichier.name,
                        candidat,
                        metier,
                        competences,
                        caces,
                        permis,
                        type_profil,
                        texte,
                        taches,
                        metiers_recherches,
                        date_fin_mission.isoformat() if date_fin_mission else None,
                        date_disponibilite.isoformat() if date_disponibilite else None,
                    )

                    st.success(
                        f"CV de {candidat} enregistré "
                        f"pour {agence}."
                    )

                    st.rerun()

                except Exception as erreur:

                    st.error(
                        "Erreur lors de l'enregistrement "
                        "du CV dans Supabase."
                    )

                    st.exception(erreur)

            with st.expander(
                "Voir le texte extrait du CV"
            ):

                st.text(
                    texte
                )


# ============================================================
# CVTHEQUE
# ============================================================

elif page == "📂 CVthèque":

    st.title(
        "📚 CVthèque"
    )

    recherche = st.text_input(
        "🔎 Rechercher un candidat, une compétence..."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        filtre_metier = st.text_input(
            "👷 Métier"
        )

    with col2:

        filtre_caces = st.text_input(
            "🚜 CACES"
        )

    with col3:

        filtre_permis = st.text_input(
            "🚗 Permis"
        )

    cvs = lister_cv(
        agence
    )

    if not cvs:

        st.info(
            "Aucun CV enregistré pour cette agence."
        )

    else:

        for cv in cvs:

            cv_id = cv.get("id")
            candidat = cv.get("candidat") or ""
            metier = cv.get("metier") or ""
            competences = cv.get("competences") or ""
            taches = cv.get("taches") or ""
            caces = cv.get("caces") or ""
            permis = cv.get("permis") or ""
            type_profil = cv.get("type_profil") or ""
            date_creation = cv.get("date_creation") or ""
            texte = cv.get("texte") or ""
            metiers_recherches = cv.get("metiers_recherches") or ""
            date_fin_mission = cv.get("date_fin_mission") or ""
            date_disponibilite = cv.get("date_disponibilite") or ""

            texte_recherche = (
                f"{candidat} "
                f"{metier} "
                f"{competences} "
                f"{caces} "
                f"{permis} "
                f"{texte}"
            ).lower()

            if (
                recherche
                and recherche.lower()
                not in texte_recherche
            ):
                continue

            if (
                filtre_metier
                and filtre_metier.lower()
                not in metier.lower()
            ):
                continue

            if (
                filtre_caces
                and filtre_caces.lower()
                not in caces.lower()
            ):
                continue

            if (
                filtre_permis
                and filtre_permis.lower()
                not in permis.lower()
            ):
                continue

            with st.expander(
                f"👤 {candidat} - {metier}"
            ):

                st.write(
                    f"**Métier :** {metier}"
                )

                st.write(
                    f"**Métiers recherchés / pressentis :** "
                    f"{metiers_recherches if metiers_recherches else 'Non renseigné'}"
                )

                st.write(
                    f"**Fin de mission :** "
                    f"{date_fin_mission if date_fin_mission else 'Non renseignée'}"
                )

                st.write(
                    f"**Disponibilité :** "
                    f"{date_disponibilite if date_disponibilite else 'Non renseignée'}"
                )

                st.write(
                    f"**Compétences :** {competences}"
                )

                st.write(
                    f"**Tâches déjà réalisées :** "
                    f"{taches if taches else 'Non renseigné'}"
                )

                st.write(
                    f"**CACES :** "
                    f"{caces if caces else 'Aucun'}"
                )

                st.write(
                    f"**Permis :** "
                    f"{permis if permis else 'Non renseigné'}"
                )

                if type_profil == "🟢 Intérimaire":

                    st.write(
                        "**Type de profil :** "
                        "🟢 Intérimaire"
                    )

                else:

                    st.write(
                        "**Type de profil :** "
                        "🟡 Candidat"
                    )

                st.caption(
                    f"Ajouté le {date_creation}"
                )

                if texte:

                    with st.expander(
                        "Voir le texte complet du CV"
                    ):

                        st.text(
                            texte
                        )

                st.markdown("---")

                if st.button(
                    "🗑️ Supprimer ce CV",
                    key=f"suppr_cv_{cv_id}",
                ):

                    try:

                        supprimer_cv(
                            cv_id
                        )

                        st.success(
                            "CV supprimé."
                        )

                        st.rerun()

                    except Exception as erreur:

                        st.error(
                            "Erreur lors de la suppression du CV."
                        )

                        st.exception(erreur)


# ============================================================
# IMPORT FICHE DE POSTE
# ============================================================

elif page == "🏢 Importer une fiche de poste":

    st.title(
        "🏢 Importer une fiche de poste"
    )

    fichier = st.file_uploader(
        "Sélectionnez une fiche de poste (PDF ou Word)",
        type=["pdf", "docx"],
    )

    if fichier is not None:

        texte = extract_text(
            fichier
        )

        if not texte:

            st.error(
                "Impossible d'extraire le texte de cette fiche "
                "de poste (document scanné ou vide ?)."
            )

        else:

            # =================================================
            # LECTURE CIBLÉE
            # =================================================

            fiche_ciblee = extraire_fiche_poste_ciblee(
                texte
            )
            
            entreprise_detectee = (
                fiche_ciblee.get("entreprise") or ""
            )

            poste_detecte_cible = (
                fiche_ciblee.get("poste") or ""
            )

            taches_detectees_ciblees = (
                fiche_ciblee.get("taches") or ""
            )

            entreprise_trouvee = (
                fiche_ciblee.get(
                    "entreprise_trouvee"
                )
            )

            poste_trouve = (
                fiche_ciblee.get(
                    "poste_trouve"
                )
            )

            taches_trouvees = (
                fiche_ciblee.get(
                    "taches_trouvees"
                )
            )

            # =================================================
            # AUTRES INFORMATIONS
            # =================================================

            competences_detectees = ""

            caces_detectes = extraire_caces(
                texte
            )

            permis_detectes = extraire_permis(
                texte
            )

            vip_sir_detecte = detecter_vip_sir(
                texte
            )

            # =================================================
            # MESSAGE
            # =================================================

            if (
                not entreprise_trouvee
                or not poste_trouve
                or not taches_trouvees
            ):

                st.warning(
                    "Certaines rubriques n'ont pas été détectées "
                    "automatiquement. L'application ne va pas "
                    "inventer de valeur."
                )

            if not entreprise_trouvee:

                st.warning(
                    "⚠️ La rubrique "
                    "« Nom de l'entreprise » "
                    "n'a pas été trouvée."
                )

            if not poste_trouve:

                st.warning(
                    "⚠️ La rubrique "
                    "« Intitulé du poste » "
                    "n'a pas été trouvée."
                )

            if not taches_trouvees:

                st.warning(
                    "⚠️ La rubrique "
                    "« Liste des tâches proposées » "
                    "n'a pas été trouvée."
                )

            st.success(
                "Lecture ciblée terminée. "
                "Vérifiez les informations avant d'enregistrer."
            )

            # =================================================
            # FORMULAIRE
            # =================================================

            with st.form("form_poste"):

                entreprise = st.text_input(
                    "Entreprise cliente",
                    value=entreprise_detectee,
                )

                poste = st.text_input(
                    "Intitulé du poste",
                    value=poste_detecte_cible,
                )

                competences = st.text_area(
                    "Compétences requises",
                    value=competences_detectees,
                )

                taches = st.text_area(
                    "Tâches à réaliser",
                    value=taches_detectees_ciblees,
                    help=(
                        "Copiées automatiquement depuis la rubrique "
                        "« Liste des tâches proposées »."
                    ),
                )

                caces = st.text_input(
                    "CACES requis",
                    value=caces_detectes,
                )

                permis = st.text_input(
                    "Permis requis",
                    value=permis_detectes,
                )

                options_vip = [
                    "",
                    "VIP",
                    "SIR",
                    "VIP + SIR",
                ]

                vip_sir = st.selectbox(
                    "Suivi médical requis",
                    options_vip,
                    index=(
                        options_vip.index(
                            vip_sir_detecte
                        )
                        if vip_sir_detecte in options_vip
                        else 0
                    ),
                    help=(
                        "VIP = Visite Infirmier Périodique. "
                        "SIR = Suivi Individuel Renforcé."
                    ),
                )

                valider = st.form_submit_button(
                    "Enregistrer cette fiche de poste"
                )

            # =================================================
            # ENREGISTREMENT
            # =================================================

            if valider:

                if not entreprise or not poste:

                    st.error(
                        "Merci de renseigner au moins "
                        "l'entreprise et l'intitulé du poste."
                    )

                else:

                    try:

                        enregistrer_poste(
                            agence,
                            entreprise,
                            poste,
                            competences,
                            caces,
                            permis,
                            texte,
                            taches,
                            vip_sir,
                        )

                        st.success(
                            f"Fiche de poste « {poste} » "
                            f"enregistrée pour {entreprise}."
                        )

                        st.rerun()

                    except Exception as erreur:

                        st.error(
                            "Erreur lors de l'enregistrement "
                            "de la fiche de poste."
                        )

                        st.exception(erreur)

            with st.expander(
                "Voir le texte extrait de la fiche de poste"
            ):

                st.text(
                    texte
                )


# ============================================================
# POSTETHEQUE
# ============================================================

elif page == "📁 Postethèque":

    st.title(
        "📁 Postethèque"
    )

    recherche_poste = st.text_input(
        "🔎 Rechercher une entreprise, un poste, "
        "une compétence..."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        filtre_poste_intitule = st.text_input(
            "💼 Intitulé du poste"
        )

    with col2:

        filtre_poste_caces = st.text_input(
            "🚜 CACES"
        )

    with col3:

        filtre_poste_permis = st.text_input(
            "🚗 Permis"
        )

    postes_liste = recuperer_postes(
        agence
    )

    if not postes_liste:

        st.info(
            "Aucune fiche de poste enregistrée "
            "pour cette agence."
        )

    else:

        for poste_item in postes_liste:

            poste_id = poste_item.get("id")
            entreprise = poste_item.get("entreprise") or ""
            intitule = poste_item.get("poste") or ""
            competences = poste_item.get("competences") or ""
            taches = poste_item.get("taches") or ""
            vip_sir = poste_item.get("vip_sir") or ""
            caces = poste_item.get("caces") or ""
            permis = poste_item.get("permis") or ""
            date_creation = (
                poste_item.get("date_creation") or ""
            )
            texte_poste = poste_item.get("texte") or ""

            texte_recherche_poste = (
                f"{entreprise} "
                f"{intitule} "
                f"{competences} "
                f"{caces} "
                f"{permis} "
                f"{texte_poste}"
            ).lower()

            if (
                recherche_poste
                and recherche_poste.lower()
                not in texte_recherche_poste
            ):
                continue

            if (
                filtre_poste_intitule
                and filtre_poste_intitule.lower()
                not in intitule.lower()
            ):
                continue

            if (
                filtre_poste_caces
                and filtre_poste_caces.lower()
                not in caces.lower()
            ):
                continue

            if (
                filtre_poste_permis
                and filtre_poste_permis.lower()
                not in permis.lower()
            ):
                continue

            with st.expander(
                f"🏢 {entreprise} — {intitule}"
            ):

                st.write(
                    f"**Entreprise :** {entreprise}"
                )

                st.write(
                    f"**Intitulé du poste :** {intitule}"
                )

                st.write(
                    f"**Compétences requises :** "
                    f"{competences if competences else 'Non renseigné'}"
                )

                st.write(
                    f"**Tâches à réaliser :** "
                    f"{taches if taches else 'Non renseigné'}"
                )

                st.write(
                    f"**CACES requis :** "
                    f"{caces if caces else 'Aucun'}"
                )

                st.write(
                    f"**Permis requis :** "
                    f"{permis if permis else 'Non renseigné'}"
                )

                st.write(
                    f"**Suivi médical :** "
                    f"{vip_sir if vip_sir else 'Non renseigné'}"
                )

                st.caption(
                    f"Ajouté le {date_creation}"
                )

                if texte_poste:

                    with st.expander(
                        "Voir le texte complet de la fiche de poste"
                    ):

                        st.text(
                            texte_poste
                        )

                st.markdown("---")

                if st.button(
                    "🗑️ Supprimer cette fiche de poste",
                    key=f"suppr_poste_{poste_id}",
                ):

                    try:

                        supprimer_poste(
                            poste_id
                        )

                        st.success(
                            "Fiche de poste supprimée."
                        )

                        st.rerun()

                    except Exception as erreur:

                        st.error(
                            "Erreur lors de la suppression "
                            "de la fiche de poste."
                        )

                        st.exception(erreur)


# ============================================================
# MATCHING
# ============================================================

elif page == "🔍 Matching":

    st.title(
        "🔍 Matching CV / Fiches de poste"
    )

    postes = recuperer_postes(
        agence
    )

    cvs = recuperer_cvs_matching(
        agence
    )

    if not postes:

        st.info(
            "Aucune fiche de poste enregistrée "
            "pour cette agence."
        )

    elif not cvs:

        st.info(
            "Aucun CV enregistré pour cette agence."
        )

    else:

        options_postes = {
            f"{p['poste']} — {p['entreprise']}": p["id"]
            for p in postes
        }

        choix_poste = st.selectbox(
            "Choisissez une fiche de poste",
            list(options_postes.keys()),
        )

        poste_id = options_postes[
            choix_poste
        ]

        poste = recuperer_poste(
            poste_id
        )

        if not poste:

            st.error(
                "Impossible de récupérer cette fiche de poste."
            )

        else:

            poste_nom = poste.get(
                "poste"
            ) or ""

            entreprise_nom = poste.get(
                "entreprise"
            ) or ""

            resultats = []

            for cv in cvs:

                resultat_matching = calculer_score(
                    cv,
                    poste,
                )

                resultats.append(
                    {
                        "cv_id": cv.get("id"),
                        "candidat": cv.get("candidat") or "",
                        "metier": resultat_matching[
                            "metier_cv"
                        ],
                        "score": resultat_matching[
                            "score"
                        ],
                        "explication": resultat_matching[
                            "explication"
                        ],
                    }
                )

            resultats.sort(
                key=lambda r: r["score"],
                reverse=True,
            )

            st.subheader(
                f"Résultats pour : "
                f"{poste_nom} — {entreprise_nom}"
            )

            for r in resultats:

                with st.expander(
                    f"{r['candidat']} — "
                    f"{r['score']}% de compatibilité "
                    f"({r['metier']})"
                ):

                    st.progress(
                        min(
                            r["score"],
                            100
                        ) / 100
                    )

                    for ligne_explication in (
                        r["explication"]
                    ):

                        st.write(
                            ligne_explication
                        )

                    st.markdown("---")

                    statut = st.selectbox(
                        "Statut de la candidature",
                        STATUTS_SUIVI,
                        key=f"statut_{r['cv_id']}",
                    )

                    type_entreprise = st.radio(
                        "Type d'entreprise",
                        [
                            "🟢 Client",
                            "🟠 Prospect",
                        ],
                        horizontal=True,
                        key=(
                            f"type_entreprise_"
                            f"{r['cv_id']}"
                        ),
                    )

                    if st.button(
                        "Ajouter au suivi",
                        key=f"suivi_{r['cv_id']}",
                    ):

                        try:

                            enregistrer_suivi(
                                agence,
                                r["candidat"],
                                entreprise_nom,
                                poste_nom,
                                statut,
                                type_entreprise,
                            )

                            st.success(
                                "Candidature ajoutée au suivi."
                            )

                            st.rerun()

                        except Exception as erreur:

                            st.error(
                                "Erreur lors de l'ajout "
                                "au suivi."
                            )

                            st.exception(erreur)

                    st.markdown("---")

                    if st.button(
                        "📧 Générer une présentation",
                        key=(
                            f"presentation_"
                            f"{r['cv_id']}"
                        ),
                    ):

                        cv_complet = recuperer_cv(
                            r["cv_id"]
                        )

                        if cv_complet:

                            candidat = (
                                cv_complet.get(
                                    "candidat"
                                )
                                or ""
                            )

                            metier = (
                                cv_complet.get(
                                    "metier"
                                )
                                or ""
                            )

                            competences = (
                                cv_complet.get(
                                    "competences"
                                )
                                or ""
                            )

                            caces = (
                                cv_complet.get(
                                    "caces"
                                )
                                or ""
                            )

                            permis = (
                                cv_complet.get(
                                    "permis"
                                )
                                or ""
                            )

                            texte = generer_presentation(
                                candidat,
                                metier,
                                competences,
                                caces,
                                permis,
                                entreprise_nom,
                                agence,
                            )

                            st.text_area(
                                "Présentation prête à copier",
                                value=texte,
                                height=300,
                                key=(
                                    f"texte_"
                                    f"{r['cv_id']}"
                                ),
                            )


# ============================================================
# SUIVI DES CANDIDATURES
# ============================================================

elif page == "📋 Suivi des candidatures":

    st.title(
        "📋 Suivi des candidatures"
    )

    lignes = lister_suivi(
        agence
    )

    if not lignes:

        st.info(
            "Aucune candidature suivie pour le moment."
        )

    else:

        for ligne in lignes:

            suivi_id = ligne.get("id")
            candidat = ligne.get("candidat") or ""
            entreprise = ligne.get("entreprise") or ""
            poste = ligne.get("poste") or ""
            statut = ligne.get("statut") or ""
            type_entreprise = (
                ligne.get("type_entreprise") or ""
            )
            date_creation = (
                ligne.get("date_creation") or ""
            )

            col1, col2 = st.columns(
                [4, 2]
            )

            with col1:

                st.write(
                    f"**{candidat}** → "
                    f"{poste} chez {entreprise}"
                )

                if type_entreprise == "🟢 Client":

                    st.caption(
                        "🟢 Client"
                    )

                elif type_entreprise == "🟠 Prospect":

                    st.caption(
                        "🟠 Prospect"
                    )

                st.caption(
                    f"Ajouté le {date_creation}"
                )

            with col2:

                nouveau_statut = st.selectbox(
                    "Statut",
                    STATUTS_SUIVI,
                    index=(
                        STATUTS_SUIVI.index(
                            statut
                        )
                        if statut in STATUTS_SUIVI
                        else 0
                    ),
                    key=f"maj_statut_{suivi_id}",
                    label_visibility="collapsed",
                )

                if nouveau_statut != statut:

                    try:

                        modifier_statut_suivi(
                            suivi_id,
                            nouveau_statut,
                        )

                        st.rerun()

                    except Exception as erreur:

                        st.error(
                            "Erreur lors de la modification "
                            "du statut."
                        )

                        st.exception(erreur)


# ============================================================
# STATISTIQUES
# ============================================================

elif page == "📈 Statistiques":

    st.title(
        "📈 Statistiques de l'agence"
    )

    st.subheader(
        "Activité par semaine"
    )

    stats = statistiques_par_semaine(
        agence
    )

    if not stats:

        st.info(
            "Aucune donnée disponible."
        )

    else:

        for semaine, nb in stats:

            st.write(
                f"📅 **{semaine}** : "
                f"{nb} candidature(s)"
            )

            st.markdown("---")
