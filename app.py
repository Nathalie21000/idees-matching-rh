"""
app.py - Version complète et corrigée pour Nathalie (ID'EES INTERIM)
Utilise analyser_fiche_poste et extraire_sections_poste pour une lecture intelligente des fiches de poste.
"""

import re
import streamlit as st

# Imports depuis database
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

# Imports depuis matching
from matching import calculer_score

# Imports depuis metiers (y compris les nouvelles fonctions)
from metiers import (
    METIERS,
    detecter_metier,
    extraire_competences_pro,
    extraire_taches,
    detecter_vip_sir,
    analyser_fiche_poste,  # ✅ Nouvelle fonction pour les fiches de poste
    extraire_sections_poste,  # ✅ Nouvelle fonction pour les rubriques
)

# Imports depuis utils
from utils import (
    extract_text,
    generer_presentation,
)


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ID'EES INTERIM - Assistant IA RH",
    page_icon="🧑\u200d💼",
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
# FONCTIONS UTILITAIRES
# ============================================================

def extraire_candidat(nom_fichier):
    """Déduit le nom du candidat à partir du nom du fichier."""
    nom = re.sub(r"\.pdf$", "", nom_fichier, flags=re.IGNORECASE)
    nom = re.sub(r"\.docx$", "", nom, flags=re.IGNORECASE)
    nom = re.sub(r"[_\-]+", " ", nom)
    nom = re.sub(r"\s+", " ", nom).strip()
    return nom.title() if nom else "Candidat inconnu"


def extraire_caces(texte):
    """Extrait les mentions de CACES dans un texte."""
    caces = []
    motifs = [
        r"caces\s*r\d{3}",  # Ex: CACES R482
        r"r\d{3}",  # Ex: R482
        r"permis\s*[a-zA-Z]\d{1,2}",  # Ex: Permis C, Permis CE
    ]
    for motif in motifs:
        caces.extend(re.findall(motif, texte, flags=re.IGNORECASE))
    return list(set(caces))


def extraire_permis(texte):
    """Extrait les mentions de permis dans un texte."""
    permis = []
    motifs = [r"permis\s*[a-zA-Z]\d{0,2}"]  # Ex: Permis B, Permis C
    for motif in motifs:
        permis.extend(re.findall(motif, texte, flags=re.IGNORECASE))
    return list(set(permis))


# ============================================================
# INTERFACE STREAMLIT
# ============================================================

st.title("📄 Analyse des fiches de poste et CV")

# --- Section pour les fiches de poste ---
with st.expander("📋 Analyser une fiche de poste", expanded=True):
    poste_file = st.file_uploader("Sélectionnez une fiche de poste (PDF ou Word)", type=["pdf", "docx"])
    
    if poste_file:
        # Extraire le texte brut
        texte_brut = extract_text(poste_file)
        
        if texte_brut:
            st.success("Fiche de poste analysée avec succès. Vérifiez les informations avant d'enregistrer.")
            
            # ✅ Utiliser analyser_fiche_poste pour la lecture intelligente
            resultat = analyser_fiche_poste(texte_brut)
            
            # Afficher les informations extraites
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Entreprise détectée")
                entreprise = st.text_input(
                    "Entreprise", 
                    value=resultat.get("entreprise", "")
                )
                
                st.subheader("Intitulé détecté")
                intitule = st.text_input(
                    "Intitulé du poste", 
                    value=resultat.get("intitule", "")
                )
            
            with col2:
                st.subheader("Conditions de travail liées au poste")
                conditions = st.text_area(
                    "Conditions", 
                    value=resultat.get("conditions", "")
                )
            
            # Afficher les tâches proposées (priorité aux rubriques structurées)
            st.subheader("Liste des tâches proposées")
            taches = resultat.get("taches", "")
            if not taches:
                st.warning(
                    "La rubrique « Liste des tâches à proposer » n'a pas été détectée automatiquement. "
                    "Vous pourrez renseigner les tâches manuellement."
                )
            taches_input = st.text_area("Liste des tâches proposées", value=taches)
            
            # Afficher les habilitations
            st.subheader("Habilitations, certificats et diplômes obligatoires")
            habilitations = resultat.get("habilitations", "")
            habilitations_input = st.text_area("Habilitations", value=habilitations)
            
            # Afficher la conduite d'engins
            st.subheader("Conduite d'engins")
            conduite_engins = resultat.get("conduite_engins", "")
            conduite_input = st.text_area("Conduite d'engins", value=conduite_engins)
            
            # Afficher les machines/outils
            st.subheader("Utilisation de machines / outils")
            machines_outils = resultat.get("machines_outils", "")
            machines_input = st.text_area("Machines/Outils", value=machines_outils)
            
            # Afficher les informations de sécurité/risques
            st.subheader("Sécurité et risques")
            securite_risques = resultat.get("securite_risques", "")
            securite_input = st.text_area("Sécurité/Risques", value=securite_risques)
            
            # Afficher les tâches par rubrique (optionnel)
            if resultat.get("taches_par_rubrique"):
                with st.expander("🔍 Tâches détectées par rubrique"):
                    for rubrique, taches in resultat["taches_par_rubrique"].items():
                        st.write(f"**{rubrique}** : {', '.join(taches)}")
            
            # Afficher le texte brut pour debug (optionnel)
            with st.expander("🐛 Voir le texte brut extrait de la fiche de poste"):
                st.text_area("Texte brut", value=texte_brut, height=200)
            
            # Bouton pour enregistrer
            if st.button("Enregistrer la fiche de poste"):
                poste_data = {
                    "nom": poste_file.name,
                    "texte": texte_brut,
                    "entreprise": entreprise,
                    "intitule": intitule,
                    "taches": taches_input,
                    "habilitations": habilitations_input,
                    "conduite_engins": conduite_input,
                    "machines_outils": machines_input,
                    "securite_risques": securite_input,
                    "vip": resultat.get("vip", False),
                    "sir": resultat.get("sir", False),
                }
                enregistrer_poste(poste_data)
                st.success("Fiche de poste enregistrée avec succès !")
        else:
            st.error("Impossible d'extraire le texte de ce fichier.")


