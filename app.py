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

def extraire_candidat(
    nom_fichier,
):

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

    return (
        nom.title()
        if nom
        else "Candidat inconnu"
    )


def extraire_competences(
    texte,
):
    """
    Extraction des compétences pour les CV.

    Cette fonction reste utilisée pour les CV.

    Elle n'est PAS utilisée pour les fiches de poste.
    """

    trouve = set()

    texte_min = (
        texte or ""
    ).lower()

    for mots in METIERS.values():

        for mot in mots:

            if mot.lower() in texte_min:

                trouve.add(
                    mot
                )

    for competence in extraire_competences_pro(
        texte
    ):

        trouve.add(
            competence
        )

    return ", ".join(
        sorted(trouve)
    )


def extraire_caces(
    texte,
):

    resultats = {
        m.upper()
        for m in re.findall(
            r"r4\d{2}",
            texte or "",
            flags=re.IGNORECASE,
        )
    }

    return ", ".join(
        sorted(resultats)
    )


def extraire_permis(
    texte,
):

    resultats = {
        m.upper()
        for m in re.findall(
            r"permis\s+([a-z]{1,2}\d?)",
            texte or "",
            flags=re.IGNORECASE,
        )
    }

    return ", ".join(
        sorted(resultats)
    )


# ============================================================
# BARRE LATERALE
# ============================================================

st.sidebar.title(
    "🧑‍💼 ID'EES INTERIM"
)

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

st.sidebar.caption(
    f"Agence sélectionnée : **{agence}**"
)


# ============================================================
# TABLEAU DE BORD
# ============================================================

