import re

import streamlit as st

from database import (
    init_db,
    get_connection,
    enregistrer_cv,
    enregistrer_poste,
    compter_cv,
    compter_postes,
    compter_suivi,
)
from matching import calculer_score
from metiers import METIERS, detecter_metier
from utils import extract_text

# ----------------------------
# CONFIGURATION GÉNÉRALE
# ----------------------------

st.set_page_config(
    page_title="ID'EES INTERIM - Assistant IA RH",
    page_icon="🧑‍💼",
    layout="wide"
)

# À adapter à la liste réelle des agences ID'EES INTERIM
AGENCES = [
    "Agence Paris",
    "Agence Lyon",
    "Agence Marseille",
    "Agence Toulouse",
    "Agence Nantes",
]

STATUTS_SUIVI = [
    "Candidature envoyée",
    "Entretien programmé",
    "Recruté",
    "Refusé",
]

init_db()


# ----------------------------
# FONCTIONS D'EXTRACTION
# ----------------------------

def extraire_candidat(nom_fichier):
    """
    Déduit un nom de candidat à partir du nom du fichier PDF
    (ex: 'jean_dupont_cv.pdf' -> 'Jean Dupont Cv').
    """
    nom = re.sub(r"\.pdf$", "", nom_fichier, flags=re.IGNORECASE)
    nom = re.sub(r"[_\-]+", " ", nom)
    nom = re.sub(r"\s+", " ", nom).strip()
    return nom.title() if nom else "Candidat inconnu"


def extraire_competences(texte):
    """
    Repère, parmi les mots-clés connus (metiers.py), ceux présents
    dans le texte pour obtenir une liste de compétences détectées.
    """
    trouve = set()
    for mots in METIERS.values():
        for mot in mots:
            if mot in texte:
                trouve.add(mot)
    return ", ".join(sorted(trouve))


def extraire_caces(texte):
    """
    Détecte les CACES mentionnés (ex: R482, R489, R486...).
    """
    resultats = {m.upper() for m in re.findall(r"r4\d{2}", texte)}
    return ", ".join(sorted(resultats))


def extraire_permis(texte):
    """
    Détecte les permis mentionnés (ex: permis B, permis CE...).
    """
    resultats = {m.upper() for m in re.findall(r"permis\s+([a-z]{1,2}\d?)", texte)}
    return ", ".join(sorted(resultats))


# ----------------------------
# BARRE LATÉRALE
# ----------------------------

st.sidebar.title("🧑‍💼 ID'EES INTERIM")

agence = st.sidebar.selectbox("Agence", AGENCES)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Tableau de bord",
        "📄 Importer un CV",
        "📚 CVthèque",
        "🏢 Importer une fiche de poste",
        "🔍 Matching",
        "📋 Suivi des candidatures",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Agence sélectionnée : **{agence}**")


# ----------------------------
# PAGE : TABLEAU DE BORD
# ----------------------------

if page == "📊 Tableau de bord":

    st.title("📊 Tableau de bord")
    st.caption(f"Agence : {agence}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CV enregistrés", compter_cv(agence))
    col2.metric("Postes enregistrés", compter_postes(agence))
    col3.metric("Entretiens programmés", compter_suivi(agence, "Entretien programmé"))
    col4.metric("Recrutements", compter_suivi(agence, "Recruté"))

    st.markdown("---")
    st.subheader("Répartition des candidatures par statut")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT statut, COUNT(*) FROM suivi WHERE agence=? GROUP BY statut",
        (agence,),
    )
    lignes = cursor.fetchall()
    conn.close()

    if lignes:
        st.bar_chart({statut: nb for statut, nb in lignes})
    else:
        st.info("Aucune candidature suivie pour le moment.")


# ----------------------------
# PAGE : IMPORT CV
# ----------------------------

