import streamlit as st

from supabase import create_client, Client


# ============================================================
# CONNEXION SUPABASE
# ============================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ============================================================
# INITIALISATION
# ============================================================

def init_db():
    """
    Supabase possède déjà les tables.
    Fonction conservée pour rester compatible avec app.py.
    """
    return None


# ============================================================
# ENREGISTREMENT D'UN CV
# ============================================================

def enregistrer_cv(
    agence,
    nom_fichier,
    candidat,
    metier,
    competences,
    caces,
    permis,
    type_profil,
    texte,
    taches="",
):
    donnees = {
        "agence": agence,
        "nom_fichier": nom_fichier,
        "candidat": candidat,
        "metier": metier,
        "competences": competences,
        "caces": caces,
        "permis": permis,
        "type_profil": type_profil,
        "texte": texte,
        "taches": taches,
    }

    resultat = (
        supabase
        .table("cv")
        .insert(donnees)
        .execute()
    )

    if not resultat.data:
        raise RuntimeError(
            "Supabase n'a retourné aucune donnée après "
            f"l'enregistrement du CV : {resultat}"
        )

    return resultat.data[0]


# ============================================================
# ENREGISTREMENT D'UNE FICHE DE POSTE
# ============================================================

def enregistrer_poste(
    agence,
    entreprise,
    poste,
    competences,
    caces,
    permis,
    texte,
    taches="",
    vip_sir="",
):
    donnees = {
        "agence": agence,
        "entreprise": entreprise,
        "poste": poste,
        "competences": competences,
        "caces": caces,
        "permis": permis,
        "texte": texte,
        "taches": taches,
        "vip_sir": vip_sir,
    }

    resultat = (
        supabase
        .table("postes")
        .insert(donnees)
        .execute()
    )

    if not resultat.data:
        raise RuntimeError(
            "Supabase n'a retourné aucune donnée après "
            f"l'enregistrement de la fiche de poste : {resultat}"
        )

    return resultat.data[0]


# ============================================================
# ENREGISTREMENT D'UN SUIVI
# ============================================================

def enregistrer_suivi(
    agence,
    candidat,
    entreprise,
    poste,
    statut,
    type_entreprise=None,
):
    donnees = {
        "agence": agence,
        "candidat": candidat,
        "entreprise": entreprise,
        "poste": poste,
        "statut": statut,
        "type_entreprise": type_entreprise,
    }

    resultat = (
        supabase
        .table("suivi")
        .insert(donnees)
        .execute()
    )

    if not resultat.data:
        raise RuntimeError(
            "Supabase n'a retourné aucune donnée après "
            f"l'enregistrement du suivi : {resultat}"
        )

    return resultat.data[0]


# ============================================================
# COMPTER LES CV
# ============================================================

def compter_cv(agence):
    resultat = (
        supabase
        .table("cv")
        .select("id", count="exact")
        .eq("agence", agence)
        .execute()
    )

    return resultat.count or 0


# ============================================================
# COMPTER LES POSTES
# ============================================================

def compter_postes(agence):
    resultat = (
        supabase
        .table("postes")
        .select("id", count="exact")
        .eq("agence", agence)
        .execute()
    )

    return resultat.count or 0


# ============================================================
# COMPTER LE SUIVI
# ============================================================

def compter_suivi(agence, statut):
    resultat = (
        supabase
        .table("suivi")
        .select("id", count="exact")
        .eq("agence", agence)
        .eq("statut", statut)
        .execute()
    )

    return resultat.count or 0


# ============================================================
# COMPTER LES CLIENTS
# ============================================================

def compter_clients(agence):
    resultat = (
        supabase
        .table("suivi")
        .select("id", count="exact")
        .eq("agence", agence)
        .eq("type_entreprise", "🟢 Client")
        .execute()
    )

    return resultat.count or 0


# ============================================================
# COMPTER LES PROSPECTS
# ============================================================

def compter_prospects(agence):
    resultat = (
        supabase
        .table("suivi")
        .select("id", count="exact")
        .eq("agence", agence)
        .eq("type_entreprise", "🟠 Prospect")
        .execute()
    )

    return resultat.count or 0


# ============================================================
# REPARTITION DU SUIVI PAR STATUT
# ============================================================

