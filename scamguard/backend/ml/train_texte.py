import json

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

GRAINE = 42
TAILLE_TEST = 0.2


def construire_pipeline(min_df: int = 2) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    strip_accents="unicode",
                    lowercase=True,
                    min_df=min_df,
                    max_features=40000,
                ),
            ),
            (
                "classifieur",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    C=4.0,
                    random_state=GRAINE,
                ),
            ),
        ]
    )


def charger(chemin, minimum: int) -> pd.DataFrame:
    if not chemin.exists():
        raise SystemExit(
            f"Corpus introuvable : {chemin}\n"
            "Lancez d abord : PYTHONPATH=. python etl/build_corpus.py"
        )

    corpus = pd.read_csv(chemin).dropna(subset=["message", "etiquette"])
    corpus = corpus[corpus["etiquette"].isin(["FRAUDE", "LEGITIME"])]

    if len(corpus) < minimum:
        raise SystemExit(f"Corpus trop petit : {len(corpus)} lignes, minimum {minimum}")

    return corpus


def entrainer(nom: str, corpus: pd.DataFrame, sortie, min_df: int = 2) -> dict:
    textes = corpus["message"].astype(str)
    etiquettes = corpus["etiquette"]

    print(f"\n=== Modele {nom} ===")
    print(f"Corpus      : {len(corpus)}")
    print(f"Repartition : {dict(etiquettes.value_counts())}")

    x_train, x_test, y_train, y_test = train_test_split(
        textes, etiquettes, test_size=TAILLE_TEST, random_state=GRAINE, stratify=etiquettes
    )

    pipeline = construire_pipeline(min_df)
    scores = cross_val_score(pipeline, x_train, y_train, cv=5, scoring="f1_macro")
    print(f"F1 macro CV : {scores.mean():.4f} (ecart {scores.std():.4f})")

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    rapport = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    matrice = confusion_matrix(y_test, predictions, labels=["LEGITIME", "FRAUDE"])

    print(classification_report(y_test, predictions, zero_division=0))
    print("                LEGITIME  FRAUDE")
    print(f"  LEGITIME      {matrice[0][0]:8}  {matrice[0][1]:6}")
    print(f"  FRAUDE        {matrice[1][0]:8}  {matrice[1][1]:6}")

    import joblib

    sortie.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, sortie)

    return {
        "corpus_total": len(corpus),
        "repartition": {str(k): int(v) for k, v in etiquettes.value_counts().items()},
        "taille_entrainement": len(x_train),
        "taille_test": len(x_test),
        "cv_f1_macro": round(float(scores.mean()), 4),
        "cv_ecart": round(float(scores.std()), 4),
        "precision_fraude": round(rapport["FRAUDE"]["precision"], 4),
        "rappel_fraude": round(rapport["FRAUDE"]["recall"], 4),
        "f1_fraude": round(rapport["FRAUDE"]["f1-score"], 4),
        "exactitude": round(rapport["accuracy"], 4),
        "matrice_confusion": {
            "vrais_negatifs": int(matrice[0][0]),
            "faux_positifs": int(matrice[0][1]),
            "faux_negatifs": int(matrice[1][0]),
            "vrais_positifs": int(matrice[1][1]),
        },
        "artefact": str(sortie),
    }


def exporter_json_mobile(pipeline, chemin, version: str) -> None:
    vectoriseur = pipeline.named_steps["tfidf"]
    modele = pipeline.named_steps["classifieur"]
    classes = list(modele.classes_)

    # sklearn oriente ses coefficients vers la classe d indice 1. Quand FRAUDE
    # est la classe 0, on inverse le signe pour que la sigmoide du telephone
    # donne directement la probabilite de fraude.
    sens = -1.0 if classes.index("FRAUDE") == 0 else 1.0

    charge = {
        "version": version,
        "type": "tfidf_logreg",
        "classes": classes,
        "index_fraude": classes.index("FRAUDE"),
        "vocabulaire": {t: int(i) for t, i in vectoriseur.vocabulary_.items()},
        "idf": vectoriseur.idf_.tolist(),
        "poids": [sens * float(c) for c in modele.coef_[0]],
        "biais": sens * float(modele.intercept_[0]),
        "ngram_max": 2,
        "sublinear_tf": True,
    }
    chemin.write_text(json.dumps(charge, ensure_ascii=False), encoding="utf-8")
