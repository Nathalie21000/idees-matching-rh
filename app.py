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
    supprimer_poste,
)

from matching import calculer_score

from metiers import (
    METIERS,
    detecter_metier,
    extraire_competences_pro,
    extraire_taches,
    extraire_taches_par_lignes,
    detecter_vip_sir,
    analyser_fiche_poste,
)

from utils import (
    extract_text,
    generer_presentation,
)


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ID'EES INTERIM - Assistant IA RH",
    page_icon="🧑‍💼",
    layout="wide",
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
]

init_db()


# ============================================================
# EXTRACTION CV
# ============================================================

def extraire_candidat(nom_fichier):
    nom = re.sub(
        r"\.(pdf|docx)$",
        "",
        nom_fichier,
        flags=re.IGNORECASE,
    )
    nom = re.sub(r"[_\-]+", " ", nom)
    nom = re.sub(r"\s+", " ", nom).strip()
    return nom.title() if nom else "Candidat inconnu"


def extraire_competences(texte):
    """
    Pour un CV, récupère les compétences/mots-clés utiles.
    Cette fonction n'est PAS utilisée pour remplir automatiquement
    les compétences d'une fiche de poste.
    """
    trouve = set()
    texte_min = (texte or "").lower()

    for mots in METIERS.values():
        for mot in mots:
            if mot.lower() in texte_min:
                trouve.add(mot)

    for competence in extraire_competences_pro(texte):
        trouve.add(competence)

    return ", ".join(sorted(trouve))


def extraire_caces(texte):
    resultats = {
        m.upper()
        for m in re.findall(
            r"r4\d{2}",
            texte or "",
            flags=re.IGNORECASE,
        )
    }
    return ", ".join(sorted(resultats))


def extraire_permis(texte):
    resultats = {
        m.upper()
        for m in re.findall(
            r"permis\s+([a-z]{1,2}\d?)",
            texte or "",
            flags=re.IGNORECASE,
        )
    }
    return ", ".join(sorted(resultats))


def _texte_taches_cv(texte):
    """
    Tâches CV :
    1. on prend les lignes qui commencent par un verbe d'action
       (regroupées par rubrique par extraire_taches_par_lignes) ;
    2. on complète avec les tâches connues ;
    3. on déduplique.
    """
    resultat = []
    vus = set()

    taches_par_rubrique = extraire_taches_par_lignes(texte)

    for groupe in taches_par_rubrique.values():
        for ligne in groupe:
            cle = ligne.lower().strip()
            if cle not in vus:
                vus.add(cle)
                resultat.append(ligne)

    for tache in extraire_taches(texte):
        cle = tache.lower().strip()
        if cle not in vus:
            vus.add(cle)
            resultat.append(tache)

    return resultat


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🧑‍💼 ID'EES INTERIM")