def repartition_suivi(agence):
    resultat = (
        supabase
        .table("suivi")
        .select("statut")
        .eq("agence", agence)
        .execute()
    )

    lignes = resultat.data or []

    compteurs = {}

    for ligne in lignes:
        statut = ligne.get("statut")

        if statut:
            compteurs[statut] = compteurs.get(statut, 0) + 1

    return compteurs


# ============================================================
# LISTER LES CV
# ============================================================

def lister_cv(agence):
    resultat = (
        supabase
        .table("cv")
        .select(
            "id, candidat, metier, competences, taches, "
            "caces, permis, type_profil, date_creation, texte"
        )
        .eq("agence", agence)
        .order("date_creation", desc=True)
        .execute()
    )

    return resultat.data or []


# ============================================================
# RECUPERER LES CV POUR LE MATCHING
# ============================================================

def recuperer_cvs_matching(agence):
    resultat = (
        supabase
        .table("cv")
        .select(
            "id, candidat, texte, metier, competences, taches, "
            "caces, permis, type_profil"
        )
        .eq("agence", agence)
        .order("date_creation", desc=True)
        .execute()
    )

    return resultat.data or []


# ============================================================
# RECUPERER LES FICHES DE POSTE
# ============================================================

def recuperer_postes(agence):
    resultat = (
        supabase
        .table("postes")
        .select(
            "id, entreprise, poste, competences, taches, "
            "vip_sir, caces, permis, texte, date_creation"
        )
        .eq("agence", agence)
        .order("date_creation", desc=True)
        .execute()
    )

    return resultat.data or []


# ============================================================
# RECUPERER UNE FICHE DE POSTE
# ============================================================

def recuperer_poste(id_poste):
    resultat = (
        supabase
        .table("postes")
        .select(
            "id, entreprise, poste, competences, taches, "
            "vip_sir, caces, permis, texte, date_creation"
        )
        .eq("id", id_poste)
        .single()
        .execute()
    )

    return resultat.data


# ============================================================
# AJOUTER UNE CANDIDATURE AU SUIVI
# ============================================================

def ajouter_suivi(
    agence,
    candidat,
    entreprise,
    poste,
    statut,
    type_entreprise,
):
    return enregistrer_suivi(
        agence,
        candidat,
        entreprise,
        poste,
        statut,
        type_entreprise,
    )


# ============================================================
# LISTER LE SUIVI
# ============================================================

def lister_suivi(agence):
    resultat = (
        supabase
        .table("suivi")
        .select(
            "id, candidat, entreprise, poste, statut, "
            "type_entreprise, date_creation"
        )
        .eq("agence", agence)
        .order("date_creation", desc=True)
        .execute()
    )

    return resultat.data or []


# ============================================================
# MODIFIER LE STATUT D'UNE CANDIDATURE
# ============================================================

def modifier_statut_suivi(suivi_id, nouveau_statut):
    resultat = (
        supabase
        .table("suivi")
        .update({"statut": nouveau_statut})
        .eq("id", suivi_id)
        .execute()
    )

    return resultat.data or []


# ============================================================
# RECUPERER UN CV
# ============================================================

def recuperer_cv(id_cv):
    resultat = (
        supabase
        .table("cv")
        .select(
            "id, candidat, metier, competences, taches, "
            "caces, permis, type_profil, texte"
        )
        .eq("id", id_cv)
        .single()
        .execute()
    )

    return resultat.data


# ============================================================
# SUPPRIMER UN CV
# ============================================================

def supprimer_cv(id_cv):
    return (
        supabase
        .table("cv")
        .delete()
        .eq("id", id_cv)
        .execute()
    )


# ============================================================
# SUPPRIMER UNE FICHE DE POSTE
# ============================================================

def supprimer_poste(id_poste):
    return (
        supabase
        .table("postes")
        .delete()
        .eq("id", id_poste)
        .execute()
    )


# ============================================================
# STATISTIQUES PAR JOUR
# ============================================================

def statistiques_par_semaine(agence):
    resultat = (
        supabase
        .table("suivi")
        .select("date_creation")
        .eq("agence", agence)
        .order("date_creation", desc=True)
        .execute()
    )

    lignes = resultat.data or []

    statistiques = {}

    for ligne in lignes:
        date_creation = ligne.get("date_creation")

        if not date_creation:
            continue

        jour = str(date_creation)[:10]

        statistiques[jour] = statistiques.get(jour, 0) + 1

    return list(statistiques.items())
