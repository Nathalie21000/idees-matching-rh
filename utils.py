"""
Utilitaires d'extraction PDF / DOCX.

Version V10

Objectifs :
- conserver les retours à la ligne ;
- lire les PDF texte ;
- lire les DOCX et leurs tableaux ;
- lire directement les champs de formulaire du modèle
  de fiche de poste ID'EES INTERIM ;
- utiliser en priorité les champs du formulaire pour :
    * entreprise ;
    * intitulé du poste ;
    * liste des tâches proposées ;
    * conditions particulières ;
    * produits chimiques ;
    * conduite d'engins ;
    * machines / outils ;
    * habilitations ;
- conserver une solution de secours par extraction classique ;
- préparer l'ajout futur de l'OCR pour les PDF scannés.
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
    Nettoie un texte sans détruire sa structure ligne par ligne.
    """

    if not texte:
        return ""

    texte = str(texte)

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")
    texte = texte.replace("\xa0", " ")

    lignes = []

    for ligne in texte.split("\n"):

        ligne = re.sub(
            r"[ \t]+",
            " ",
            ligne,
        )

        ligne = ligne.strip()

        lignes.append(ligne)

    return "\n".join(lignes).strip()


def nettoyer_texte(texte):
    """
    Fonction conservée pour compatibilité avec les anciennes versions.
    """

    return normaliser_texte(texte)


# ============================================================
# OUTILS
# ============================================================

def _nettoyer_valeur_champ(valeur):
    """
    Nettoie la valeur d'un champ PDF.
    """

    if valeur is None:
        return ""

    valeur = str(valeur)

    valeur = valeur.replace("\r\n", "\n")
    valeur = valeur.replace("\r", "\n")
    valeur = valeur.replace("\xa0", " ")

    lignes = []

    for ligne in valeur.split("\n"):

        ligne = re.sub(
            r"[ \t]+",
            " ",
            ligne,
        )

        ligne = ligne.strip()

        if ligne:
            lignes.append(ligne)

    return "\n".join(lignes).strip()


def _texte_non_vide(*valeurs):
    """
    Retourne la première valeur non vide.
    """

    for valeur in valeurs:

        valeur = _nettoyer_valeur_champ(valeur)

        if valeur:
            return valeur

    return ""


# ============================================================
# EXTRACTION PDF CLASSIQUE
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte d'un PDF en conservant autant que possible
    les retours à la ligne.
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
# LECTURE DES CHAMPS DU FORMULAIRE PDF
# ============================================================

def extraire_champs_formulaire_pdf(file):
    """
    Lit les champs de formulaire PDF avec pypdf.

    Le modèle ID'EES INTERIM utilise notamment :

        Texte 01 = Nom de l'entreprise
        Texte 02 = Intitulé du poste
        Texte 03 = Liste des tâches proposées
        Texte 04 = Conditions particulières
        Texte 05 = Utilisation de produits chimiques
        Texte 06 = Conduite d'engins
        Texte 07 = Utilisation de machines / outils
        Texte 08 = Habilitations

    Retourne un dictionnaire vide si les champs ne sont
    pas accessibles.
    """

    if PdfReader is None:
        return {}

    champs = {}

    try:

        try:
            file.seek(0)
        except Exception:
            pass

        lecteur = PdfReader(file)

        champs_pdf = lecteur.get_form_text_fields()

        if not champs_pdf:
            return {}

        for nom, valeur in champs_pdf.items():

            valeur_nettoyee = _nettoyer_valeur_champ(
                valeur
            )

            if valeur_nettoyee:

                champs[
                    str(nom).strip()
                ] = valeur_nettoyee

    except Exception:

        return {}

    return champs


