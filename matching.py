from metiers import detecter_metier


def calculer_score(cv_text, poste_text):
    """
    Matching intelligent entre un CV et une fiche de poste.
    """

    cv_words = set(cv_text.split())
    poste_words = set(poste_text.split())

    if len(poste_words) == 0:
        return 0, [], "Non détecté", "Non détecté"

    mots_communs = cv_words.intersection(poste_words)

    score_mots = len(mots_communs) / len(poste_words) * 100

    metier_cv = detecter_metier(cv_text)
    metier_poste = detecter_metier(poste_text)

    bonus = 0

    if metier_cv == metier_poste and metier_cv != "Non détecté":
        bonus = 25

    score_final = min(score_mots + bonus, 100)

    return (
        round(score_final),
        sorted(mots_communs),
        metier_cv,
        metier_poste
    )
