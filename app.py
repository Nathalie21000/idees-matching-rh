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
    statistiques_hebdomadaires,
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
# STYLE
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

    .stApp {
        background-color: var(--idees-grey);
    }

    section[data-testid="stSidebar"] {
        background-color: var(--idees-anthracite);
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* --------------------------------------------------------
       LOGO DANS LA SIDEBAR
       -------------------------------------------------------- */

    section[data-testid="stSidebar"] div[data-testid="stImage"] {
        background-color: white;
        border-radius: 10px;
        padding: 12px;
        margin: 10px auto 18px auto;
    }

    section[data-testid="stSidebar"] div[data-testid="stImage"] img {
        border-radius: 4px;
    }

    .idees-title {
        color: var(--idees-green);
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .idees-subtitle {
        color: var(--idees-anthracite);
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background-color: var(--idees-white);
        border: 1px solid var(--idees-border);
        border-left: 5px solid var(--idees-green);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .metric-title {
        color: #6B7376;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .metric-value {
        color: var(--idees-anthracite);
        font-size: 2rem;
        font-weight: 800;
    }

    .section-card {
        background-color: var(--idees-white);
        border: 1px solid var(--idees-border);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    div.stButton > button {
        background-color: var(--idees-green);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background-color: var(--idees-green-dark);
        color: white;
    }

    .stProgress > div > div > div > div {
        background-color: var(--idees-green);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DONNÉES GÉNÉRALES
# ============================================================

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


# ============================================================
# INITIALISATION
# ============================================================

init_db()


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def afficher_metric(titre, valeur):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{titre}</div>
            <div class="metric-value">{valeur}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nettoyer_texte(texte):
    if not texte:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(texte)
    ).strip()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # VRAI LOGO ID'EES INTERIM
    # --------------------------------------------------------

    st.image(
        "logo.png",
        width=170,
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:-8px;
            margin-bottom:22px;
        ">
            <div style="
                font-size:17px;
                font-weight:800;
                color:white;
                letter-spacing:0.2px;
            ">
                ID'EES INTERIM
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    agence = st.selectbox(
        "Agence",
        AGENCES,
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Tableau de bord",
            "🌍 Tableau de bord DZ",
            "📄 Importer un CV",
            "📚 CVthèque",
            "💼 Importer une fiche de poste",
            "📋 Postethèque",
            "🎯 Matching",
            "📌 Suivi des candidatures",
            "📈 Statistiques",
        ],
    )


# ============================================================
# TABLEAU DE BORD AGENCE
# ============================================================

if page == "📊 Tableau de bord":

    st.markdown(
        '<div class="idees-title">📊 Tableau de bord</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="idees-subtitle">Agence de {agence}</div>',
        unsafe_allow_html=True,
    )

    cvs_dashboard = lister_cv(agence)
    suivis_dashboard = lister_suivi(agence)
    postes_dashboard = recuperer_postes(agence)

    nombre_cv = len(cvs_dashboard)
    nombre_postes = len(postes_dashboard)

    nombre_entretiens = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("statut") == "Entretien programmé"
    )

    nombre_recrutements = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("statut") == "Recruté"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        afficher_metric("CVthèque", nombre_cv)

    with col2:
        afficher_metric("Postes", nombre_postes)

    with col3:
        afficher_metric("Entretiens", nombre_entretiens)

    with col4:
        afficher_metric("Recrutements", nombre_recrutements)

    st.markdown("---")

    # --------------------------------------------------------
    # CLIENTS / PROSPECTS
    # --------------------------------------------------------

    st.subheader("Transformation Clients / Prospects")

    clients_envoyes = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("type_entreprise") == "🟢 Client"
        and ligne.get("statut") != "Commande non pourvue"
    )

    clients_recrutes = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("type_entreprise") == "🟢 Client"
        and ligne.get("statut") == "Recruté"
    )

    prospects_envoyes = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("type_entreprise") == "🟠 Prospect"
        and ligne.get("statut") != "Commande non pourvue"
    )

    prospects_recrutes = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("type_entreprise") == "🟠 Prospect"
        and ligne.get("statut") != "Commande non pourvue"
        and ligne.get("statut") == "Recruté"
    )

    taux_client = (
        clients_recrutes / clients_envoyes * 100
        if clients_envoyes
        else 0
    )

    taux_prospect = (
        prospects_recrutes / prospects_envoyes * 100
        if prospects_envoyes
        else 0
    )

    col1, col2 = st.columns(2)

    with col1:
        afficher_metric(
            "🟢 Taux de transformation Clients",
            f"{taux_client:.1f} %",
        )

    with col2:
        afficher_metric(
            "🟠 Taux de transformation Prospects",
            f"{taux_prospect:.1f} %",
        )

    # --------------------------------------------------------
    # PROFILS
    # --------------------------------------------------------

    st.subheader("Transformation par profil")

    profils_dashboard = {}

    for cv in cvs_dashboard:

        candidat = cv.get("candidat")
        type_profil = cv.get("type_profil")

        if not type_profil:
            continue

        profils_dashboard[candidat] = type_profil

    profil_envoyes = {
        "Intérimaire": 0,
        "Candidat": 0,
    }

    profil_recrutes = {
        "Intérimaire": 0,
        "Candidat": 0,
    }

    for ligne in suivis_dashboard:

        type_profil = ligne.get("type_profil")

        if type_profil not in profil_envoyes:
            continue

        if ligne.get("statut") != "Commande non pourvue":
            profil_envoyes[type_profil] += 1

        if ligne.get("statut") == "Recruté":
            profil_recrutes[type_profil] += 1

    col1, col2 = st.columns(2)

    for col, profil in [
        (col1, "Intérimaire"),
        (col2, "Candidat"),
    ]:

        taux = (
            profil_recrutes[profil]
            / profil_envoyes[profil]
            * 100
            if profil_envoyes[profil]
            else 0
        )

        with col:
            afficher_metric(
                profil,
                f"{taux:.1f} %",
            )

    # --------------------------------------------------------
    # COMMANDES NON POURVUES
    # --------------------------------------------------------

    non_pourvues = sum(
        1
        for ligne in suivis_dashboard
        if ligne.get("statut") == "Commande non pourvue"
    )

    total_candidatures = len(suivis_dashboard)

    poids_non_pourvues = (
        non_pourvues / total_candidatures * 100
        if total_candidatures
        else 0
    )

    st.subheader("Commandes non pourvues")

    col1, col2 = st.columns(2)

    with col1:
        afficher_metric(
            "Commandes non pourvues",
            non_pourvues,
        )

    with col2:
        afficher_metric(
            "Poids des non pourvues",
            f"{poids_non_pourvues:.1f} %",
        )

    # --------------------------------------------------------
    # MÉTIERS
    # --------------------------------------------------------

    st.subheader("Répartition des métiers")

    metiers = {}

    for cv in cvs_dashboard:

        metier = cv.get("metier")

        if metier:
            metiers[metier] = (
                metiers.get(metier, 0) + 1
            )

    if metiers:
        st.bar_chart(metiers)
    else:
        st.info("Aucun métier disponible.")

    # --------------------------------------------------------
    # MÉTIERS RECHERCHÉS
    # --------------------------------------------------------

    st.subheader("Métiers recherchés")

    metiers_recherches = {}

    for cv in cvs_dashboard:

        texte = cv.get("metiers_recherches")

        if not texte:
            continue

        for metier in str(texte).split(","):

            metier = metier.strip()

            if metier:
                metiers_recherches[metier] = (
                    metiers_recherches.get(metier, 0) + 1
                )

    if metiers_recherches:
        st.bar_chart(metiers_recherches)

    # --------------------------------------------------------
    # POSTES DEMANDÉS
    # --------------------------------------------------------

    st.subheader("Postes demandés")

    postes_demandes = {}

    for poste in postes_dashboard:

        nom_poste = poste.get("poste")

        if nom_poste:
            postes_demandes[nom_poste] = (
                postes_demandes.get(nom_poste, 0) + 1
            )

    if postes_demandes:
        st.bar_chart(postes_demandes)

    # --------------------------------------------------------
    # STATUTS
    # --------------------------------------------------------

    st.subheader("Répartition des candidatures")

    repartition = repartition_suivi(agence)

    if repartition:
        st.bar_chart(repartition)
    else:
        st.info("Aucune candidature enregistrée.")