# --- Section pour les CV ---
with st.expander("👤 Analyser un CV", expanded=False):
    cv_file = st.file_uploader("Sélectionnez un CV (PDF ou Word)", type=["pdf", "docx"])
    
    if cv_file:
        texte_brut = extract_text(cv_file)
        
        if texte_brut:
            st.success("CV analysé avec succès. Vérifiez les informations avant d'enregistrer.")
            
            # Analyser le CV (utilisation des fonctions existantes)
            metier_detecte = detecter_metier(texte_brut)
            competences = extraire_competences_pro(texte_brut)
            taches = extraire_taches(texte_brut)
            caces = extraire_caces(texte_brut)
            permis = extraire_permis(texte_brut)
            vip_sir = detecter_vip_sir(texte_brut)
            
            # Afficher les informations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Candidat")
                nom_candidat = extraire_candidat(cv_file.name)
                nom = st.text_input("Nom du candidat", value=nom_candidat)
                
                st.subheader("Métier détecté")
                metier = st.selectbox(
                    "Métier", 
                    options=["Non détecté"] + list(METIERS.keys()), 
                    index=list(METIERS.keys()).index(metier_detecte) if metier_detecte in METIERS else 0
                )
            
            with col2:
                st.subheader("VIP/SIR")
                vip = st.checkbox("VIP", value="VIP" in vip_sir)
                sir = st.checkbox("SIR", value="SIR" in vip_sir)
            
            st.subheader("Compétences détectées")
            competences_input = st.text_area("Compétences", value=", ".join(competences))
            
            st.subheader("Tâches détectées")
            taches_input = st.text_area("Tâches", value=", ".join(taches))
            
            st.subheader("CACES détectés")
            caces_input = st.text_area("CACES", value=", ".join(caces))
            
            st.subheader("Permis détectés")
            permis_input = st.text_area("Permis", value=", ".join(permis))
            
            # Bouton pour enregistrer
            if st.button("Enregistrer le CV"):
                cv_data = {
                    "nom": nom,
                    "texte": texte_brut,
                    "metier": metier,
                    "competences": competences_input,
                    "taches": taches_input,
                    "caces": caces_input,
                    "permis": permis_input,
                    "vip": vip,
                    "sir": sir,
                }
                enregistrer_cv(cv_data)
                st.success("CV enregistré avec succès !")
        else:
            st.error("Impossible d'extraire le texte de ce fichier.")


# --- Section pour le matching ---
with st.expander("🔍 Matching CV/Fiche de poste", expanded=False):
    st.subheader("Trouver les CV correspondants à une fiche de poste")
    
    postes = recuperer_postes()
    poste_selectionne = st.selectbox("Sélectionnez une fiche de poste", options=[p["nom"] for p in postes])
    
    if poste_selectionne:
        poste = recuperer_poste(poste_selectionne)
        if poste:
            st.text_area("Description de la fiche de poste", value=poste["texte"], height=100)
            
            if st.button("Rechercher les CV correspondants"):
                cvs_matching = recuperer_cvs_matching(poste["texte"])
                if cvs_matching:
                    st.write(f"{len(cvs_matching)} CV(s) correspondant(s) trouvé(s) :")
                    for cv in cvs_matching:
                        st.write(f"- {cv['nom']} ({cv['metier']})")
                else:
                    st.warning("Aucun CV correspondant trouvé.")


# --- Section pour le suivi ---
with st.expander("📊 Suivi des candidats", expanded=False):
    st.subheader("Liste des suivis")
    suivis = lister_suivi()
    for suivi in suivis:
        st.write(f"- {suivi['candidat']} : {suivi['statut']}")


# --- Section pour les statistiques ---
with st.expander("📈 Statistiques", expanded=False):
    st.subheader("Statistiques globales")
    st.write(f"Nombre de CV : {compter_cv()}")
    st.write(f"Nombre de fiches de poste : {compter_postes()}")
    st.write(f"Nombre de suivis : {compter_suivi()}")
    
    st.subheader("Répartition des suivis")
    repartition = repartition_suivi()
    st.bar_chart(repartition)