if page == "📊 Tableau de bord":

    st.title(
        "📊 Tableau de bord"
    )

    st.caption(
        f"Agence : {agence}"
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

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

    st.markdown("---")

    col5, col6 = st.columns(
        2
    )

    col5.metric(
        "🟢 CV envoyés à des clients",
        compter_clients(agence),
    )

    col6.metric(
        "🟠 CV envoyés à des prospects",
        compter_prospects(agence),
    )

    st.subheader(
        "Répartition des candidatures par statut"
    )

    lignes = repartition_suivi(
        agence
    )

    if lignes:

        st.bar_chart(
            lignes
        )

    else:

        st.info(
            "Aucune candidature suivie pour le moment."
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
        type=[
            "pdf",
            "docx",
        ],
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

            candidat_detecte = (
                extraire_candidat(
                    fichier.name
                )
            )

            metier_detecte = (
                detecter_metier(
                    texte
                )
            )

            competences_detectees = (
                extraire_competences(
                    texte
                )
            )

            taches_detectees = ", ".join(
                extraire_taches(
                    texte
                )
            )

            caces_detectes = (
                extraire_caces(
                    texte
                )
            )

            permis_detectes = (
                extraire_permis(
                    texte
                )
            )

            st.success(
                "CV analysé avec succès. "
                "Vérifiez les informations avant d'enregistrer."
            )

            with st.form(
                "form_cv"
            ):

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

                    st.exception(
                        erreur
                    )

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

    col1, col2, col3 = st.columns(
        3
    )

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

            cv_id = cv.get(
                "id"
            )

            candidat = cv.get(
                "candidat"
            ) or ""

            metier = cv.get(
                "metier"
            ) or ""

            competences = cv.get(
                "competences"
            ) or ""

            taches = cv.get(
                "taches"
            ) or ""

            caces = cv.get(
                "caces"
            ) or ""

            permis = cv.get(
                "permis"
            ) or ""

            type_profil = cv.get(
                "type_profil"
            ) or ""

            date_creation = cv.get(
                "date_creation"
            ) or ""

            texte = cv.get(
                "texte"
            ) or ""

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


# ============================================================
# IMPORT FICHE DE POSTE
# ============================================================

elif page == "🏢 Importer une fiche de poste":

    st.title(
        "🏢 Importer une fiche de poste"
    )

    st.info(
        "L'application recherche uniquement le nom de "
        "l'entreprise, l'intitulé du poste et la rubrique "
        "« Liste des tâches proposées »."
    )

    fichier = st.file_uploader(
        "Sélectionnez une fiche de poste (PDF ou Word)",
        type=[
            "pdf",
            "docx",
        ],
    )

    if fichier is not None:

        texte = extract_text(
            fichier
        )

        if not texte:

            st.error(
                "Impossible de lire cette fiche de poste. "
                "Le document est peut-être scanné ou vide."
            )

        else:

            # ==================================================
            # LECTURE CIBLEE
            # ==================================================

            fiche = (
                extraire_fiche_poste_ciblee(
                    texte
                )
            )

            entreprise_detectee = (
                fiche.get(
                    "entreprise"
                )
                or ""
            )

            poste_detecte = (
                fiche.get(
                    "poste"
                )
                or ""
            )

            taches_detectees = (
                fiche.get(
                    "taches"
                )
                or ""
            )

            # --------------------------------------------------
            # MESSAGE DE CONTROLE
            # --------------------------------------------------

            entreprise_trouvee = fiche.get(
                "entreprise_trouvee",
                False,
            )

            poste_trouve = fiche.get(
                "poste_trouve",
                False,
            )

            taches_trouvees = fiche.get(
                "taches_trouvees",
                False,
            )

            if (
                entreprise_trouvee
                and poste_trouve
                and taches_trouvees
            ):

                st.success(
                    "Les 3 informations principales "
                    "de la fiche de poste ont été détectées."
                )

            else:

                st.warning(
                    "Certaines rubriques n'ont pas été "
                    "détectées automatiquement. "
                    "L'application ne va pas inventer de valeur."
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

            # ==================================================
            # FORMULAIRE
            # ==================================================

            with st.form(
                "form_poste"
            ):

                entreprise = st.text_input(
                    "Entreprise cliente",
                    value=entreprise_detectee,
                )

                poste = st.text_input(
                    "Intitulé du poste",
                    value=poste_detecte,
                )

                # ------------------------------------------------
                # IMPORTANT :
                # ON NE REMPLIT PLUS LES COMPETENCES
                # AUTOMATIQUEMENT.
                # ------------------------------------------------

                competences = st.text_area(
                    "Compétences requises",
                    value="",
                    help=(
                        "Ce champ n'est plus rempli automatiquement "
                        "pour éviter les faux résultats. "
                        "Vous pouvez le compléter manuellement si nécessaire."
                    ),
                )

                taches = st.text_area(
                    "Tâches à réaliser",
                    value=taches_detectees,
                    height=220,
                    help=(
                        "Copie du contenu de la rubrique "
                        "« Liste des tâches proposées » de la fiche de poste."
                    ),
                )

                # ------------------------------------------------
                # CACES ET PERMIS
                # ------------------------------------------------

                caces_detectes = extraire_caces(
                    texte
                )

                permis_detectes = extraire_permis(
                    texte
                )

                caces = st.text_input(
                    "CACES requis",
                    value=caces_detectes,
                )

                permis = st.text_input(
                    "Permis requis",
                    value=permis_detectes,
                )

                # ------------------------------------------------
                # VIP / SIR
                # ------------------------------------------------

                vip_sir_detecte = detecter_vip_sir(
                    texte
                )

                choix_vip_sir = [
                    "",
                    "VIP",
                    "SIR",
                    "VIP + SIR",
                ]

                if (
                    vip_sir_detecte
                    in choix_vip_sir
                ):

                    index_vip_sir = choix_vip_sir.index(
                        vip_sir_detecte
                    )

                else:

                    index_vip_sir = 0

                vip_sir = st.selectbox(
                    "Suivi médical requis",
                    choix_vip_sir,
                    index=index_vip_sir,
                    help=(
                        "VIP = Visite Infirmier Périodique. "
                        "SIR = Suivi Individuel Renforcé."
                    ),
                )

                valider = st.form_submit_button(
                    "Enregistrer cette fiche de poste"
                )

            # ==================================================
            # ENREGISTREMENT
            # ==================================================

            if valider:

                if not entreprise:

                    st.error(
                        "Merci de renseigner le nom de l'entreprise."
                    )

                elif not poste:

                    st.error(
                        "Merci de renseigner l'intitulé du poste."
                    )

                elif not taches:

                    st.warning(
                        "Aucune tâche n'a été détectée. "
                        "Vous pouvez renseigner manuellement "
                        "la rubrique « Tâches à réaliser »."
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

                        st.exception(
                            erreur
                        )

            # ==================================================
            # CONTROLE DU TEXTE LU
            # ==================================================

            with st.expander(
                "🔎 Voir exactement ce que l'application a lu"
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

    col1, col2, col3 = st.columns(
        3
    )

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

            poste_id = poste_item.get(
                "id"
            )

            entreprise = poste_item.get(
                "entreprise"
            ) or ""

            intitule = poste_item.get(
                "poste"
            ) or ""

            competences = poste_item.get(
                "competences"
            ) or ""

            taches = poste_item.get(
                "taches"
            ) or ""

            vip_sir = poste_item.get(
                "vip_sir"
            ) or ""

            caces = poste_item.get(
                "caces"
            ) or ""

            permis = poste_item.get(
                "permis"
            ) or ""

            date_creation = poste_item.get(
                "date_creation"
            ) or ""

            texte_poste = poste_item.get(
                "texte"
            ) or ""

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

                st.markdown(
                    "---"
                )

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

                        st.exception(
                            erreur
                        )


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
            list(
                options_postes.keys()
            ),
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

            poste_nom = (
                poste.get(
                    "poste"
                )
                or ""
            )

            entreprise_nom = (
                poste.get(
                    "entreprise"
                )
                or ""
            )

            resultats = []

            for cv in cvs:

                resultat_matching = (
                    calculer_score(
                        cv,
                        poste,
                    )
                )

                resultats.append(
                    {
                        "cv_id": cv.get(
                            "id"
                        ),
                        "candidat": cv.get(
                            "candidat"
                        ) or "",
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
                            100,
                        ) / 100
                    )

                    for ligne_explication in (
                        r["explication"]
                    ):

                        st.write(
                            ligne_explication
                        )

                    st.markdown(
                        "---"
                    )

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

                            st.exception(
                                erreur
                            )

                    st.markdown(
                        "---"
                    )

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

                            texte = (
                                generer_presentation(
                                    candidat,
                                    metier,
                                    competences,
                                    caces,
                                    permis,
                                    entreprise_nom,
                                    agence,
                                )
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

            suivi_id = ligne.get(
                "id"
            )

            candidat = ligne.get(
                "candidat"
            ) or ""

            entreprise = ligne.get(
                "entreprise"
            ) or ""

            poste = ligne.get(
                "poste"
            ) or ""

            statut = ligne.get(
                "statut"
            ) or ""

            type_entreprise = (
                ligne.get(
                    "type_entreprise"
                )
                or ""
            )

            date_creation = (
                ligne.get(
                    "date_creation"
                )
                or ""
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

                        st.exception(
                            erreur
                        )


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

            st.markdown(
                "---"
            )
