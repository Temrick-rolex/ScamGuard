import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from etl.sources.paths import CORPUS_URL
from ml.paths import PIPELINE_URL
from ml.url_features import NOMS, domaine_de, extraire_lot

GRAINE = 42
TAILLE_TEST = 0.2


def entrainer_url() -> dict:
    if not CORPUS_URL.exists():
        raise SystemExit(
            f"Corpus introuvable : {CORPUS_URL}\n"
            "Lancez d abord : PYTHONPATH=. python etl/build_corpus.py"
        )

    corpus = pd.read_csv(CORPUS_URL).dropna(subset=["url", "etiquette"])
    corpus = corpus[corpus["etiquette"].isin(["FRAUDE", "LEGITIME"])]

    corpus["domaine"] = corpus["url"].astype(str).map(domaine_de)
    avant = len(corpus)
    corpus = corpus.drop_duplicates(subset=["domaine"])
    equilibre = corpus["etiquette"].value_counts().min()
    corpus = corpus.groupby("etiquette", group_keys=False).head(equilibre)

    print("\n=== Modele URL ===")
    print(f"Domaines uniques : {len(corpus)} (sur {avant} URLs)")
    print(f"Corpus      : {len(corpus)}")
    print(f"Repartition : {dict(corpus['etiquette'].value_counts())}")
    print("Extraction des caracteristiques...")

    caracteristiques = extraire_lot(corpus["url"].astype(str).tolist())
    etiquettes = corpus["etiquette"].tolist()

    x_train, x_test, y_train, y_test = train_test_split(
        caracteristiques,
        etiquettes,
        test_size=TAILLE_TEST,
        random_state=GRAINE,
        stratify=etiquettes,
    )

    modele = RandomForestClassifier(
        n_estimators=100,
        max_depth=22,
        min_samples_leaf=4,
        class_weight="balanced",
        n_jobs=-1,
        random_state=GRAINE,
    )
    modele.fit(x_train, y_train)
    predictions = modele.predict(x_test)

    rapport = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    matrice = confusion_matrix(y_test, predictions, labels=["LEGITIME", "FRAUDE"])

    print(classification_report(y_test, predictions, zero_division=0))
    print("                LEGITIME  FRAUDE")
    print(f"  LEGITIME      {matrice[0][0]:8}  {matrice[0][1]:6}")
    print(f"  FRAUDE        {matrice[1][0]:8}  {matrice[1][1]:6}")

    importances = sorted(
        zip(NOMS, modele.feature_importances_), key=lambda x: -x[1]
    )[:8]
    print("\nCaracteristiques les plus decisives :")
    for nom, poids in importances:
        print(f"  {nom:22} {poids:.4f}")

    PIPELINE_URL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"modele": modele, "noms": NOMS}, PIPELINE_URL, compress=3)

    return {
        "corpus_total": len(corpus),
        "repartition": {str(k): int(v) for k, v in corpus["etiquette"].value_counts().items()},
        "taille_entrainement": len(x_train),
        "taille_test": len(x_test),
        "cv_f1_macro": None,
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
        "caracteristiques_decisives": [{"nom": n, "poids": round(float(p), 4)} for n, p in importances],
        "artefact": str(PIPELINE_URL),
    }
