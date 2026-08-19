from metiers import detecter_metier


# ============================================================
# PONDERATION DU SCORE
# ============================================================

POIDS_METIER = 25
POIDS_TACHES = 30
POIDS_COMPETENCES = 20
POIDS_CACES = 15
POIDS_PERMIS = 10

# Total = 100


def _liste_depuis_champ(champ):
    """
    Transforme un champ texte stocké en base (chaîne séparée
    par des virgules) en liste de valeurs nettoyées.
    """

    if not champ:
        return []

    return [
        valeur.strip().lower()
        for valeur in champ.split(",")
        if valeur.strip()
    ]


def calculer_score(cv, poste):
    """
    Calcule un score de compatibilité pondéré entre un CV
    et une fiche de poste.

    cv, poste : dictionnaires issus de Supabase, avec au
    minimum les clés "texte", et idéalement "metier",
    "competences", "taches", "caces", "permis".

    Retourne un dictionnaire :
    {
        "score": int (0-100),
        "explication": [liste de lignes ✅ / ⚠️ / ℹ️],
        "metier_cv": str,
        "metier_poste": str,
    }
    """

    cv_texte = cv.get("texte") or ""
    poste_texte = poste.get("texte") or ""

    metier_cv = cv.get("metier") or detecter_metier(cv_texte)
    metier_poste = detecter_metier(poste_texte)

    explication = []

    # --------------------------------------------------
    # METIER
    # --------------------------------------------------

    metier_ok = (
        metier_cv == metier_poste
        and metier_cv != "Non détecté"
    )

    if metier_ok:
        score_metier = POIDS_METIER

        explication.append(
            f"✅ Métier correspondant ({metier_cv})"
        )

    else:
        score_metier = 0

        explication.append(
            "⚠️ Métier différent "
            f"(CV : {metier_cv} / Poste : {metier_poste})"
        )

    # --------------------------------------------------
    # TACHES
    # --------------------------------------------------

    taches_poste = _liste_depuis_champ(poste.get("taches"))
    taches_cv = _liste_depuis_champ(cv.get("taches"))

    taches_communes = [
        t for t in taches_poste if t in taches_cv
    ]

    taches_manquantes = [
        t for t in taches_poste if t not in taches_cv
    ]

    if taches_poste:

        score_taches = (
            len(taches_communes)
            / len(taches_poste)
            * POIDS_TACHES
        )

        if taches_communes:

            explication.append(
                f"✅ {len(taches_communes)}/"
                f"{len(taches_poste)} tâches déjà "
                "réalisées par le candidat"
            )

        else:

            explication.append(
                "⚠️ Aucune des tâches demandées "
                "n'a été retrouvée dans le CV"
            )

        if taches_manquantes:

            explication.append(
                "⚠️ Tâches non retrouvées : "
                + ", ".join(taches_manquantes)
            )

    else:

        score_taches = 0

        explication.append(
            "ℹ️ Aucune tâche renseignée sur la fiche de poste"
        )

    # --------------------------------------------------
    # COMPETENCES
    # --------------------------------------------------

    competences_poste = _liste_depuis_champ(
        poste.get("competences")
    )

    competences_cv = _liste_depuis_champ(
        cv.get("competences")
    )

    competences_communes = [
        c for c in competences_poste if c in competences_cv
    ]

    competences_manquantes = [
        c for c in competences_poste
        if c not in competences_cv
    ]

    if competences_poste:

        score_competences = (
            len(competences_communes)
            / len(competences_poste)
            * POIDS_COMPETENCES
        )

        explication.append(
            f"✅ {len(competences_communes)}/"
            f"{len(competences_poste)} compétences "
            "requises présentes"
        )

        if competences_manquantes:

            explication.append(
                "⚠️ Compétence(s) demandée(s) non trouvée(s) : "
                + ", ".join(competences_manquantes)
            )

    else:

        score_competences = 0

        explication.append(
            "ℹ️ Aucune compétence renseignée sur la fiche de poste"
        )

    # --------------------------------------------------
    # CACES
    # --------------------------------------------------

    caces_poste = _liste_depuis_champ(poste.get("caces"))
    caces_cv = _liste_depuis_champ(cv.get("caces"))

    if not caces_poste:

        score_caces = POIDS_CACES

        explication.append(
            "ℹ️ Aucun CACES requis pour ce poste"
        )

    else:

        caces_communs = [
            c for c in caces_poste if c in caces_cv
        ]

        score_caces = (
            len(caces_communs)
            / len(caces_poste)
            * POIDS_CACES
        )

        if len(caces_communs) == len(caces_poste):

            explication.append(
                "✅ CACES requis présent(s) "
                f"({', '.join(caces_poste)})"
            )

        elif caces_communs:

            explication.append(
                "⚠️ CACES partiellement présent(s) "
                f"({', '.join(caces_communs)} sur "
                f"{', '.join(caces_poste)} requis)"
            )

        else:

            explication.append(
                "⚠️ CACES requis absent du CV "
                f"({', '.join(caces_poste)})"
            )

    # --------------------------------------------------
    # PERMIS
    # --------------------------------------------------

    permis_poste = _liste_depuis_champ(poste.get("permis"))
    permis_cv = _liste_depuis_champ(cv.get("permis"))

    if not permis_poste:

        score_permis = POIDS_PERMIS

        explication.append(
            "ℹ️ Aucun permis requis pour ce poste"
        )

    else:

        permis_communs = [
            p for p in permis_poste if p in permis_cv
        ]

        score_permis = (
            len(permis_communs)
            / len(permis_poste)
            * POIDS_PERMIS
        )

        if len(permis_communs) == len(permis_poste):

            explication.append(
                "✅ Permis requis présent(s) "
                f"({', '.join(permis_poste)})"
            )

        else:

            explication.append(
                "⚠️ Permis requis absent du CV "
                f"({', '.join(permis_poste)})"
            )

    # --------------------------------------------------
    # SUIVI MEDICAL VIP / SIR (information, non noté)
    # --------------------------------------------------

    vip_sir = poste.get("vip_sir")

    if vip_sir:

        explication.append(
            f"ℹ️ Ce poste nécessite un suivi médical : {vip_sir}"
        )

    # --------------------------------------------------
    # SCORE FINAL
    # --------------------------------------------------

    score_final = (
        score_metier
        + score_taches
        + score_competences
        + score_caces
        + score_permis
    )

    score_final = round(min(score_final, 100))

    return {
        "score": score_final,
        "explication": explication,
        "metier_cv": metier_cv,
        "metier_poste": metier_poste,
    }
