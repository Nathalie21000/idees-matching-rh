"""
Utilitaires d'extraction PDF / DOCX.

Version spéciale pour la fiche de poste ID'EES INTERIM.

Le formulaire PDF utilisé par l'agence est un PDF interactif :
- Texte 01 = Nom de l'entreprise
- Texte 02 = Intitulé du poste
- Texte 03 = Liste des tâches proposées

On lit directement les champs du formulaire lorsque ceux-ci
sont présents. C'est beaucoup plus fiable que de deviner les
valeurs à partir du texte extrait.
"""

import io
import re

import pdfplumber
import docx
from pypdf import PdfReader

from metiers import analyser_fiche_poste


# ============================================================
# NORMALISATION
# ============================================================

def normaliser_texte(texte):
    """Nettoie le texte sans supprimer les retours à la ligne."""

    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")
    texte = texte.replace("\xa0", " ")

    lignes = []

    for ligne in texte.split("\n"):

        ligne = re.sub(
            r"[ \t]+",
            " ",
            ligne,
        ).strip()

        lignes.append(ligne)

    return "\n".join(lignes).strip()


def nettoyer_texte(texte):
    """Compatibilité avec les anciennes versions de utils.py."""
    return normaliser_texte(texte)


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """Extrait le texte natif du PDF."""

    try:
        file.seek(0)
    except Exception:
        pass

    texte_pages = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                    layout=True,
                ) or ""

                if texte_page:
                    texte_pages.append(texte_page)

    except Exception:

        return ""

    return normaliser_texte(
        "\n\n".join(texte_pages)
    )


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """Extrait les paragraphes et tableaux d'un DOCX."""

    try:
        file.seek(0)
    except Exception:
        pass

    morceaux = []

    try:

        document = docx.Document(file)

        # Paragraphes
        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

        # Tableaux
        for table in document.tables:

            for ligne in table.rows:

                for cellule in ligne.cells:

                    contenu = cellule.text.strip()

                    if contenu:

                        for sous_ligne in contenu.splitlines():

                            sous_ligne = sous_ligne.strip()

                            if sous_ligne:
                                morceaux.append(
                                    sous_ligne
                                )

    except Exception:

        return ""

    return normaliser_texte(
        "\n".join(morceaux)
    )