elif page == "📄 Importer un CV":

    st.title("📄 Importer un CV")

    fichier = st.file_uploader("Sélectionnez un CV (PDF)", type=["pdf"])

    if fichier is not None:

        texte = extract_text(fichier)

        if not texte:
            st.error("Impossible d'extraire le texte de ce PDF (fichier scanné ?).")
        else:
            candidat_detecte = extraire_candidat(fichier.name)
            metier_detecte = detecter_metier(texte)
            competences_detectees = extraire_competences(texte)
            caces_detectes = extraire_caces(texte)
            permis_detectes = extraire_permis(texte)

            st.success("CV analysé avec succès. Vérifiez les informations avant d'enregistrer.")

            with st.form("form_cv"):
                candidat = st.text_input("Nom du candidat", value=candidat_detecte)
                metier = st.text_input("Métier détecté", value=metier_detecte)
                competences = st.text_area("Compétences détectées", value=competences_detectees)
                caces = st.text_input("CACES détectés", value=caces_detectes)
                permis = st.text_input("Permis détectés", value=permis_detectes)

                valider = st.form_submit_button("Enregistrer ce CV")

            if valider:
                enregistrer_cv(
                    agence,
                    fichier.name,
                    candidat,
                    metier,
                    competences,
                    caces,
                    permis,
                    texte,
                )
                st.success(f"CV de {candidat} enregistré pour {agence}.")
                st.rerun()

            with st.expander("Voir le texte extrait du CV"):
                st.text(texte)

# ----------------------------
# PAGE : CVTHÈQUE
# ----------------------------

