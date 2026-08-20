"""
Utilitaires d'extraction PDF / DOCX.

Version V10

Objectif principal :
- lire correctement notre modèle de fiche de poste ID'EES INTERIM ;
- récupérer directement les champs Acrobat du PDF :
    Texte 01 = Nom de l'entreprise
    Texte 02 = Intitulé du poste
    Texte 03 = Liste des tâches proposées
- ne plus confondre les libellés des deux colonnes ;
- conserver une extraction classique pour les autres PDF et les DOCX.
"""

import re

import pdfplumber
import docx

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from metiers import analyser_fiche_poste


# ============================================================
# NORMALISATION
# ============================================================

def normaliser_texte(texte):
    """
    Nettoie le texte sans détruire les retours à la ligne.
    """
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
    """
    Fonction conservée pour compatibilité avec l'ancien code.
    """
    return normaliser_texte(texte)


# ============================================================
# EXTRACTION PDF CLASSIQUE
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte d'un PDF classique.

    On conserve la mise en page autant que possible afin
    de ne pas mélanger les différentes rubriques.
    """

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
                texte_pages.append(
                    texte_page
                )

    return normaliser_texte(
        "\n\n".join(texte_pages)
    )


# ============================================================
# EXTRACTION DOCX
# ============================================================

def extraire_texte_docx(file):
    """
    Lit les paragraphes et les tableaux d'un fichier Word.
    """

    try:
        file.seek(0)
    except Exception:
        pass

    document = docx.Document(file)

    morceaux = []

    # Paragraphes
    for paragraphe in document.paragraphs:

        texte = paragraphe.text.strip()

        if texte:
            morceaux.append(
                texte
            )

    # Tableaux
    for table in document.tables:

        for ligne in table.rows:

            cellules = []

            for cellule in ligne.cells:

                contenu = cellule.text.strip()

                if contenu:
                    cellules.append(
                        contenu
                    )

            if cellules:

                morceaux.append(
                    "\n".join(cellules)
                )

    return normaliser_texte(
        "\n".join(morceaux)
    )


# ============================================================
# LECTURE DES CHAMPS ACROBAT DU MODELE ID'EES
# ============================================================

def _lire_champs_acrobat_fiche_poste(file):
    """
    Lit directement les champs de formulaire du modèle
    PDF ID'EES INTERIM.

    Dans notre modèle :

        Texte 01 = Nom de l'entreprise
        Texte 02 = Intitulé du poste
        Texte 03 = Liste des tâches proposées

    Cette méthode est prioritaire car elle évite totalement
    les problèmes liés aux deux colonnes du formulaire.
    """

    resultat = {
        "entreprise": "",
        "intitule": "",
        "taches": "",
    }

    if PdfReader is None:
        return resultat

    try:
        file.seek(0)

        lecteur = PdfReader(file)

        champs = lecteur.get_fields()

        if not champs:
            return resultat

        # ----------------------------------------------------
        # Nom de l'entreprise
        # ----------------------------------------------------

        champ_entreprise = champs.get(
            "Texte 01"
        )

        if champ_entreprise:

            valeur = champ_entreprise.get(
                "/V"
            )

            if valeur is not None:

                resultat["entreprise"] = str(
                    valeur
                ).strip()

        # ----------------------------------------------------
        # Intitulé du poste
        # ----------------------------------------------------

        champ_intitule = champs.get(
            "Texte 02"
        )

        if champ_intitule:

            valeur = champ_intitule.get(
                "/V"
            )

            if valeur is not None:

                resultat["intitule"] = str(
                    valeur
                ).strip()

        # ----------------------------------------------------
        # Liste des tâches proposées
        # ----------------------------------------------------

        champ_taches = champs.get(
            "Texte 03"
        )

        if champ_taches:

            valeur = champ_taches.get(
                "/V"
            )

            if valeur is not None:

                resultat["taches"] = str(
                    valeur
                ).strip()

    except Exception:
        # On ne fait pas planter l'application si le PDF
        # n'est pas un formulaire Acrobat.
        pass

    return resultat


# ============================================================
# EXTRACTION DE SECOURS PAR COORDONNEES
# ============================================================

def _extraire_champs_par_coordonnees(file):
    """
    Méthode de secours pour le même modèle de fiche de poste.

    Si le PDF a été aplati et que les champs Acrobat ne sont
    plus disponibles, on récupère les trois zones correspondant
    aux emplacements du modèle.

    Cette méthode ne dépend donc pas de la lecture linéaire
    des deux colonnes.
    """

    resultat = {
        "entreprise": "",
        "intitule": "",
        "taches": "",
    }

    try:
        file.seek(0)

        with pdfplumber.open(file) as pdf:

            if not pdf.pages:
                return resultat

            page = pdf.pages[0]

            largeur = page.width
            hauteur = page.height

            # ------------------------------------------------
            # NOM DE L'ENTREPRISE
            #
            # Zone du champ Texte 01 du modèle
            # ------------------------------------------------

            zone_entreprise = page.crop(
                (
                    25,
                    142,
                    min(260, largeur),
                    185,
                )
            )

            texte_entreprise = (
                zone_entreprise.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                )
                or ""
            )

            # ------------------------------------------------
            # INTITULE
            #
            # Zone du champ Texte 02
            # ------------------------------------------------

            zone_intitule = page.crop(
                (
                    25,
                    200,
                    min(260, largeur),
                    245,
                )
            )

            texte_intitule = (
                zone_intitule.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                )
                or ""
            )

            # ------------------------------------------------
            # LISTE DES TACHES
            #
            # Zone du champ Texte 03
            # ------------------------------------------------

            zone_taches = page.crop(
                (
                    265,
                    142,
                    min(570, largeur),
                    240,
                )
            )

            texte_taches = (
                zone_taches.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                )
                or ""
            )

            resultat["entreprise"] = (
                normaliser_texte(
                    texte_entreprise
                )
            )

            resultat["intitule"] = (
                normaliser_texte(
                    texte_intitule
                )
            )

            resultat["taches"] = (
                normaliser_texte(
                    texte_taches
                )
            )

    except Exception:
        pass

    return resultat


# ============================================================
# DETECTION DU MODELE ID'EES
# ============================================================

def _extraire_champs_fiche_poste_pdf(file):
    """
    Essaie plusieurs méthodes dans l'ordre :

    1. champs Acrobat du formulaire ;
    2. extraction par coordonnées si le PDF a été aplati.

    On ne tente PAS de deviner les trois informations
    à partir de mots trouvés ailleurs dans le document.
    """

    resultat = {
        "entreprise": "",
        "intitule": "",
        "taches": "",
    }

    # --------------------------------------------------------
    # 1. Champs Acrobat
    # --------------------------------------------------------

    champs = _lire_champs_acrobat_fiche_poste(
        file
    )

    for cle in resultat:

        if champs.get(cle):

            resultat[cle] = champs[cle]

    # --------------------------------------------------------
    # 2. Extraction par coordonnées
    # seulement pour les champs encore vides
    # --------------------------------------------------------

    if (
        not resultat["entreprise"]
        or not resultat["intitule"]
        or not resultat["taches"]
    ):

        coordonnees = _extraire_champs_par_coordonnees(
            file
        )

        for cle in resultat:

            if (
                not resultat[cle]
                and coordonnees.get(cle)
            ):

                resultat[cle] = (
                    coordonnees[cle]
                )

    return resultat


# ============================================================
# EXTRACTION GENERALE
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un PDF ou d'un DOCX.
    """

    nom_fichier = (
        getattr(file, "name", "")
        or ""
    )

    extension = ""

    if "." in nom_fichier:

        extension = (
            nom_fichier
            .lower()
            .rsplit(".", 1)[-1]
        )

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    if extension == "docx":

        return extraire_texte_docx(
            file
        )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == "pdf":

        return extraire_texte_pdf(
            file
        )

    # --------------------------------------------------------
    # Compatibilité ancienne version
    # --------------------------------------------------------

    return extraire_texte_pdf(
        file
    )


