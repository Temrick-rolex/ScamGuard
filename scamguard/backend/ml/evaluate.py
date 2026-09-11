from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import Pipeline

FRAUD_CLASS = 1


def evaluate(pipeline: Pipeline, texts: list[str], targets: list[int]) -> dict:
    predictions = pipeline.predict(texts)
    precision, recall, f1, support = precision_recall_fscore_support(
        targets, predictions, labels=[0, 1], zero_division=0
    )
    matrix = confusion_matrix(targets, predictions, labels=[0, 1])

    return {
        "taille_test": len(targets),
        "legitime": {
            "precision": round(float(precision[0]), 3),
            "rappel": round(float(recall[0]), 3),
            "f1": round(float(f1[0]), 3),
            "support": int(support[0]),
        },
        "fraude": {
            "precision": round(float(precision[1]), 3),
            "rappel": round(float(recall[1]), 3),
            "f1": round(float(f1[1]), 3),
            "support": int(support[1]),
        },
        "matrice_confusion": {
            "vrais_negatifs": int(matrix[0][0]),
            "faux_positifs": int(matrix[0][1]),
            "faux_negatifs": int(matrix[1][0]),
            "vrais_positifs": int(matrix[1][1]),
        },
    }


def print_report(metrics: dict, corpus_size: int) -> None:
    fraude = metrics["fraude"]
    legitime = metrics["legitime"]
    matrix = metrics["matrice_confusion"]

    print(f"Corpus total : {corpus_size} exemples")
    print(f"Jeu de test  : {metrics['taille_test']} exemples\n")
    print(f"{'Classe':<12}{'Precision':>11}{'Rappel':>9}{'F1':>8}{'Support':>9}")
    print(f"{'LEGITIME':<12}{legitime['precision']:>11}{legitime['rappel']:>9}{legitime['f1']:>8}{legitime['support']:>9}")
    print(f"{'FRAUDE':<12}{fraude['precision']:>11}{fraude['rappel']:>9}{fraude['f1']:>8}{fraude['support']:>9}")
    print("\nMatrice de confusion")
    print(f"  legitimes bien classes : {matrix['vrais_negatifs']}")
    print(f"  fausses alertes        : {matrix['faux_positifs']}")
    print(f"  fraudes manquees       : {matrix['faux_negatifs']}")
    print(f"  fraudes detectees      : {matrix['vrais_positifs']}")

    if fraude["rappel"] < 0.85:
        print("\nAttention : rappel fraude sous la cible de 0.85 - corpus a enrichir")