# ============================================================
# TABLEAU DE BORD DZ
# ============================================================

elif page == "🌍 Tableau de bord DZ":

    st.markdown(
        '<div class="idees-title">🌍 Tableau de bord DZ</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="idees-subtitle">Vue régionale</div>',
        unsafe_allow_html=True,
    )

    stats_dz = statistiques_dz(AGENCES)

    total_cv = sum(
        ligne["cv"]
        for ligne in stats_dz.values()
    )

    total_postes = sum(
        ligne["postes"]
        for ligne in stats_dz.values()
    )

    total_candidatures = sum(
        ligne["candidatures"]
        for ligne in stats_dz.values()
    )

    total_entretiens = sum(
        ligne["entretiens"]
        for ligne in stats_dz.values()
    )

    total_recrutements = sum(
        ligne["recrutements"]
        for ligne in stats_dz.values()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        afficher_metric("CV", total_cv)

    with col2:
        afficher_metric("Postes", total_postes)

    with col3:
        afficher_metric("Candidatures", total_candidatures)

    with col4:
        afficher_metric("Entretiens", total_entretiens)

    with col5:
        afficher_metric("Recrutements", total_recrutements)

    st.markdown("---")

    st.subheader("Performance par agence")

    tableau_dz = []

    for nom_agence, data in stats_dz.items():

        candidatures = data["candidatures"]

        suivis_agence = lister_suivi(nom_agence)

        candidatures_eligibles = sum(
            1
            for ligne in suivis_agence
            if ligne.get("statut") != "Commande non pourvue"
        )

        recrutements = data["recrutements"]

        taux_transformation = (
            recrutements
            / candidatures_eligibles
            * 100
            if candidatures_eligibles
            else 0
        )

        tableau_dz.append(
            {
                "Agence": nom_agence,
                "CV": data["cv"],
                "Postes": data["postes"],
                "Candidatures": candidatures,
                "Entretiens": data["entretiens"],
                "Recrutements": recrutements,
                "Clients": data["clients"],
                "Prospects": data["prospects"],
                "Transformation": f"{taux_transformation:.1f} %",
            }
        )

    tableau_dz = sorted(
        tableau_dz,
        key=lambda x: (
            x["Recrutements"],
            x["Candidatures"],
            x["Postes"],
        ),
        reverse=True,
    )

    st.dataframe(
        tableau_dz,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Candidatures par agence")

    candidatures_chart = {
        agence_nom: data["candidatures"]
        for agence_nom, data in stats_dz.items()
    }

    st.bar_chart(candidatures_chart)

    st.subheader("Recrutements par agence")

    recrutements_chart = {
        agence_nom: data["recrutements"]
        for agence_nom, data in stats_dz.items()
    }

    st.bar_chart(recrutements_chart)

    st.subheader("CV par agence")

    cv_chart = {
        agence_nom: data["cv"]
        for agence_nom, data in stats_dz.items()
    }

    st.bar_chart(cv_chart)

    st.subheader("Classement")

    classement = sorted(
        tableau_dz,
        key=lambda x: x["Recrutements"],
        reverse=True,
    )

    for index, ligne in enumerate(
        classement,
        start=1,
    ):

        st.write(
            f"**{index}. {ligne['Agence']}** — "
            f"{ligne['Recrutements']} recrutement(s)"
        )


# ============================================================
# IMPORTER UN CV
# ============================================================

elif page == "📄 Importer un CV":

    st.markdown(
        '<div class="idees-title">📄 Importer un CV</div>',
        unsafe_allow_html=True,
    )

    fichier = st.file_uploader(
        "Déposer un CV",
        type=[
            "pdf",
            "docx",
            "txt",
        ],
    )

    if fichier:

        if st.button("Analyser le CV"):

            with st.spinner("Analyse du CV en cours..."):

                texte = extract_text(fichier)

                texte = nettoyer_texte(texte)

                metier = detecter_metier(texte)

                competences = extraire_competences_pro(
                    texte
                )

                taches = extraire_taches(
                    texte
                )

            st.success("CV analysé.")

            candidat = st.text_input(
                "Nom du candidat",
            )

            type_profil = st.radio(
                "Type de profil",
                [
                    "🟢 Intérimaire",
                    "🟡 Candidat",
                ],
                horizontal=True,
            )

            metiers_recherches = st.text_input(
                "Métiers recherchés",
            )

            col1, col2 = st.columns(2)

            with col1:
                date_fin_mission = st.date_input(
                    "Date de fin de mission",
                    value=None,
                )

            with col2:
                date_disponibilite = st.date_input(
                    "Date de disponibilité",
                    value=None,
                )

            caces = st.text_input(
                "CACES",
            )

            permis = st.text_input(
                "Permis",
            )

            if st.button(
                "💾 Enregistrer le CV"
            ):

                type_profil_stockage = (
                    "Intérimaire"
                    if "Intérimaire" in type_profil
                    else "Candidat"
                )

                enregistrer_cv(
                    agence=agence,
                    nom_fichier=fichier.name,
                    candidat=candidat,
                    metier=metier,
                    competences=competences,
                    caces=caces,
                    permis=permis,
                    type_profil=type_profil_stockage,
                    texte=texte,
                    taches=taches,
                    metiers_recherches=metiers_recherches,
                    date_fin_mission=(
                        str(date_fin_mission)
                        if date_fin_mission
                        else None
                    ),
                    date_disponibilite=(
                        str(date_disponibilite)
                        if date_disponibilite
                        else None
                    ),
                )

                st.success(
                    "CV enregistré dans la CVthèque."
                )


# ============================================================
# CVTHÈQUE
# ============================================================

elif page == "📚 CVthèque":

    st.markdown(
        '<div class="idees-title">📚 CVthèque</div>',
        unsafe_allow_html=True,
    )

    cvs = lister_cv(agence)

    recherche = st.text_input(
        "🔎 Rechercher un candidat, métier ou compétence"
    )

    if recherche:

        recherche_lower = recherche.lower()

        cvs = [
            cv
            for cv in cvs
            if recherche_lower in str(
                cv.get("candidat", "")
            ).lower()
            or recherche_lower in str(
                cv.get("metier", "")
            ).lower()
            or recherche_lower in str(
                cv.get("competences", "")
            ).lower()
        ]

    if not cvs:

        st.info(
            "Aucun CV disponible."
        )

    for cv in cvs:

        with st.container():

            st.markdown(
                "---"
            )

            col1, col2, col3 = st.columns(
                [4, 2, 1]
            )

            with col1:

                st.subheader(
                    cv.get("candidat")
                    or "Candidat sans nom"
                )

                st.write(
                    f"**Métier :** "
                    f"{cv.get('metier', '')}"
                )

                st.write(
                    f"**Type de profil :** "
                    f"{cv.get('type_profil', '')}"
                )

                st.write(
                    f"**Métiers recherchés :** "
                    f"{cv.get('metiers_recherches', '')}"
                )

                st.write(
                    f"**Compétences :** "
                    f"{cv.get('competences', '')}"
                )

                st.write(
                    f"**Tâches :** "
                    f"{cv.get('taches', '')}"
                )

                st.write(
                    f"**CACES :** "
                    f"{cv.get('caces', '')}"
                )

                st.write(
                    f"**Permis :** "
                    f"{cv.get('permis', '')}"
                )

                st.write(
                    f"**Fin de mission :** "
                    f"{cv.get('date_fin_mission', '')}"
                )

                st.write(
                    f"**Disponibilité :** "
                    f"{cv.get('date_disponibilite', '')}"
                )

            with col2:

                if cv.get("texte"):

                    with st.expander(
                        "Voir le CV"
                    ):

                        st.write(
                            cv.get("texte")
                        )

            with col3:

                if st.button(
                    "🗑️ Supprimer",
                    key=f"supprimer_cv_{cv['id']}",
                ):

                    supprimer_cv(
                        cv["id"]
                    )

                    st.rerun()


# ============================================================
# IMPORTER UNE FICHE DE POSTE
# ============================================================

elif page == "💼 Importer une fiche de poste":

    st.markdown(
        '<div class="idees-title">💼 Importer une fiche de poste</div>',
        unsafe_allow_html=True,
    )

    fichier = st.file_uploader(
        "Déposer une fiche de poste",
        type=[
            "pdf",
            "docx",
            "txt",
        ],
    )

    if fichier:

        if st.button("Analyser la fiche de poste"):

            with st.spinner(
                "Analyse de la fiche de poste..."
            ):

                texte = extract_text(
                    fichier
                )

                texte = nettoyer_texte(
                    texte
                )

                donnees = (
                    extraire_fiche_poste_ciblee(
                        texte
                    )
                )

                entreprise = donnees.get(
                    "entreprise",
                    "",
                )

                poste = donnees.get(
                    "poste",
                    "",
                )

                competences = donnees.get(
                    "competences",
                    "",
                )

                taches = donnees.get(
                    "taches",
                    "",
                )

                caces = donnees.get(
                    "caces",
                    "",
                )

                permis = donnees.get(
                    "permis",
                    "",
                )

                vip_sir = detecter_vip_sir(
                    texte
                )

            st.success(
                "Fiche de poste analysée."
            )

            entreprise = st.text_input(
                "Entreprise",
                value=entreprise,
            )

            poste = st.text_input(
                "Poste",
                value=poste,
            )

            competences = st.text_area(
                "Compétences",
                value=competences,
            )

            taches = st.text_area(
                "Tâches",
                value=taches,
            )

            caces = st.text_input(
                "CACES",
                value=caces,
            )

            permis = st.text_input(
                "Permis",
                value=permis,
            )

            vip_sir = st.text_input(
                "VIP / SIR",
                value=vip_sir,
            )

            if st.button(
                "💾 Enregistrer la fiche de poste"
            ):

                enregistrer_poste(
                    agence=agence,
                    entreprise=entreprise,
                    poste=poste,
                    competences=competences,
                    caces=caces,
                    permis=permis,
                    texte=texte,
                    taches=taches,
                    vip_sir=vip_sir,
                )

                st.success(
                    "Fiche de poste enregistrée."
                )


# ============================================================
# POSTETHÈQUE
# ============================================================

elif page == "📋 Postethèque":

    st.markdown(
        '<div class="idees-title">📋 Postethèque</div>',
        unsafe_allow_html=True,
    )

    postes = recuperer_postes(
        agence
    )

    if not postes:

        st.info(
            "Aucune fiche de poste disponible."
        )

    for poste in postes:

        with st.container():

            st.markdown("---")

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                st.subheader(
                    poste.get(
                        "poste",
                        "Poste",
                    )
                )

                st.write(
                    f"**Entreprise :** "
                    f"{poste.get('entreprise', '')}"
                )

                st.write(
                    f"**Compétences :** "
                    f"{poste.get('competences', '')}"
                )

                st.write(
                    f"**Tâches :** "
                    f"{poste.get('taches', '')}"
                )

                st.write(
                    f"**CACES :** "
                    f"{poste.get('caces', '')}"
                )

                st.write(
                    f"**Permis :** "
                    f"{poste.get('permis', '')}"
                )

                st.write(
                    f"**VIP / SIR :** "
                    f"{poste.get('vip_sir', '')}"
                )

                with st.expander(
                    "Voir la fiche complète"
                ):

                    st.write(
                        poste.get(
                            "texte",
                            "",
                        )
                    )

            with col2:

                if st.button(
                    "🗑️ Supprimer",
                    key=f"supprimer_poste_{poste['id']}",
                ):

                    supprimer_poste(
                        poste["id"]
                    )

                    st.rerun()


# ============================================================
# MATCHING
# ============================================================

elif page == "🎯 Matching":

    st.markdown(
        '<div class="idees-title">🎯 Matching</div>',
        unsafe_allow_html=True,
    )

    postes = recuperer_postes(
        agence
    )

    if not postes:

        st.info(
            "Aucun poste disponible."
        )

    else:

        poste_options = {
            f"{p.get('entreprise', '')} - "
            f"{p.get('poste', '')}": p["id"]
            for p in postes
        }

        poste_selection = st.selectbox(
            "Choisir une fiche de poste",
            list(poste_options.keys()),
        )

        poste_id = poste_options[
            poste_selection
        ]

        poste = recuperer_poste(
            poste_id
        )

        cvs = recuperer_cvs_matching(
            agence
        )

        resultats_matching = []

        for cv in cvs:

            score = calculer_score(
                cv,
                poste,
            )

            resultats_matching.append(
                {
                    "cv_id": cv["id"],
                    "candidat": cv.get(
                        "candidat",
                        "",
                    ),
                    "metier": cv.get(
                        "metier",
                        "",
                    ),
                    "type_profil": cv.get(
                        "type_profil",
                        "",
                    ),
                    "score": score,
                }
            )

        resultats_matching.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        for r in resultats_matching:

            with st.container():

                st.markdown("---")

                col1, col2, col3 = st.columns(
                    [4, 2, 2]
                )

                with col1:

                    st.subheader(
                        r["candidat"]
                    )

                    st.write(
                        f"**Métier :** "
                        f"{r['metier']}"
                    )

                    st.write(
                        f"**Profil :** "
                        f"{r['type_profil']}"
                    )

                with col2:

                    st.metric(
                        "Score",
                        f"{r['score']} %",
                    )

                with col3:

                    statut = st.selectbox(
                        "Statut",
                        STATUTS_SUIVI,
                        key=f"statut_{r['cv_id']}",
                    )

                    type_entreprise = st.radio(
                        "Type d'entreprise",
                        [
                            "🟢 Client",
                            "🟠 Prospect",
                        ],
                        key=f"type_entreprise_{r['cv_id']}",
                        horizontal=True,
                    )

                    if st.button(
                        "➕ Ajouter au suivi",
                        key=f"ajouter_{r['cv_id']}",
                    ):

                        entreprise_nom = poste.get(
                            "entreprise",
                            "",
                        )

                        poste_nom = poste.get(
                            "poste",
                            "",
                        )

                        cv_complet = recuperer_cv(
                            r["cv_id"]
                        )

                        type_profil = (
                            cv_complet.get(
                                "type_profil"
                            )
                            if cv_complet
                            else ""
                        )

                        enregistrer_suivi(
                            agence,
                            r["candidat"],
                            entreprise_nom,
                            poste_nom,
                            statut,
                            type_entreprise,
                            type_profil,
                        )

                        st.success(
                            "Candidature ajoutée au suivi."
                        )

                        presentation = generer_presentation(
                            cv_complet,
                            poste,
                        )

                        if presentation:

                            st.markdown(
                                "### Présentation candidat"
                            )

                            st.write(
                                presentation
                            )


# ============================================================
# SUIVI DES CANDIDATURES
# ============================================================

elif page == "📌 Suivi des candidatures":

    st.markdown(
        '<div class="idees-title">📌 Suivi des candidatures</div>',
        unsafe_allow_html=True,
    )

    suivis = lister_suivi(
        agence
    )

    if not suivis:

        st.info(
            "Aucune candidature enregistrée."
        )

    for ligne in suivis:

        st.markdown("---")

        col1, col2, col3, col4 = st.columns(
            [3, 3, 2, 2]
        )

        with col1:

            st.write(
                f"**Candidat :** "
                f"{ligne.get('candidat', '')}"
            )

            st.write(
                f"**Profil :** "
                f"{ligne.get('type_profil', '')}"
            )

        with col2:

            st.write(
                f"**Poste :** "
                f"{ligne.get('poste', '')}"
            )

            st.write(
                f"**Entreprise :** "
                f"{ligne.get('entreprise', '')}"
            )

        with col3:

            st.write(
                f"**Entreprise :** "
                f"{ligne.get('type_entreprise', '')}"
            )

            st.write(
                f"**Date :** "
                f"{str(ligne.get('date_creation', ''))[:10]}"
            )

        with col4:

            nouveau_statut = st.selectbox(
                "Statut",
                STATUTS_SUIVI,
                index=(
                    STATUTS_SUIVI.index(
                        ligne.get("statut")
                    )
                    if ligne.get("statut")
                    in STATUTS_SUIVI
                    else 0
                ),
                key=f"statut_suivi_{ligne['id']}",
            )

            if nouveau_statut != ligne.get(
                "statut"
            ):

                if st.button(
                    "💾 Modifier",
                    key=f"modifier_{ligne['id']}",
                ):

                    modifier_statut_suivi(
                        ligne["id"],
                        nouveau_statut,
                    )

                    st.success(
                        "Statut modifié."
                    )

                    st.rerun()


# ============================================================
# STATISTIQUES
# ============================================================

elif page == "📈 Statistiques":

    st.markdown(
        '<div class="idees-title">📈 Statistiques</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="idees-subtitle">Agence de {agence}</div>',
        unsafe_allow_html=True,
    )

    stats = statistiques_hebdomadaires(
        agence
    )

    if not stats:

        st.info(
            "Aucune donnée disponible."
        )

    else:

        # ----------------------------------------------------
        # TABLEAU HEBDOMADAIRE
        # ----------------------------------------------------

        st.subheader(
            "📅 Activité hebdomadaire"
        )

        lignes_tableau = []

        for semaine, donnees in stats:

            lignes_tableau.append(
                {
                    "Semaine": semaine,
                    "Envoyées": donnees[
                        "envoyees"
                    ],
                    "Recrutées": donnees[
                        "recrutees"
                    ],
                    "Non pourvues": donnees[
                        "non_pourvues"
                    ],
                    "Taux transformation": (
                        f"{donnees['taux_transformation']:.1f} %"
                    ),
                    "Poids non pourvues": (
                        f"{donnees['poids_non_pourvues']:.1f} %"
                    ),
                    "Clients": donnees[
                        "clients"
                    ],
                    "Prospects": donnees[
                        "prospects"
                    ],
                    "Intérimaires": donnees[
                        "interimaires"
                    ],
                    "Candidats": donnees[
                        "candidats"
                    ],
                }
            )

        st.dataframe(
            lignes_tableau,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # DERNIÈRE SEMAINE
        # ----------------------------------------------------

        derniere_semaine = stats[0][1]

        st.subheader(
            "📊 Dernière semaine enregistrée"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            afficher_metric(
                "Candidatures envoyées",
                derniere_semaine[
                    "envoyees"
                ],
            )

        with col2:

            afficher_metric(
                "Recrutements",
                derniere_semaine[
                    "recrutees"
                ],
            )

        with col3:

            afficher_metric(
                "Commandes non pourvues",
                derniere_semaine[
                    "non_pourvues"
                ],
            )

        with col4:

            afficher_metric(
                "Transformation",
                f"{derniere_semaine['taux_transformation']:.1f} %",
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            afficher_metric(
                "Clients",
                derniere_semaine[
                    "clients"
                ],
            )

        with col2:

            afficher_metric(
                "Prospects",
                derniere_semaine[
                    "prospects"
                ],
            )

        with col3:

            afficher_metric(
                "Intérimaires",
                derniere_semaine[
                    "interimaires"
                ],
            )

        with col4:

            afficher_metric(
                "Candidats",
                derniere_semaine[
                    "candidats"
                ],
            )

        # ----------------------------------------------------
        # DÉTAIL CLIENT / PROSPECT
        # ----------------------------------------------------

        st.subheader(
            "🟢 Client / 🟠 Prospect"
        )

        for semaine, donnees in stats:

            st.markdown(
                f"### Semaine du {semaine}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"🟢 **Clients :** "
                    f"{donnees['clients']}"
                )

            with col2:

                st.write(
                    f"🟠 **Prospects :** "
                    f"{donnees['prospects']}"
                )

        # ----------------------------------------------------
        # DÉTAIL DES PROFILS
        # ----------------------------------------------------

        st.subheader(
            "👤 Intérimaires / Candidats"
        )

        for semaine, donnees in stats:

            st.markdown(
                f"### Semaine du {semaine}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"🟢 **Intérimaires :** "
                    f"{donnees['interimaires']}"
                )

            with col2:

                st.write(
                    f"🟡 **Candidats :** "
                    f"{donnees['candidats']}"
                )

        # ----------------------------------------------------
        # COMMANDES NON POURVUES
        # ----------------------------------------------------

        st.subheader(
            "⚠️ Poids des commandes non pourvues"
        )

        poids_chart = {
            semaine: donnees[
                "poids_non_pourvues"
            ]
            for semaine, donnees in stats
        }

        st.bar_chart(
            poids_chart
        )

        # ----------------------------------------------------
        # TAUX DE TRANSFORMATION
        # ----------------------------------------------------

        st.subheader(
            "📈 Taux de transformation"
        )

        transformation_chart = {
            semaine: donnees[
                "taux_transformation"
            ]
            for semaine, donnees in stats
        }

        st.line_chart(
            transformation_chart
        )