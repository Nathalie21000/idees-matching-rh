import sqlite3
from datetime import datetime


DB_NAME = "assorti.db"


# ----------------------------
# CONNEXION À LA BASE
# ----------------------------

def get_connection():
    return sqlite3.connect(DB_NAME)


# ----------------------------
# AJOUT AUTOMATIQUE DES COLONNES
# MANQUANTES
# ----------------------------

def ajouter_colonne_si_absente(cursor, table, colonne, type_colonne="TEXT"):

    cursor.execute(f"PRAGMA table_info({table})")
    colonnes_existantes = [ligne[1] for ligne in cursor.fetchall()]

    if colonne not in colonnes_existantes:
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {colonne} {type_colonne}"
        )


# ----------------------------
# INITIALISATION DE LA BASE
# ----------------------------

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------
    # TABLE CV
    # ----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agence TEXT,
            nom_fichier TEXT,
            candidat TEXT,
            metier TEXT,
            competences TEXT,
            caces TEXT,
            permis TEXT,
            type_profil TEXT,
            texte TEXT,
            date_creation TEXT
        )
    """)

    # ----------------------------
    # TABLE POSTES
    # ----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agence TEXT,
            entreprise TEXT,
            poste TEXT,
            competences TEXT,
            caces TEXT,
            permis TEXT,
            texte TEXT,
            date_creation TEXT
        )
    """)

    # ----------------------------
    # TABLE SUIVI
    # ----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suivi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agence TEXT,
            candidat TEXT,
            entreprise TEXT,
            poste TEXT,
            statut TEXT,
            type_entreprise TEXT,
            date_creation TEXT
        )
    """)

    # ----------------------------
    # MIGRATION TABLE CV
    # ----------------------------

    ajouter_colonne_si_absente(
        cursor, "cv", "agence"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "nom_fichier"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "candidat"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "metier"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "competences"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "caces"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "permis"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "type_profil"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "texte"
    )

    ajouter_colonne_si_absente(
        cursor, "cv", "date_creation"
    )

    # ----------------------------
    # MIGRATION TABLE POSTES
    # ----------------------------

    ajouter_colonne_si_absente(
        cursor, "postes", "agence"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "entreprise"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "poste"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "competences"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "caces"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "permis"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "texte"
    )

    ajouter_colonne_si_absente(
        cursor, "postes", "date_creation"
    )

    # ----------------------------
    # MIGRATION TABLE SUIVI
    # ----------------------------

    ajouter_colonne_si_absente(
        cursor, "suivi", "agence"
    )

    ajouter_colonne_si_absente(
        cursor, "suivi", "candidat"
    )

    ajouter_colonne_si_absente(
        cursor, "suivi", "entreprise"
    )

    ajouter_colonne_si_absente(
        cursor, "suivi", "poste"
    )

    ajouter_colonne_si_absente(
        cursor, "suivi", "statut"
    )

    ajouter_colonne_si_absente(
        cursor, "suivi", "type_entreprise"
    )

    ajouter_colonne_si_absente(
        cursor, "suivi", "date_creation"
    )

    conn.commit()
    conn.close()


# ----------------------------
# ENREGISTREMENT CV
# ----------------------------

def enregistrer_cv(
    agence,
    nom_fichier,
    candidat,
    metier,
    competences,
    caces,
    permis,
    type_profil,
    texte
):

    conn = get_connection()
    cursor = conn.cursor()

    date_creation = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO cv (
            agence,
            nom_fichier,
            candidat,
            metier,
            competences,
            caces,
            permis,
            type_profil,
            texte,
            date_creation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agence,
        nom_fichier,
        candidat,
        metier,
        competences,
        caces,
        permis,
        type_profil,
        texte,
        date_creation
    ))

    conn.commit()
    conn.close()


# ----------------------------
# ENREGISTREMENT POSTE
# ----------------------------

def enregistrer_poste(
    agence,
    entreprise,
    poste,
    competences,
    caces,
    permis,
    texte
):

    conn = get_connection()
    cursor = conn.cursor()

    date_creation = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO postes (
            agence,
            entreprise,
            poste,
            competences,
            caces,
            permis,
            texte,
            date_creation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agence,
        entreprise,
        poste,
        competences,
        caces,
        permis,
        texte,
        date_creation
    ))

    conn.commit()
    conn.close()


# ----------------------------
# TABLEAU DE BORD
# ----------------------------

def compter_cv(agence):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM cv WHERE agence=?",
        (agence,)
    )

    nb = cursor.fetchone()[0]

    conn.close()

    return nb


def compter_postes(agence):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM postes WHERE agence=?",
        (agence,)
    )

    nb = cursor.fetchone()[0]

    conn.close()

    return nb


def compter_suivi(agence, statut):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM suivi
        WHERE agence=? AND statut=?
        """,
        (agence, statut)
    )

    nb = cursor.fetchone()[0]

    conn.close()

    return nb


# ----------------------------
# LISTE DES CV
# ----------------------------

def lister_cv(agence):

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
            type_profil,
            date_creation
        FROM cv
        WHERE agence=?
        ORDER BY date_creation DESC
    """, (agence,))

    resultats = cursor.fetchall()

    conn.close()

    return resultats


# ----------------------------
# SUPPRESSION CV
# ----------------------------

def supprimer_cv(id_cv):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cv WHERE id=?",
        (id_cv,)
    )

    conn.commit()
    conn.close()


# ----------------------------
# STATISTIQUES HEBDOMADAIRES
# ----------------------------

def statistiques_par_semaine(agence):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            strftime('%Y-%W', date_creation) AS semaine,
            COUNT(*)
        FROM suivi
        WHERE agence=?
        GROUP BY semaine
        ORDER BY semaine DESC
    """, (agence,))

    resultat = cursor.fetchall()

    conn.close()

    return resultat
