import joblib

from ml.paths import PIPELINE_EMAIL, PIPELINE_SMS, PIPELINE_URL


class ClassifieurTexte:
    def __init__(self, chemin, nom: str) -> None:
        self.nom = nom
        self._pipeline = None
        self._version = "absent"
        self._index_fraude = 0
        self._charger(chemin)

    def _charger(self, chemin) -> None:
        if not chemin.exists():
            return
        try:
            self._pipeline = joblib.load(chemin)
            self._version = chemin.stem.replace("pipeline_", "")
            self._index_fraude = list(self._pipeline.classes_).index("FRAUDE")
        except Exception:
            self._pipeline = None
            self._version = "absent"

    @property
    def available(self) -> bool:
        return self._pipeline is not None

    @property
    def version(self) -> str:
        return self._version

    def score(self, texte: str) -> int | None:
        if self._pipeline is None:
            return None
        probabilites = self._pipeline.predict_proba([texte])[0]
        return round(float(probabilites[self._index_fraude]) * 100)


class ClassifieurUrl:
    def __init__(self, chemin) -> None:
        self._modele = None
        self._version = "absent"
        self._index_fraude = 0
        self._charger(chemin)

    def _charger(self, chemin) -> None:
        if not chemin.exists():
            return
        try:
            charge = joblib.load(chemin)
            self._modele = charge["modele"]
            self._version = chemin.stem.replace("pipeline_", "")
            self._index_fraude = list(self._modele.classes_).index("FRAUDE")
        except Exception:
            self._modele = None
            self._version = "absent"

    @property
    def available(self) -> bool:
        return self._modele is not None

    @property
    def version(self) -> str:
        return self._version

    def score(self, url: str) -> int | None:
        if self._modele is None:
            return None

        from ml.url_features import extraire

        probabilites = self._modele.predict_proba([extraire(url)])[0]
        return round(float(probabilites[self._index_fraude]) * 100)

    def score_maximum(self, urls: list[str]) -> int | None:
        scores = [s for s in (self.score(u) for u in urls) if s is not None]
        return max(scores) if scores else None


scorer = ClassifieurTexte(PIPELINE_SMS, "sms")
scorer_email = ClassifieurTexte(PIPELINE_EMAIL, "email")
scorer_url = ClassifieurUrl(PIPELINE_URL)
