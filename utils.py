import pdfplumber
import docx
import re
import unicodedata


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word (.docx).

    Le texte conserve les retours à la ligne afin de permettre
    l'analyse précise des rubriques d'une fiche de poste.
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

    Attention :
    pdfplumber ne fait pas d'OCR.
    Un PDF scanné sous forme d'image ne pourra donc pas être
    lu correctement avec cette méthode seule.
    """

    texte_pages = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

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

    Lit :
    - les paragraphes ;
    - les tableaux ;
    - les cellules des tableaux.
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
    Nettoyage léger du texte.

    IMPORTANT :
    Les retours à la ligne sont conservés car ils sont
    indispensables pour comprendre la structure de la fiche.
    """

    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")
    texte = texte.replace("\xa0", " ")

    # Remplacement des espaces multiples
    texte = re.sub(r"[ \t]+", " ", texte)

    # Nettoyage des lignes
    lignes = []

    for ligne in texte.split("\n"):

        ligne = ligne.strip()

        if ligne:
            lignes.append(ligne)

    return "\n".join(lignes)


# ============================================================
# NORMALISATION POUR LA RECHERCHE
# ============================================================

def _sans_accents(texte):
    """
    Supprime les accents uniquement pour faciliter la recherche
    des libellés.

    Le texte original est conservé pour les valeurs affichées.
    """

    if not texte:
        return ""

    texte = unicodedata.normalize(
        "NFD",
        texte
    )

    texte = "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )

    return texte


def _normaliser_recherche(texte):
    """
    Normalisation utilisée uniquement pour comparer les
    libellés.
    """

    texte = _sans_accents(texte.lower())

    texte = texte.replace("’", "'")

    texte = re.sub(
        r"[^a-z0-9]+",
        " ",
        texte
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte
    )

    return texte.strip()


# ============================================================
# LIBELLES EXACTS DU MODELE DE FICHE DE POSTE
# ============================================================

LIBELLES_ENTREPRISE = [
    "nom de l'entreprise",
    "nom de l entreprise",
]

LIBELLES_POSTE = [
    "intitulé du poste",
    "intitule du poste",
]

LIBELLES_TACHES = [
    "liste des tâches proposées",
    "liste des taches proposees",
    "liste des tâches proposées :",
    "liste des taches proposees :",
]


# ============================================================
# AUTRES RUBRIQUES DU MODELE
# ============================================================

# Ces rubriques ne servent PAS à remplir les champs.
# Elles servent uniquement à savoir où s'arrêter lorsqu'on
# récupère la valeur d'une rubrique ciblée.

AUTRES_RUBRIQUES = [
    "nom de l'entreprise",
    "intitulé du poste",
    "liste des tâches proposées",
    "conditions de travail liées au poste",
    "habilitations obligatoires",
    "habilitations, certificats et diplômes obligatoires",
    "habilitations certificats et diplômes obligatoires",
    "conduite d'engins",
    "utilisation de machines / outils",
    "utilisation de machines outils",
    "compétences requises",
    "competences requises",
    "permis",
    "caces",
    "sécurité",
    "risques",
    "consignes de sécurité",
    "sécurité et risques",
]


# ============================================================
# TEST D'UNE LIGNE
# ============================================================

def _ligne_est_libelle(ligne, libelles):
    """
    Vérifie si une ligne correspond à l'un des libellés.
    """

    ligne_norm = _normaliser_recherche(ligne)

    for libelle in libelles:

        libelle_norm = _normaliser_recherche(libelle)

        if ligne_norm == libelle_norm:
            return True

        if ligne_norm.startswith(libelle_norm + " "):
            return True

        if ligne_norm.startswith(libelle_norm + ":"):
            return True

    return False


# ============================================================
# EXTRACTION DE VALEUR APRES UN LIBELLE
# ============================================================

