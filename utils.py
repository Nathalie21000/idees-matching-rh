import pdfplumber
import docx
import re


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word (.docx).

    Pour un PDF :
    - lecture du texte natif avec pdfplumber.

    Pour un DOCX :
    - lecture des paragraphes ;
    - lecture des tableaux.

    Le texte retourné conserve les retours à la ligne afin
    de permettre l'analyse des rubriques de fiches de poste.
    """

    nom_fichier = getattr(file, "name", "") or ""
    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):
        texte = extraire_texte_docx(file)

    elif nom_fichier_min.endswith(".pdf"):
        texte = extraire_texte_pdf(file)

    else:
        texte = ""

    return nettoyer_texte(texte)


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte d'un PDF page par page.

    Important :
    pdfplumber ne fait PAS d'OCR.
    Un PDF constitué uniquement d'images/scans pourra donc
    retourner très peu ou pas de texte.
    """

    texte_pages = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text()

                if texte_page:
                    texte_pages.append(texte_page)

    except Exception:
        return ""

    return "\n".join(texte_pages)


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le contenu d'un document Word .docx.

    Les paragraphes ET les tableaux sont lus.
    """

    morceaux = []

    try:

        document = docx.Document(file)

        # ----------------------------
        # Paragraphes
        # ----------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

        # ----------------------------
        # Tableaux
        # ----------------------------

        for table in document.tables:

            for ligne in table.rows:

                cellules = []

                for cellule in ligne.cells:

                    texte_cellule = cellule.text.strip()

                    if texte_cellule:
                        cellules.append(texte_cellule)

                if cellules:
                    morceaux.append(" | ".join(cellules))

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoie légèrement le texte sans supprimer les retours
    à la ligne.

    C'est volontaire :
    l'analyse des fiches de poste a besoin de connaître
    les différentes lignes et rubriques.
    """

    if not texte:
        return ""

    # Normalisation des retours à la ligne
    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    # Espaces insécables
    texte = texte.replace("\xa0", " ")

    # Plusieurs espaces -> un seul
    texte = re.sub(r"[ \t]+", " ", texte)

    # Plusieurs lignes vides -> une seule
    texte = re.sub(r"\n\s*\n+", "\n\n", texte)

    return texte.strip()


# ============================================================
# LECTURE CIBLEE DE LA FICHE DE POSTE
# (uniquement : entreprise, intitulé du poste, tâches)
# ============================================================

LIBELLES_CIBLES = {
    "entreprise": r"nom\s+de\s+l['’]entreprise\s*:?",
    "poste": r"intitulé\s+du\s+poste\s*:?",
    "taches": r"liste\s+des\s+tâches\s+propos[ée]es\s*:?",
}


def _capturer_lignes_apres_libelle(texte, motif_libelle, autres_motifs):
    """
    Cherche un libellé dans le texte et renvoie la (ou les)
    ligne(s) qui suivent, jusqu'à une ligne vide ou jusqu'à
    ce qu'une AUTRE rubrique ciblée soit rencontrée.
    """

    correspondance = re.search(
        motif_libelle,
        texte,
        flags=re.IGNORECASE,
    )

    if not correspondance:
        return []

    apres = texte[correspondance.end():]

    lignes_capturees = []

    for ligne in apres.split("\n"):

        ligne_nettoyee = ligne.strip()

        if not ligne_nettoyee:

            if lignes_capturees:
                break

            continue

        est_une_autre_rubrique = False

        for motif in autres_motifs:

            if re.match(
                motif,
                ligne_nettoyee,
                flags=re.IGNORECASE,
            ):
                est_une_autre_rubrique = True
                break

        if est_une_autre_rubrique:
            break

        lignes_capturees.append(ligne_nettoyee)

        if len(lignes_capturees) >= 8:
            break

    return lignes_capturees


def extraire_fiche_poste_ciblee(texte):
    """
    Recherche UNIQUEMENT 3 informations dans la fiche de
    poste, à partir de la structure connue du formulaire
    ID'EES INTERIM :

    - Nom de l'entreprise
    - Intitulé du poste
    - Liste des tâches proposées

    Aucune autre rubrique n'est devinée. Si une information
    n'est pas trouvée, le champ correspondant reste vide et
    le drapeau "_trouvee"/"_trouve" associé passe à False —
    à l'appelant de prévenir l'utilisateur plutôt que
    d'inventer une valeur.
    """

    resultat_vide = {
        "entreprise": "",
        "poste": "",
        "taches": "",
        "entreprise_trouvee": False,
        "poste_trouve": False,
        "taches_trouvees": False,
    }

    if not texte:
        return resultat_vide

    tous_motifs = list(LIBELLES_CIBLES.values())

    lignes_entreprise = _capturer_lignes_apres_libelle(
        texte,
        LIBELLES_CIBLES["entreprise"],
        tous_motifs,
    )

    lignes_poste = _capturer_lignes_apres_libelle(
        texte,
        LIBELLES_CIBLES["poste"],
        tous_motifs,
    )

    lignes_taches = _capturer_lignes_apres_libelle(
        texte,
        LIBELLES_CIBLES["taches"],
        tous_motifs,
    )

    # Entreprise et intitulé de poste : une seule ligne suffit
    entreprise = lignes_entreprise[0] if lignes_entreprise else ""
    poste = lignes_poste[0] if lignes_poste else ""

    # Tâches : on garde chaque ligne, séparées par des virgules
    # (format attendu par le moteur de matching)
    taches = ", ".join(lignes_taches)

    return {
        "entreprise": entreprise,
        "poste": poste,
        "taches": taches,
        "entreprise_trouvee": bool(entreprise),
        "poste_trouve": bool(poste),
        "taches_trouvees": bool(taches),
    }


# ============================================================
# GÉNÉRATION DE PRÉSENTATION CANDIDAT
# ============================================================

def generer_presentation(
    candidat,
    metier,
    competences,
    caces,
    permis,
    entreprise,
    agence
):
    """
    Génère la présentation d'un candidat destinée
    à l'entreprise cliente.
    """

    texte = f"""
Objet : Proposition de candidature – {metier}

Bonjour,

Suite à votre recherche, nous avons le plaisir de vous proposer la candidature de {candidat}.

Son profil présente plusieurs atouts :

- Métier : {metier}

- Compétences : {competences}

- CACES : {caces if caces else "Non renseigné"}

- Permis : {permis if permis else "Non renseigné"}

Ce candidat semble correspondre aux critères recherchés pour votre besoin.

Nous restons à votre disposition pour toute information complémentaire ou pour organiser une rencontre.

Cordialement,

ID'EES Intérim
Agence de {agence}
"""

    return texte.strip()