# ============================================================
# EXTRACTION GENERALE
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un PDF ou d'un DOCX.
    """

    nom_fichier = getattr(
        file,
        "name",
        "",
    ) or ""

    extension = (
        nom_fichier.lower().rsplit(".", 1)[-1]
        if "." in nom_fichier
        else ""
    )

    if extension == "docx":

        return extraire_texte_docx(file)

    if extension == "pdf":

        return extraire_texte_pdf(file)

    return ""


# ============================================================
# LECTURE DES CHAMPS DU FORMULAIRE PDF ID'EES
# ============================================================

def _valeur_champ_pdf(
    reader,
    nom_champ,
):
    """
    Retourne la valeur d'un champ AcroForm PDF.
    """

    try:

        champs = reader.get_fields() or {}

        champ = champs.get(nom_champ)

        if not champ:
            return ""

        valeur = champ.get("/V")

        if valeur is None:
            return ""

        return str(valeur).strip()

    except Exception:

        return ""


def _lire_formulaire_idees(file):
    """
    Lit directement les champs texte du formulaire
    ID'EES INTERIM.

    Correspondance vérifiée sur le formulaire :

        Texte 01 = entreprise
        Texte 02 = poste
        Texte 03 = tâches
    """

    resultat = {
        "entreprise": "",
        "poste": "",
        "taches": "",
    }

    try:

        file.seek(0)

        contenu = file.read()

        file.seek(0)

        reader = PdfReader(
            io.BytesIO(contenu)
        )

        resultat["entreprise"] = (
            _valeur_champ_pdf(
                reader,
                "Texte 01",
            )
        )

        resultat["poste"] = (
            _valeur_champ_pdf(
                reader,
                "Texte 02",
            )
        )

        resultat["taches"] = (
            _valeur_champ_pdf(
                reader,
                "Texte 03",
            )
        )

    except Exception:

        return resultat

    return resultat


# ============================================================
# FALLBACK POUR PDF APLATI
# ============================================================

def _extraire_champ_par_zone_pdf(
    file,
    champ,
):
    """
    Fallback si le PDF a été aplati.

    Les coordonnées correspondent au formulaire
    GJP-A-019-07 que nous avons retrouvé.
    """

    zones = {

        # x0, y0, x1, y1
        "entreprise": (
            32,
            669,
            252,
            698,
        ),

        "poste": (
            31,
            609,
            251,
            639,
        ),

        "taches": (
            271,
            612,
            562,
            694,
        ),
    }

    if champ not in zones:
        return ""

    x0, y0, x1, y1 = zones[champ]

    try:

        file.seek(0)

        with pdfplumber.open(file) as pdf:

            page = pdf.pages[0]

            top = page.height - y1
            bottom = page.height - y0

            mots = page.extract_words(
                x_tolerance=2,
                y_tolerance=3,
                keep_blank_chars=False,
            )

            mots_zone = []

            for mot in mots:

                if (
                    mot["x1"] >= x0
                    and mot["x0"] <= x1
                    and mot["bottom"] >= top
                    and mot["top"] <= bottom
                ):
                    mots_zone.append(mot)

            if not mots_zone:
                return ""

            lignes = []

            ligne_courante = []

            dernier_top = None

            for mot in sorted(
                mots_zone,
                key=lambda m: (
                    m["top"],
                    m["x0"],
                ),
            ):

                if (
                    dernier_top is not None
                    and abs(
                        mot["top"]
                        - dernier_top
                    ) > 5
                ):

                    if ligne_courante:

                        lignes.append(
                            " ".join(
                                ligne_courante
                            )
                        )

                    ligne_courante = []

                ligne_courante.append(
                    mot["text"]
                )

                dernier_top = mot["top"]

            if ligne_courante:

                lignes.append(
                    " ".join(
                        ligne_courante
                    )
                )

            return "\n".join(
                ligne.strip()
                for ligne in lignes
                if ligne.strip()
            ).strip()

    except Exception:

        return ""


# ============================================================
# ANALYSE CLASSIQUE POUR AUTRES DOCUMENTS
# ============================================================

def _analyse_fallback_texte(texte):

    try:

        return analyser_fiche_poste(
            texte
        )

    except Exception:

        return {
            "entreprise": "",
            "intitule": "",
            "taches": "",
            "competences": "",
            "vip_sir": "",
        }


# ============================================================
# EXTRACTION FICHE DE POSTE
# ============================================================

def extraire_fiche_poste(file):
    """
    Extrait une fiche de poste.

    Pour le formulaire PDF ID'EES :
    lecture directe des champs Texte 01, Texte 02 et Texte 03.

    Si le PDF a été aplati :
    lecture des zones correspondant aux champs.

    Pour un DOCX :
    analyse textuelle classique.

    IMPORTANT :
    on ne déduit plus les compétences, CACES ou permis
    à partir de tout le texte de la fiche ID'EES.
    """

    nom_fichier = getattr(
        file,
        "name",
        "",
    ) or ""

    extension = (
        nom_fichier.lower().rsplit(
            ".",
            1,
        )[-1]
        if "." in nom_fichier
        else ""
    )

    # ========================================================
    # PDF
    # ========================================================

    if extension == "pdf":

        champs = _lire_formulaire_idees(
            file
        )

        entreprise = (
            champs["entreprise"].strip()
        )

        poste = (
            champs["poste"].strip()
        )

        taches = (
            champs["taches"].strip()
        )

        # ----------------------------------------------------
        # FALLBACK SI CHAMPS VIDES
        # ----------------------------------------------------

        if not entreprise:

            entreprise = (
                _extraire_champ_par_zone_pdf(
                    file,
                    "entreprise",
                )
            )

        if not poste:

            poste = (
                _extraire_champ_par_zone_pdf(
                    file,
                    "poste",
                )
            )

        if not taches:

            taches = (
                _extraire_champ_par_zone_pdf(
                    file,
                    "taches",
                )
            )

        texte = extract_text(file)

        # ----------------------------------------------------
        # SI ON A TROUVE AU MOINS UN DES 3 CHAMPS
        # ----------------------------------------------------

        if (
            entreprise
            or poste
            or taches
        ):

            texte_cible = (
                "Nom de l'entreprise\n"
                + entreprise
                + "\n\n"
                + "Intitulé du poste\n"
                + poste
                + "\n\n"
                + "Liste des tâches proposées\n"
                + taches
            ).strip()

            analyse = {

                "entreprise": entreprise,

                "intitule": poste,

                "taches": taches,

                # Volontairement vide.
                "competences": "",

                "vip_sir": "",
            }

            return {
                "texte": (
                    texte_cible
                    if texte_cible
                    else texte
                ),

                "analyse": analyse,

                "ocr_necessaire": False,
            }

    # ========================================================
    # DOCX / AUTRE FALLBACK
    # ========================================================

    texte = extract_text(file)

    if not texte:

        return {

            "texte": "",

            "analyse": (
                _analyse_fallback_texte("")
            ),

            "ocr_necessaire": True,
        }

    analyse = (
        _analyse_fallback_texte(
            texte
        )
    )

    return {

        "texte": texte,

        "analyse": analyse,

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
    """
    Génère la présentation d'un candidat.
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
