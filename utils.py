import pdfplumber
import re


def extract_text(file):
    """
    Extrait le texte d'un PDF.
    """

    texte = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texte += page.extract_text() or ""

    return nettoyer_texte(texte)


def nettoyer_texte(texte):
    """
    Nettoyage du texte avant analyse.
    """

    texte = texte.lower()

    texte = texte.replace("\n", " ")

    texte = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9 ]", " ", texte)

    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()
# ----------------------------
# GÉNÉRATION PRÉSENTATION CANDIDAT
# ----------------------------

def generer_presentation(
    candidat,
    metier,
    competences,
    caces,
    permis,
    entreprise,
    agence
):

    texte = f"""
Objet : Proposition de candidature – {metier}

Bonjour,

Suite à votre recherche, nous avons le plaisir de vous proposer la candidature de {candidat}.

Son profil présente plusieurs atouts :

• Métier : {metier}

• Compétences : {competences}

• CACES : {caces if caces else "Non renseigné"}

• Permis : {permis if permis else "Non renseigné"}

Ce candidat semble correspondre aux critères recherchés pour votre besoin.

Nous restons à votre disposition pour toute information complémentaire ou pour organiser une rencontre.

Cordialement,

ID'EES Intérim
Agence de {agence}
"""

    return texte
