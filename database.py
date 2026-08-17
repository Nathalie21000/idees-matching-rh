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
    Cette fonction est conservée pour que app.py
    puisse continuer à appeler init_db().
    """
    return None


# ============================================================
# CONNEXION
# ============================================================

def get_connection():
    """
    Retourne la connexion Supabase.
    """
    return supabase


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
    }

 resultat = supabase.table("cv").insert(donnees).execute()

if not resultat.data:
    raise RuntimeError(
        f"Supabase n'a retourné aucune donnée après l'enregistrement du CV : {resultat}"
    )

return resultat


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
):
    donnees = {
        "agence": agence,
        "entreprise": entreprise,
        "poste": poste,
        "competences": competences,
        "caces": caces,
        "permis": permis,
        "texte": texte,
    }

    return supabase.table("postes").insert(donnees).execute()


# ============================================================
# ENREGISTREMENT DU SUIVI
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

    return supabase.table("suivi").insert(donnees).execute()


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
# COMPTER LE SUIVI PAR STATUT
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
# LISTER LES CV
# ============================================================

def lister_cv(agence):
    resultat = (
        supabase
        .table("cv")
        .select(
            "id, candidat, metier, competences, "
            "caces, permis, type_profil, date_creation"
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
            "id, candidat, texte, metier, competences, "
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
            "id, entreprise, poste, competences, "
            "caces, permis, texte"
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
            "id, entreprise, poste, competences, "
            "caces, permis, texte"
        )
        .eq("id", id_poste)
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
# STATISTIQUES
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

        semaine = str(date_creation)[:10]

        statistiques[semaine] = statistiques.get(semaine, 0) + 1

    return list(statistiques.items())
