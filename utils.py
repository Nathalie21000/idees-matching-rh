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
    Extrait le texte d'un PDF ou d'un Word.

    Pour les PDF :
    - extrait le texte visible ;
    - extrait également les valeurs des champs de formulaire
      PDF (AcroForm) lorsque le document en contient.

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

    C'est important pour notre fiche de poste ID'EES INTERIM :
    les zones Nom de l'entreprise, Intitulé du poste et Liste
    des tâches proposées sont des champs de formulaire.
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

                entreprise = champs.get("Texte 01", "")
                poste = champs.get("Texte 02", "")
                taches = champs.get("Texte 03", "")

                # On ajoute des lignes structurées.
                #
                # Elles permettent ensuite à
                # extraire_fiche_poste_ciblee() de récupérer
                # les bonnes valeurs sans les confondre avec
                # les autres rubriques.

                if entreprise:
                    morceaux.append(
                        f"Nom de l'entreprise : {entreprise}"
                    )

                if poste:
                    morceaux.append(
                        f"Intitulé du poste : {poste}"
                    )

                if taches:
                    morceaux.append(
                        f"Liste des tâches proposées : {taches}"
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

    Retourne un dictionnaire :

        {
            "Texte 01": "...",
            "Texte 02": "...",
            "Texte 03": "..."
        }

    Les autres champs du formulaire sont également récupérés,
    mais ils ne sont pas utilisés pour notre extraction ciblée.
    """

    resultat = {}

    try:

        catalogue = pdf.doc.catalog

        acro_form = catalogue.get("AcroForm")

        if not acro_form:
            return resultat

        acro_form = resolve(acro_form)

        champs = acro_form.get("Fields")

        if not champs:
            return resultat

        champs = resolve(champs)

        def parcourir_champ(champ, prefix=""):

            champ_resolu = champ.resolve()

            nom = resolve_and_decode(
                champ_resolu.get("T")
            )

            if nom:
                if prefix:
                    nom_complet = f"{prefix}.{nom}"
                else:
                    nom_complet = nom
            else:
                nom_complet = prefix

            # --------------------------------------------
            # Valeur du champ
            # --------------------------------------------

            valeur = champ_resolu.get("V")

            if valeur is not None:

                try:
                    valeur = resolve_and_decode(
                        valeur
                    )
                except Exception:
                    valeur = str(valeur)

                if valeur is not None:

                    valeur = str(
                        valeur
                    ).strip()

                    if valeur:
                        resultat[
                            nom_complet
                        ] = valeur

            # --------------------------------------------
            # Sous-champs éventuels
            # --------------------------------------------

            enfants = champ_resolu.get(
                "Kids"
            )

            if enfants:

                for enfant in resolve(enfants):

                    parcourir_champ(
                        enfant,
                        nom_complet
                    )

        for champ in champs:

            parcourir_champ(champ)

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

        document = docx.Document(file)

        # ----------------------------------------------------
        # Paragraphes
        # ----------------------------------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

        # ----------------------------------------------------
        # Tableaux
        # ----------------------------------------------------

        for table in document.tables:

            for ligne in table.rows:

                cellules = []

                for cellule in ligne.cells:

                    texte_cellule = cellule.text.strip()

                    if texte_cellule:
                        cellules.append(
                            texte_cellule
                        )

                if cellules:

                    morceaux.append(
                        " | ".join(cellules)
                    )

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoyage léger.

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
    Normalisation utilisée pour comparer les libellés.
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
    Extrait UNIQUEMENT :

    - le nom de l'entreprise ;
    - l'intitulé du poste ;
    - la liste des tâches proposées.

    Pour notre formulaire ID'EES INTERIM, les valeurs sont
    normalement ajoutées par extract_text() sous la forme :

        Nom de l'entreprise : ...
        Intitulé du poste : ...
        Liste des tâches proposées : ...

    Aucun métier ou aucune compétence n'est déduit ici.
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

    lignes = texte.split("\n")

    for ligne in lignes:

        ligne = ligne.strip()

        if not ligne:
            continue

        ligne_norm = normaliser_texte(
            ligne
        )

        # ----------------------------------------------------
        # ENTREPRISE
        # ----------------------------------------------------

        if ligne_norm.startswith(
            "nom de l'entreprise :"
        ):

            valeur = re.sub(
                r"^nom de l'entreprise\s*:\s*",
                "",
                ligne,
                flags=re.IGNORECASE
            ).strip()

            if valeur:
                resultat["entreprise"] = valeur

        # ----------------------------------------------------
        # POSTE
        # ----------------------------------------------------

        elif ligne_norm.startswith(
            "intitulé du poste :"
        ) or ligne_norm.startswith(
            "intitule du poste :"
        ):

            valeur = re.sub(
                r"^intitul[ée]\s+du\s+poste\s*:\s*",
                "",
                ligne,
                flags=re.IGNORECASE
            ).strip()

            if valeur:
                resultat["poste"] = valeur

        # ----------------------------------------------------
        # TACHES
        # ----------------------------------------------------

        elif ligne_norm.startswith(
            "liste des tâches proposées :"
        ) or ligne_norm.startswith(
            "liste des taches proposees :"
        ):

            valeur = re.sub(
                r"^liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:\s*",
                "",
                ligne,
                flags=re.IGNORECASE
            ).strip()

            if valeur:
                resultat["taches"] = valeur

    # ========================================================
    # INDICATEURS
    # ========================================================

    resultat["entreprise_trouvee"] = bool(
        resultat["entreprise"]
    )

    resultat["poste_trouve"] = bool(
        resultat["poste"]
    )

    resultat["taches_trouvees"] = bool(
        resultat["taches"]
    )

    return resultat


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