def _extraire_valeur_depuis_ligne(
    ligne,
    libelles
):
    """
    Cherche une valeur placée sur la même ligne que le libellé.

    Exemple :

    Nom de l'entreprise : DUPONT BTP

    retourne :

    DUPONT BTP
    """

    ligne_originale = ligne.strip()

    ligne_norm = _normaliser_recherche(
        ligne_originale
    )

    for libelle in libelles:

        libelle_norm = _normaliser_recherche(
            libelle
        )

        # ----------------------------------------------------
        # Recherche dans la ligne originale.
        # On utilise une version insensible aux accents.
        # ----------------------------------------------------

        pattern = re.escape(
            libelle_norm
        )

        # Transformation de la ligne en version comparable
        ligne_compare = _normaliser_recherche(
            ligne_originale
        )

        match = re.search(
            pattern,
            ligne_compare,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        valeur = ligne_compare[
            match.end():
        ].strip(" :-|")

        if valeur:
            return valeur

    return ""


# ============================================================
# EXTRACTION D'UNE RUBRIQUE
# ============================================================

def _extraire_rubrique(
    texte,
    libelles,
    mode="simple"
):
    """
    Recherche une rubrique dans le texte.

    La fonction gère deux cas :

    1. Le libellé et la valeur sont sur la même ligne.
    2. Le libellé est seul sur une ligne et la valeur se trouve
       sur les lignes suivantes.

    Elle s'arrête lorsqu'une autre rubrique du modèle apparaît.
    """

    if not texte:
        return ""

    lignes = texte.split("\n")

    for index, ligne in enumerate(lignes):

        ligne = ligne.strip()

        if not ligne:
            continue

        # ----------------------------------------------------
        # Le libellé est-il présent dans cette ligne ?
        # ----------------------------------------------------

        ligne_norm = _normaliser_recherche(
            ligne
        )

        trouve_libelle = False
        libelle_utilise = ""

        for libelle in libelles:

            libelle_norm = _normaliser_recherche(
                libelle
            )

            if (
                ligne_norm == libelle_norm
                or ligne_norm.startswith(
                    libelle_norm + " "
                )
                or ligne_norm.startswith(
                    libelle_norm + ":"
                )
            ):
                trouve_libelle = True
                libelle_utilise = libelle
                break

        if not trouve_libelle:
            continue

        # ----------------------------------------------------
        # CAS 1 :
        # libellé + valeur sur la même ligne
        # ----------------------------------------------------

        valeur_meme_ligne = _extraire_valeur_depuis_ligne(
            ligne,
            [libelle_utilise]
        )

        if valeur_meme_ligne:

            # Pour entreprise et poste, une seule valeur.
            if mode == "simple":
                return valeur_meme_ligne

            # Pour les tâches, la ligne peut contenir plusieurs
            # éléments.
            if mode == "taches":
                return valeur_meme_ligne

        # ----------------------------------------------------
        # CAS 2 :
        # valeur sur la ou les lignes suivantes
        # ----------------------------------------------------

        valeurs = []

        for ligne_suivante in lignes[index + 1:]:

            ligne_suivante = ligne_suivante.strip()

            if not ligne_suivante:
                break

            # ------------------------------------------------
            # Ne pas récupérer une autre rubrique
            # ------------------------------------------------

            ligne_suivante_norm = _normaliser_recherche(
                ligne_suivante
            )

            est_autre_rubrique = False

            for autre in AUTRES_RUBRIQUES:

                autre_norm = _normaliser_recherche(
                    autre
                )

                if (
                    ligne_suivante_norm == autre_norm
                    or ligne_suivante_norm.startswith(
                        autre_norm + " "
                    )
                    or ligne_suivante_norm.startswith(
                        autre_norm + ":"
                    )
                ):
                    est_autre_rubrique = True
                    break

            if est_autre_rubrique:
                break

            valeurs.append(
                ligne_suivante
            )

            # ------------------------------------------------
            # Pour entreprise et poste :
            # une seule ligne suffit.
            # ------------------------------------------------

            if mode == "simple":
                break

            # ------------------------------------------------
            # Pour les tâches :
            # on accepte plusieurs lignes.
            # ------------------------------------------------

            if mode == "taches" and len(valeurs) >= 30:
                break

        if valeurs:

            if mode == "simple":
                return valeurs[0]

            return ", ".join(valeurs)

    return ""


# ============================================================
# LECTURE CIBLEE DE LA FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Lit UNIQUEMENT les trois informations essentielles
    de la fiche de poste :

    1. Nom de l'entreprise
    2. Intitulé du poste
    3. Liste des tâches proposées

    IMPORTANT :

    Cette fonction ne cherche volontairement PAS les compétences,
    le métier, les CACES ou les permis.

    Elle ne doit donc jamais remplir automatiquement les
    compétences avec des mots génériques comme :
    - travail en équipe
    - manutention
    - montage
    - tri
    - port de charges

    si ces éléments ne proviennent pas directement de la
    rubrique "Liste des tâches proposées".
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

    # --------------------------------------------------------
    # ENTREPRISE
    # --------------------------------------------------------

    entreprise = _extraire_rubrique(
        texte,
        LIBELLES_ENTREPRISE,
        mode="simple"
    )

    # --------------------------------------------------------
    # POSTE
    # --------------------------------------------------------

    poste = _extraire_rubrique(
        texte,
        LIBELLES_POSTE,
        mode="simple"
    )

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------

    taches = _extraire_rubrique(
        texte,
        LIBELLES_TACHES,
        mode="taches"
    )

    resultat["entreprise"] = entreprise.strip()
    resultat["poste"] = poste.strip()
    resultat["taches"] = taches.strip()

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
