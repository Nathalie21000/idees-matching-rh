import pdfplumber
import docx
import re

from pdfplumber.utils.pdfinternals import (
    resolve,
    resolve_and_decode,
)


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word (.docx).

    Pour les PDF :
    - extrait le texte visible ;
    - extrait également les valeurs des champs de formulaire
      PDF lorsque le document en contient.

    Pour les DOCX :
    - extrait les paragraphes ;
    - extrait les tableaux.
    """

    nom_fichier = getattr(file, "name", "") or ""
    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):

        texte = extraire_texte_docx(file)

        return nettoyer_texte(texte)

    elif nom_fichier_min.endswith(".pdf"):

        texte = extraire_texte_pdf(file)

        return nettoyer_texte(texte)

    return ""


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte visible d'un PDF ET les valeurs des
    champs de formulaire PDF.

    Pour notre fiche de poste ID'EES INTERIM, les champs :

    Texte 01 = Nom de l'entreprise
    Texte 02 = Intitulé du poste
    Texte 03 = Liste des tâches proposées
    """

    morceaux = []

    try:

        with pdfplumber.open(file) as pdf:

            # ------------------------------------------------
            # 1. TEXTE VISIBLE
            # ------------------------------------------------

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

                if texte_page:
                    morceaux.append(texte_page)

            # ------------------------------------------------
            # 2. CHAMPS DE FORMULAIRE
            # ------------------------------------------------

            champs = extraire_champs_formulaire(pdf)

            if champs:

                entreprise = champs.get(
                    "Texte 01",
                    ""
                )

                poste = champs.get(
                    "Texte 02",
                    ""
                )

                taches = champs.get(
                    "Texte 03",
                    ""
                )

                # --------------------------------------------
                # ENTREPRISE
                # --------------------------------------------

                if entreprise:

                    morceaux.append(
                        f"Nom de l'entreprise : {entreprise}"
                    )

                # --------------------------------------------
                # POSTE
                # --------------------------------------------

                if poste:

                    morceaux.append(
                        f"Intitulé du poste : {poste}"
                    )

                # --------------------------------------------
                # TACHES
                # --------------------------------------------

                if taches:

                    morceaux.append(
                        "Liste des tâches proposées : "
                        + taches
                    )

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# EXTRACTION DES CHAMPS DE FORMULAIRE PDF
# ============================================================