elif page == "📚 CVthèque":

    st.title("📚 CVthèque")

    recherche = st.text_input(
        "Rechercher un candidat, un métier ou une compétence"
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            candidat,
            metier,
            competences,
            caces,
            permis,
            date_creation
        FROM cv
        WHERE agence=?
        ORDER BY date_creation DESC
    """, (agence,))

    cvs = cursor.fetchall()
    conn.close()

    if not cvs:
        st.info("Aucun CV enregistré pour cette agence.")

    else:

        for cv in cvs:

            (
                cv_id,
                candidat,
                metier,
                competences,
                caces,
                permis,
                date_creation,
            ) = cv

            texte_recherche = (
                f"{candidat} {metier} {competences}"
            ).lower()

            if recherche:
                if recherche.lower() not in texte_recherche:
                    continue

            with st.expander(f"👤 {candidat} - {metier}"):

                st.write(f"**Métier :** {metier}")

                st.write(f"**Compétences :** {competences}")

                st.write(f"**CACES :** {caces if caces else 'Aucun'}")

                st.write(f"**Permis :** {permis if permis else 'Non renseigné'}")

                st.caption(f"Ajouté le {date_creation}")
# ----------------------------
# PAGE : IMPORT FICHE DE POSTE
# ----------------------------

elif page == "🏢 Importer une fiche de poste":

    st.title("🏢 Importer une fiche de poste")

    fichier = st.file_uploader("Sélectionnez une fiche de poste (PDF)", type=["pdf"])

    if fichier is not None:

        texte = extract_text(fichier)

        if not texte:
            st.error("Impossible d'extraire le texte de ce PDF (fichier scanné ?).")
        else:
            metier_detecte = detecter_metier(texte)
            competences_detectees = extraire_competences(texte)
            caces_detectes = extraire_caces(texte)
            permis_detectes = extraire_permis(texte)

            st.success("Fiche de poste analysée avec succès. Vérifiez les informations avant d'enregistrer.")

            with st.form("form_poste"):
                entreprise = st.text_input("Entreprise cliente")
                poste = st.text_input(
                    "Intitulé du poste",
                    value=metier_detecte if metier_detecte != "Non détecté" else "",
                )
                competences = st.text_area("Compétences requises", value=competences_detectees)
                caces = st.text_input("CACES requis", value=caces_detectes)
                permis = st.text_input("Permis requis", value=permis_detectes)

                valider = st.form_submit_button("Enregistrer cette fiche de poste")

            if valider:
                if not entreprise or not poste:
                    st.error("Merci de renseigner au moins l'entreprise et l'intitulé du poste.")
                else:
                    enregistrer_poste(
                        agence,
                        entreprise,
                        poste,
                        competences,
                        caces,
                        permis,
                        texte,
                    )
                    st.success(f"Fiche de poste « {poste} » enregistrée pour {entreprise}.")
                    st.rerun()

            with st.expander("Voir le texte extrait de la fiche de poste"):
                st.text(texte)


# ----------------------------
# PAGE : MATCHING
# ----------------------------

elif page == "🔍 Matching":

    st.title("🔍 Matching CV / Fiches de poste")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, poste, entreprise FROM postes WHERE agence=? ORDER BY date_creation DESC",
        (agence,),
    )
    postes = cursor.fetchall()

    cursor.execute(
        "SELECT id, candidat, texte FROM cv WHERE agence=? ORDER BY date_creation DESC",
        (agence,),
    )
    cvs = cursor.fetchall()

    conn.close()

    if not postes:
        st.info("Aucune fiche de poste enregistrée pour cette agence.")
    elif not cvs:
        st.info("Aucun CV enregistré pour cette agence.")
    else:
        options_postes = {f"{p[1]} — {p[2]}": p[0] for p in postes}
        choix_poste = st.selectbox("Choisissez une fiche de poste", list(options_postes.keys()))
        poste_id = options_postes[choix_poste]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT texte, poste, entreprise FROM postes WHERE id=?", (poste_id,))
        poste_texte, poste_nom, entreprise_nom = cursor.fetchone()
        conn.close()

        resultats = []
        for cv_id, candidat, cv_texte in cvs:
            score, mots_communs, metier_cv, _ = calculer_score(cv_texte, poste_texte)
            resultats.append({
                "cv_id": cv_id,
                "candidat": candidat,
                "metier": metier_cv,
                "score": score,
                "mots_communs": mots_communs,
            })

        resultats.sort(key=lambda r: r["score"], reverse=True)

        st.subheader(f"Résultats pour : {poste_nom} — {entreprise_nom}")

        for r in resultats:
            with st.expander(f"{r['candidat']} — {r['score']}% de compatibilité ({r['metier']})"):
                st.progress(min(r["score"], 100) / 100)

                if r["mots_communs"]:
                    st.caption("Mots-clés en commun : " + ", ".join(r["mots_communs"][:20]))

                statut = st.selectbox(
                    "Statut de la candidature",
                    STATUTS_SUIVI,
                    key=f"statut_{r['cv_id']}",
                )

                if st.button("Ajouter au suivi", key=f"suivi_{r['cv_id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO suivi(agence, candidat, entreprise, poste, statut)
                        VALUES(?,?,?,?,?)
                        """,
                        (agence, r["candidat"], entreprise_nom, poste_nom, statut),
                    )
                    conn.commit()
                    conn.close()
                    st.success("Candidature ajoutée au suivi.")


# ----------------------------
# PAGE : SUIVI DES CANDIDATURES
# ----------------------------

elif page == "📋 Suivi des candidatures":

    st.title("📋 Suivi des candidatures")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, candidat, entreprise, poste, statut, date_creation "
        "FROM suivi WHERE agence=? ORDER BY date_creation DESC",
        (agence,),
    )
    lignes = cursor.fetchall()
    conn.close()

    if not lignes:
        st.info("Aucune candidature suivie pour le moment.")
    else:
        for suivi_id, candidat, entreprise, poste, statut, date_creation in lignes:
            col1, col2 = st.columns([4, 2])

            with col1:
                st.write(f"**{candidat}** → {poste} chez {entreprise}")
                st.caption(f"Ajouté le {date_creation}")

            with col2:
                nouveau_statut = st.selectbox(
                    "Statut",
                    STATUTS_SUIVI,
                    index=STATUTS_SUIVI.index(statut) if statut in STATUTS_SUIVI else 0,
                    key=f"maj_statut_{suivi_id}",
                    label_visibility="collapsed",
                )
                if nouveau_statut != statut:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE suivi SET statut=? WHERE id=?",
                        (nouveau_statut, suivi_id),
                    )
                    conn.commit()
                    conn.close()
                    st.rerun()

            st.markdown("---")
