import re

SEPARATEUR = re.compile(r"^--- Exemple \d+ ---$", re.M)


def lire_blocs(chemin, etiquette_par_defaut: str) -> list[dict[str, str]]:
    """Format : blocs separes par '--- Exemple N ---',
    chaque bloc contient Label:, Source: et Contenu: suivi du texte."""
    if not chemin.exists():
        return []

    brut = chemin.read_text(encoding="utf-8", errors="ignore")
    lignes = []

    for bloc in SEPARATEUR.split(brut)[1:]:
        etiquette = etiquette_par_defaut
        source = "inconnue"
        contenu = []
        dans_contenu = False

        for ligne in bloc.splitlines():
            if ligne.startswith("Label:"):
                etiquette = ligne.removeprefix("Label:").strip().upper()
            elif ligne.startswith("Source:"):
                source = ligne.removeprefix("Source:").strip()
            elif ligne.startswith("Contenu:"):
                dans_contenu = True
            elif dans_contenu:
                contenu.append(ligne)

        texte = "\n".join(contenu).strip()
        if texte:
            lignes.append({"message": texte, "etiquette": etiquette, "source": source})

    return lignes


def lire_pipes(chemin) -> list[dict[str, str]]:
    """Format : LABEL | SOURCE | VALEUR, une ligne par exemple."""
    if not chemin.exists():
        return []

    lignes = []
    with chemin.open(encoding="utf-8", errors="ignore") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue

            morceaux = [m.strip() for m in ligne.split("|", 2)]
            if len(morceaux) != 3:
                continue

            etiquette, source, valeur = morceaux
            if etiquette not in {"FRAUDE", "LEGITIME"} or not valeur:
                continue

            lignes.append({"valeur": valeur, "etiquette": etiquette, "source": source})

    return lignes