# ============================================================
# EXTRACTION STRUCTUREE DE LA FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_pdf(file):
    """
    Extraction spécifique du modèle de fiche de poste ID'EES INTERIM.

    PRIORITÉ :

    1. Champs de formulaire PDF.
    2. Analyse classique du texte PDF.

    Cela évite que pdfplumber mélange les libellés des différentes
    zones du formulaire.
    """

    texte = extraire_texte_pdf(file)

    champs = extraire_champs_formulaire_pdf(
        file
    )

    analyse_generique = analyser_fiche_poste(
        texte
    )

    # --------------------------------------------------------
    # VALEURS DIRECTEMENT ISSUES DU FORMULAIRE
    # --------------------------------------------------------

    entreprise = _texte_non_vide(
        champs.get("Texte 01"),
        analyse_generique.get("entreprise"),
    )

    intitule = _texte_non_vide(
        champs.get("Texte 02"),
        analyse_generique.get("intitule"),
    )

    taches = _texte_non_vide(
        champs.get("Texte 03"),
        analyse_generique.get("taches"),
    )

    conditions_particulieres = _texte_non_vide(
        champs.get("Texte 04"),
        analyse_generique.get("conditions_particulieres"),
        analyse_generique.get("securite_risques"),
    )

    produits_chimiques = _texte_non_vide(
        champs.get("Texte 05"),
        analyse_generique.get("produits_chimiques"),
    )

    conduite_engins = _texte_non_vide(
        champs.get("Texte 06"),
        analyse_generique.get("conduite_engins"),
    )

    machines_outils = _texte_non_vide(
        champs.get("Texte 07"),
        analyse_generique.get("machines_outils"),
    )

    habilitations = _texte_non_vide(
        champs.get("Texte 08"),
        analyse_generique.get("habilitations"),
    )

    # --------------------------------------------------------
    # VIP / SIR
    # --------------------------------------------------------

    texte_min = texte.lower()

    vip = bool(
        re.search(
            r"\bvip\b",
            texte_min,
        )
    )

    sir = bool(
        re.search(
            r"\bsir\b",
            texte_min,
        )
    )

    if vip and sir:
        vip_sir = "VIP + SIR"

    elif vip:
        vip_sir = "VIP"

    elif sir:
        vip_sir = "SIR"

    else:
        vip_sir = ""

    # --------------------------------------------------------
    # COMPETENCES
    # --------------------------------------------------------
    #
    # IMPORTANT :
    # On ne remplit PAS artificiellement les compétences avec
    # tous les mots trouvés dans la fiche.
    #
    # Cela évite l'ancien problème :
    # BR / ENGINS / HABILITATION / MANUTENTION / etc.
    #
    # Si le modèle possède une vraie zone de compétences dans
    # une future version, on pourra la brancher ici.
    # --------------------------------------------------------

    competences = _texte_non_vide(
        analyse_generique.get("competences")
    )

    # --------------------------------------------------------
    # RESULTAT
    # --------------------------------------------------------

    analyse = dict(
        analyse_generique
    )

    analyse.update(
        {
            "entreprise": entreprise,
            "intitule": intitule,
            "taches": taches,
            "competences": competences,
            "conditions_particulieres":
                conditions_particulieres,
            "produits_chimiques":
                produits_chimiques,
            "conduite_engins":
                conduite_engins,
            "machines_outils":
                machines_outils,
            "habilitations":
                habilitations,
            "vip_sir":
                vip_sir,
            "champs_formulaire":
                champs,
        }
    )

    return {
        "texte": texte,
        "analyse": analyse,
        "champs": champs,
        "ocr_necessaire": not bool(texte),
    }


# ============================================================
# EXTRACTION DOCX
# ============================================================

def extraire_texte_docx(file):
    """
    Lit les paragraphes et les tableaux d'un DOCX.
    """

    try:
        file.seek(0)
    except Exception:
        pass

    document = docx.Document(
        file
    )

    morceaux = []

    # --------------------------------------------------------
    # PARAGRAPHES
    # --------------------------------------------------------

    for paragraphe in document.paragraphs:

        texte = paragraphe.text.strip()

        if texte:

            morceaux.append(
                texte
            )

    # --------------------------------------------------------
    # TABLEAUX
    # --------------------------------------------------------

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
# EXTRACTION GENERALE
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un PDF ou DOCX.

    Pour un PDF :
        lecture avec pdfplumber.

    Pour un DOCX :
        lecture des paragraphes et tableaux.

    Les PDF scannés nécessiteront l'OCR dans une prochaine étape.
    """

    nom_fichier = (
        getattr(
            file,
            "name",
            "",
        )
        or ""
    )

    extension = ""

    if "." in nom_fichier:

        extension = (
            nom_fichier
            .lower()
            .rsplit(
                ".",
                1,
            )[-1]
        )

    if extension == "docx":

        return extraire_texte_docx(
            file
        )

    if extension == "pdf":

        return extraire_texte_pdf(
            file
        )

    # Compatibilité
    return extraire_texte_pdf(
        file
    )


# ============================================================
# FICHE DE POSTE
# ============================================================

def extraire_fiche_poste(file):
    """
    Fonction principale utilisée par app.py.

    Pour un PDF :
        utilise la lecture spécifique du formulaire.

    Pour un DOCX :
        utilise l'extraction classique puis l'analyse structurée.
    """

    nom_fichier = (
        getattr(
            file,
            "name",
            "",
        )
        or ""
    )

    extension = ""

    if "." in nom_fichier:

        extension = (
            nom_fichier
            .lower()
            .rsplit(
                ".",
                1,
            )[-1]
        )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == "pdf":

        resultat = extraire_fiche_poste_pdf(
            file
        )

        return resultat

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    texte = extract_text(
        file
    )

    if not texte:

        return {
            "texte": "",
            "analyse": analyser_fiche_poste(""),
            "champs": {},
            "ocr_necessaire": True,
        }

    return {
        "texte": texte,
        "analyse": analyser_fiche_poste(
            texte
        ),
        "champs": {},
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
    Génère la présentation du candidat.
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