# ============================================================
# EXTRACTION COMPLETE D'UNE FICHE DE POSTE
# ============================================================

def extraire_fiche_poste(file):
    """
    Extraction spécialisée pour une fiche de poste.

    Pour notre modèle ID'EES :
        entreprise = champ Texte 01
        intitulé   = champ Texte 02
        tâches     = champ Texte 03

    Pour les autres documents :
        on conserve l'analyse générale.
    """

    nom_fichier = (
        getattr(file, "name", "")
        or ""
    ).lower()

    # ========================================================
    # CAS PDF
    # ========================================================

    if nom_fichier.endswith(".pdf"):

        # ----------------------------------------------------
        # Lire le texte général
        # ----------------------------------------------------

        texte = extraire_texte_pdf(
            file
        )

        # ----------------------------------------------------
        # Lire les trois champs précis du modèle
        # ----------------------------------------------------

        champs = _extraire_champs_fiche_poste_pdf(
            file
        )

        # ----------------------------------------------------
        # Analyse générale uniquement pour les autres
        # informations
        # ----------------------------------------------------

        analyse = analyser_fiche_poste(
            texte
        )

        # ----------------------------------------------------
        # IMPORTANT :
        # Les trois champs du modèle écrasent complètement
        # toute détection générique.
        # ----------------------------------------------------

        analyse["entreprise"] = (
            champs["entreprise"]
        )

        analyse["intitule"] = (
            champs["intitule"]
        )

        analyse["taches"] = (
            champs["taches"]
        )

        # ----------------------------------------------------
        # Les tâches sont également conservées sous forme
        # de liste pour le récapitulatif.
        # ----------------------------------------------------

        if champs["taches"]:

            analyse[
                "taches_par_rubrique"
            ] = {
                "Liste des tâches proposées": [
                    ligne.strip()
                    for ligne
                    in champs["taches"].splitlines()
                    if ligne.strip()
                ]
            }

        else:

            analyse[
                "taches_par_rubrique"
            ] = {}

        # ----------------------------------------------------
        # On ne laisse surtout pas le métier détecté remplacer
        # un intitulé vide du formulaire.
        # ----------------------------------------------------

        if not champs["intitule"]:

            analyse["intitule"] = ""

        return {
            "texte": texte,
            "analyse": analyse,
            "ocr_necessaire": not bool(
                texte
            ),
        }

    # ========================================================
    # CAS DOCX
    # ========================================================

    texte = extract_text(
        file
    )

    if not texte:

        return {
            "texte": "",
            "analyse": analyser_fiche_poste(
                ""
            ),
            "ocr_necessaire": True,
        }

    analyse = analyser_fiche_poste(
        texte
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
