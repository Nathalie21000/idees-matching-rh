import sqlite3

DB_NAME = "assorti.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------
    # TABLE CV
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cv(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agence TEXT,
        nom_fichier TEXT,
        candidat TEXT,
        metier TEXT,
        competences TEXT,
        caces TEXT,
        permis TEXT,
        texte TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ----------------------------
    # TABLE POSTES
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS postes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agence TEXT,
        entreprise TEXT,
        poste TEXT,
        competences TEXT,
        caces TEXT,
        permis TEXT,
        texte TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ----------------------------
    # TABLE SUIVI
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suivi(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agence TEXT,
        candidat TEXT,
        entreprise TEXT,
        poste TEXT,
        statut TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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
    texte
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cv(
        agence,
        nom_fichier,
        candidat,
        metier,
        competences,
        caces,
        permis,
        texte
    )
    VALUES(?,?,?,?,?,?,?,?)
    """, (
        agence,
        nom_fichier,
        candidat,
        metier,
        competences,
        caces,
        permis,
        texte
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

    cursor.execute("""
    INSERT INTO postes(
        agence,
        entreprise,
        poste,
        competences,
        caces,
        permis,
        texte
    )
    VALUES(?,?,?,?,?,?,?)
    """, (
        agence,
        entreprise,
        poste,
        competences,
        caces,
        permis,
        texte
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
        "SELECT COUNT(*) FROM suivi WHERE agence=? AND statut=?",
        (agence, statut)
    )

    nb = cursor.fetchone()[0]

    conn.close()

    return nb
