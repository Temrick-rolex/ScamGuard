from app.db.session import SessionLocal
from app.models import Base, UrlReputation
from app.db.session import engine
from app.services.risk_engine.reputation import url_fingerprint
from etl.extract.from_public import lire_urls_phishing

SCORE_PHISHING = 95


def main() -> None:
    Base.metadata.create_all(bind=engine)
    urls = lire_urls_phishing()

    if not urls:
        print("Aucune URL de phishing trouvee. Verifiez datasets/raw/openphish/")
        return

    session = SessionLocal()
    ajouts = 0
    maj = 0

    try:
        for entree in urls:
            empreinte = url_fingerprint(entree["url"])
            existant = session.get(UrlReputation, empreinte)

            if existant is None:
                session.add(
                    UrlReputation(
                        url_hash=empreinte,
                        verdict="PHISHING",
                        score=SCORE_PHISHING,
                        source=entree["source"],
                    )
                )
                ajouts += 1
            else:
                existant.verdict = "PHISHING"
                existant.score = SCORE_PHISHING
                existant.source = entree["source"]
                maj += 1

        session.commit()
    finally:
        session.close()

    print(f"URLs lues     : {len(urls)}")
    print(f"Ajoutees      : {ajouts}")
    print(f"Mises a jour  : {maj}")


if __name__ == "__main__":
    main()
