"""
Utilitaires d'extraction PDF / DOCX.

Version V9 :
- conserve les retours à la ligne ;
- ne transforme plus le texte en minuscules avant l'analyse ;
- lecture PDF texte avec pdfplumber ;
- lecture DOCX paragraphes + tableaux ;
- extraction structurée du modèle de fiche de poste ;
- préparation pour l'OCR ultérieur.
"""

import io
import re
import unicodedata

import pdfplumber
import docx

from metiers import analyser_fiche_poste


# ============================================================
# NORMALISATION
# ============================================================

def normaliser_texte(texte):
    """Nettoie un texte sans détruire sa structure ligne par ligne."""
    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    texte = texte.replace("\xa0", " ")

    lignes = []
    for ligne in texte.split("\n"):
        ligne = re.sub(r"[ \t]+", " ", ligne).strip()
        lignes.append(ligne)

    return "\n".join(lignes).strip()


def nettoyer_texte(texte):
    """
    Ancienne fonction conservée pour compatibilité.
    Elle nettoie sans mettre le texte en minuscules et sans supprimer
    les retours à la ligne.
    """
    return normaliser_texte(texte)


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """Extrait le texte d'un PDF en conservant autant que possible les lignes."""
    texte_pages = []

    try:
        file.seek(0)
    except Exception:
        pass

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texte_page = page.extract_text(
                x_tolerance=2,
                y_tolerance=3,
                layout=True,
            ) or ""

            if texte_page:
                texte_pages.append(texte_page)

    return normaliser_texte("\n\n".join(texte_pages))


def _extraire_mots_pdf(file):
    """
    Extrait les mots avec leurs coordonnées.
    Utile pour les formulaires en colonnes.
    """
    try:
        file.seek(0)
    except Exception:
        pass

    pages = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            mots = page.extract_words(
                x_tolerance=2,
                y_tolerance=3,
                keep_blank_chars=False,
            )
            pages.append((page, mots))

    return pages


# ============================================================
# EXTRACTION DOCX
# ============================================================

def extraire_texte_docx(file):
    """
    Lit paragraphes et tableaux.
    Chaque cellule est conservée sur ses propres lignes.
    """
    try:
        file.seek(0)
    except Exception:
        pass

    document = docx.Document(file)
    morceaux = []

    for paragraphe in document.paragraphs:
        if paragraphe.text and paragraphe.text.strip():
            morceaux.append(paragraphe.text.strip())

    for table in document.tables:
        for ligne in table.rows:
            cellules = []
            for cellule in ligne.cells:
                contenu = cellule.text.strip()
                if contenu:
                    cellules.append(contenu)

            if cellules:
                morceaux.append("\n".join(cellules))

    return normaliser_texte("\n".join(morceaux))


# ============================================================
# EXTRACTION GENERALE
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un PDF ou DOCX.

    PDF scanné :
    si aucun texte n'est disponible, la fonction retourne "".
    L'OCR sera ajouté dans une étape séparée afin de ne pas casser
    la version actuelle.
    """
    nom_fichier = getattr(file, "name", "") or ""
    extension = nom_fichier.lower().rsplit(".", 1)[-1] if "." in nom_fichier else ""

    if extension == "docx":
        return extraire_texte_docx(file)

    if extension == "pdf":
        return extraire_texte_pdf(file)

    # Compatibilité : tenter le PDF par défaut.
    return extraire_texte_pdf(file)


# ============================================================
# FICHE DE POSTE STRUCTUREE
# ============================================================

def extraire_fiche_poste(file):
    """
    Extrait puis analyse une fiche de poste.

    Pour le modèle texte/DOCX :
        texte -> analyse structurée.

    Pour un PDF :
        on tente d'abord le texte PDF.
        Si le PDF contient du texte, on utilise la même analyse structurée.

    Cette fonction est volontairement séparée de extract_text afin de
    pouvoir ajouter l'OCR ensuite sans modifier app.py.
    """
    texte = extract_text(file)

    if not texte:
        return {
            "texte": "",
            "analyse": analyser_fiche_poste(""),
            "ocr_necessaire": True,
        }

    return {
        "texte": texte,
        "analyse": analyser_fiche_poste(texte),
        "ocr_necessaire": False,
    }


# ============================================================
# PRESENTATION CANDIDAT
# ============================================================

def generer_presentation(
    candidat,
    metier,
    competences,
    caces,
    permis,
    entreprise,
    agence,
):
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