agence = st.sidebar.selectbox(
    "Agence",
    AGENCES,
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Tableau de bord",
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
st.sidebar.caption(f"Agence sélectionnée : **{agence}**")


# ============================================================
# TABLEAU DE BORD
# ============================================================

if page == "📊 Tableau de bord":

    st.title("📊 Tableau de bord")
    st.caption(f"Agence : {agence}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("CV enregistrés", compter_cv(agence))
    col2.metric("Postes enregistrés", compter_postes(agence))
    col3.metric(
        "Entretiens programmés",
        compter_suivi(agence, "Entretien programmé"),
    )
    col4.metric(
        "Recrutements",
        compter_suivi(agence, "Recruté"),
    )

    st.markdown("---")

    col5, col6 = st.columns(2)

    col5.metric(
        "🟢 CV envoyés à des clients",
        compter_clients(agence),
    )

    col6.metric(
        "🟠 CV envoyés à des prospects",
        compter_prospects(agence),
    )

    st.subheader("Répartition des candidatures par statut")

    lignes = repartition_suivi(agence)

    if lignes:
        st.bar_chart(lignes)
    else:
        st.info("Aucune candidature suivie pour le moment.")


# ============================================================
# IMPORT CV
# ============================================================

elif page == "📄 Importer un CV":

    st.title("📄 Importer un CV")

    fichier = st.file_uploader(
        "Sélectionnez un CV (PDF ou Word)",
        type=["pdf", "docx"],
    )

    if fichier is not None:

        texte = extract_text(fichier)

        if not texte:

            st.error(
                "Impossible d'extraire le texte de ce fichier "
                "(document scanné ou vide ?)."
            )

        else:

            candidat_detecte = extraire_candidat(fichier.name)
            metier_detecte = detecter_metier(texte)
            competences_detectees = extraire_competences(texte)

            taches_detectees = ", ".join(
                _texte_taches_cv(texte)
            )

            caces_detectes = extraire_caces(texte)
            permis_detectes = extraire_permis(texte)

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

                competences = st.text_area(
                    "Compétences détectées",
                    value=competences_detectees,
                )

                taches = st.text_area(
                    "Tâches / missions déjà réalisées",
                    value=taches_detectees,
                    help=(
                        "Les lignes commençant par des verbes d'action "
                        "sont détectées même lorsqu'elles figurent "
                        "dans une rubrique Compétences."
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
                    ["🟢 Intérimaire", "🟡 Candidat"],
                    horizontal=True,
                )

                valider = st.form_submit_button("Enregistrer ce CV")

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
                    )

                    st.success(
                        f"CV de {candidat} enregistré pour {agence}."
                    )
                    st.rerun()

                except Exception as erreur:

                    st.error(
                        "Erreur lors de l'enregistrement du CV dans Supabase."
                    )
                    st.exception(erreur)

            with st.expander("Voir le texte extrait du CV"):
                st.text(texte)


# ============================================================
# CVTHEQUE
# ============================================================

elif page == "📂 CVthèque":

    st.title("📚 CVthèque")

    recherche = st.text_input(
        "🔎 Rechercher un candidat, une compétence..."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        filtre_metier = st.text_input("👷 Métier")

    with col2:
        filtre_caces = st.text_input("🚜 CACES")

    with col3:
        filtre_permis = st.text_input("🚗 Permis")

    cvs = lister_cv(agence)

    if not cvs:
        st.info("Aucun CV enregistré pour cette agence.")

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

            texte_recherche = (
                f"{candidat} {metier} {competences} "
                f"{caces} {permis} {texte}"
            ).lower()

            if recherche and recherche.lower() not in texte_recherche:
                continue

            if filtre_metier and filtre_metier.lower() not in metier.lower():
                continue

            if filtre_caces and filtre_caces.lower() not in caces.lower():
                continue

            if filtre_permis and filtre_permis.lower() not in permis.lower():
                continue

            with st.expander(f"👤 {candidat} - {metier}"):

                st.write(f"**Métier :** {metier}")
                st.write(f"**Compétences :** {competences}")

                st.write(
                    f"**Tâches déjà réalisées :** "
                    f"{taches if taches else 'Non renseigné'}"
                )

                st.write(
                    f"**CACES :** {caces if caces else 'Aucun'}"
                )

                st.write(
                    f"**Permis :** {permis if permis else 'Non renseigné'}"
                )

                st.write(
                    f"**Type de profil :** "
                    f"{type_profil if type_profil else 'Non renseigné'}"
                )

                st.caption(f"Ajouté le {date_creation}")

                if texte:
                    with st.expander("Voir le texte complet du CV"):
                        st.text(texte)


# ============================================================
# IMPORT FICHE DE POSTE
# ============================================================

elif page == "🏢 Importer une fiche de poste":

    st.title("🏢 Importer une fiche de poste")

    fichier = st.file_uploader(
        "Sélectionnez une fiche de poste (PDF ou Word)",
        type=["pdf", "docx"],
    )

    if fichier is not None:

        texte = extract_text(fichier)
        analyse = analyser_fiche_poste(texte)

        if not texte:

            st.error(
                "Impossible d'extraire le texte de cette fiche de poste "
                "(document scanné ou vide ?)."
            )

            st.info(
                "L'OCR des documents scannés est prévu dans l'étape suivante."
            )

        else:

            entreprise_detectee = analyse.get("entreprise") or ""
            poste_detecte = analyse.get("intitule") or ""
            taches_detectees = analyse.get("taches") or ""

            # IMPORTANT :
            # Les compétences ne sont plus fabriquées à partir de tout
            # le texte de la fiche. On laisse vide si la zone dédiée
            # n'est pas identifiable.
            competences_detectees = analyse.get("competences") or ""

            caces_detectes = extraire_caces(
                analyse.get("conduite_engins", "") + "\n" + texte
            )

            permis_detectes = extraire_permis(texte)

            if analyse.get("vip") and analyse.get("sir"):
                vip_sir_detecte = "VIP + SIR"
            elif analyse.get("vip"):
                vip_sir_detecte = "VIP"
            elif analyse.get("sir"):
                vip_sir_detecte = "SIR"
            else:
                vip_sir_detecte = detecter_vip_sir(texte)

            st.success(
                "Fiche de poste analysée. "
                "Vérifiez les informations avant d'enregistrer."
            )

            if not entreprise_detectee:
                st.warning(
                    "La rubrique « Nom de l'entreprise » n'a pas été "
                    "identifiée automatiquement."
                )

            if not poste_detecte:
                st.warning(
                    "La rubrique « Intitulé du poste » n'a pas été "
                    "identifiée automatiquement."
                )
                          if not entreprise_detectee:
                st.warning(
                    "La rubrique « Nom de l'entreprise » n'a pas été "
                    "identifiée automatiquement."
                )          