def extraire_champs_formulaire(pdf):
    """
    Extrait les champs AcroForm du PDF.

    Retourne un dictionnaire contenant notamment :

        Texte 01
        Texte 02
        Texte 03
    """

    resultat = {}

    try:

        catalogue = pdf.doc.catalog

        acro_form = catalogue.get(
            "AcroForm"
        )

        if not acro_form:
            return resultat

        acro_form = resolve(
            acro_form
        )

        champs = acro_form.get(
            "Fields"
        )

        if not champs:
            return resultat

        champs = resolve(
            champs
        )

        def parcourir_champ(
            champ,
            prefix=""
        ):

            champ_resolu = champ.resolve()

            nom = resolve_and_decode(
                champ_resolu.get("T")
            )

            if nom:

                if prefix:

                    nom_complet = (
                        f"{prefix}.{nom}"
                    )

                else:

                    nom_complet = nom

            else:

                nom_complet = prefix

            # --------------------------------------------
            # VALEUR DU CHAMP
            # --------------------------------------------

            valeur = champ_resolu.get(
                "V"
            )

            if valeur is not None:

                try:

                    valeur = resolve_and_decode(
                        valeur
                    )

                except Exception:

                    valeur = str(
                        valeur
                    )

                if valeur is not None:

                    valeur = str(
                        valeur
                    ).strip()

                    if valeur:

                        resultat[
                            nom_complet
                        ] = valeur

            # --------------------------------------------
            # SOUS-CHAMPS
            # --------------------------------------------

            enfants = champ_resolu.get(
                "Kids"
            )

            if enfants:

                for enfant in resolve(
                    enfants
                ):

                    parcourir_champ(
                        enfant,
                        nom_complet
                    )

        for champ in champs:

            parcourir_champ(
                champ
            )

    except Exception:

        return resultat

    return resultat


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

        document = docx.Document(
            file
        )

        # ----------------------------------------------------
        # PARAGRAPHES
        # ----------------------------------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:

                morceaux.append(
                    texte
                )

        # ----------------------------------------------------
        # TABLEAUX
        # ----------------------------------------------------

        for table in document.tables:

            for ligne in table.rows:

                cellules = []

                for cellule in ligne.cells:

                    texte_cellule = (
                        cellule.text.strip()
                    )

                    if texte_cellule:

                        cellules.append(
                            texte_cellule
                        )

                if cellules:

                    morceaux.append(
                        " | ".join(
                            cellules
                        )
                    )

    except Exception:

        return ""

    return "\n".join(
        morceaux
    )


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoie légèrement le texte.

    Les retours à la ligne sont conservés volontairement.
    """

    if not texte:

        return ""

    texte = texte.replace(
        "\r\n",
        "\n"
    )

    texte = texte.replace(
        "\r",
        "\n"
    )

    texte = texte.replace(
        "\xa0",
        " "
    )

    texte = re.sub(
        r"[ \t]+",
        " ",
        texte
    )

    texte = re.sub(
        r"\n\s*\n+",
        "\n\n",
        texte
    )

    return texte.strip()


# ============================================================
# NORMALISATION
# ============================================================

def normaliser_texte(texte):
    """
    Normalise un texte pour faciliter les comparaisons.
    """

    if not texte:

        return ""

    texte = texte.lower()

    texte = texte.replace(
        "’",
        "'"
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte
    )

    return texte.strip()


# ============================================================
# EXTRACTION CIBLEE DE LA FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Extrait uniquement :

    - le nom de l'entreprise ;
    - l'intitulé du poste ;
    - la totalité de la liste des tâches proposées.

    Les tâches peuvent être sur plusieurs lignes.

    Toutes les lignes appartenant à la rubrique
    "Liste des tâches proposées" sont conservées.
    """

    resultat = {
        "entreprise": "",
        "poste": "",
        "taches": "",
        "entreprise_trouvee": False,
        "poste_trouve": False,
        "taches_trouvees": False,
    }

    if not texte:

        return resultat

    # ========================================================
    # ENTREPRISE
    # ========================================================

    correspondance = re.search(
        r"Nom\s+de\s+l['’]entreprise\s*:\s*(.*?)(?=\n|$)",
        texte,
        flags=re.IGNORECASE,
    )

    if correspondance:

        entreprise = (
            correspondance
            .group(1)
            .strip()
        )

        if entreprise:

            resultat["entreprise"] = (
                entreprise
            )

    # ========================================================
    # INTITULE DU POSTE
    # ========================================================

    correspondance = re.search(
        r"Intitul[ée]\s+du\s+poste\s*:\s*(.*?)(?=\n|$)",
        texte,
        flags=re.IGNORECASE,
    )

    if correspondance:

        poste = (
            correspondance
            .group(1)
            .strip()
        )

        if poste:

            resultat["poste"] = (
                poste
            )

    # ========================================================
    # LISTE DES TACHES PROPOSEES
    # ========================================================

    correspondance = re.search(
        r"Liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:\s*(.*)",
        texte,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if correspondance:

        bloc_taches = (
            correspondance
            .group(1)
            .strip()
        )

        # ----------------------------------------------------
        # On recherche une éventuelle rubrique suivante.
        #
        # Cela évite de prendre le reste de la fiche de poste
        # comme faisant partie des tâches.
        # ----------------------------------------------------

        rubriques_suivantes = re.search(
            r"\n\s*(?:"
            r"Conditions\s+de\s+travail"
            r"|Comp[ée]tences"
            r"|CACES"
            r"|Permis"
            r"|Suivi\s+m[ée]dical"
            r"|VIP"
            r"|SIR"
            r"|Horaires"
            r"|R[ée]mun[ée]ration"
            r"|Profil"
            r"|Formation"
            r"|Exp[ée]rience"
            r")\s*:?",
            bloc_taches,
            flags=re.IGNORECASE,
        )

        if rubriques_suivantes:

            bloc_taches = (
                bloc_taches[
                    :rubriques_suivantes.start()
                ]
                .strip()
            )

        # ----------------------------------------------------
        # CONSERVATION DE TOUTES LES LIGNES
        # ----------------------------------------------------

        lignes = []

        for ligne in bloc_taches.splitlines():

            ligne = ligne.strip()

            if not ligne:

                continue

            lignes.append(
                ligne
            )

        # ----------------------------------------------------
        # Toutes les tâches sont conservées.
        #
        # Elles sont séparées par des virgules afin de rester
        # compatibles avec le matching existant.
        # ----------------------------------------------------

        if lignes:

            resultat["taches"] = (
                ", ".join(lignes)
            )

    # ========================================================
    # INDICATEURS
    # ========================================================

    resultat[
        "entreprise_trouvee"
    ] = bool(
        resultat["entreprise"]
    )

    resultat[
        "poste_trouve"
    ] = bool(
        resultat["poste"]
    )

    resultat[
        "taches_trouvees"
    ] = bool(
        resultat["taches"]
    )

    return resultat


# ============================================================
# GENERATION DE PRESENTATION CANDIDAT
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
