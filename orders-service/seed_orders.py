from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Korpa, StavkaKorpe, Narudzba, Base
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def seed():
    # Kreiramo aktivnu korpu za korisnika ID 1
    korpa = Korpa(korisnik_id=1, status="aktivna")
    db.add(korpa)
    db.commit()

    # Dodajemo 3 stavke u korpu
    stavke = [
        StavkaKorpe(korpa_id=korpa.id, proizvod_id="prod1", naziv_proizvoda="Roze Haljina", velicina="S", boja="Roze", kolicina=1, cijena_po_komadu=4500.0),
        StavkaKorpe(korpa_id=korpa.id, proizvod_id="prod2", naziv_proizvoda="Bluza", velicina="M", boja="Ljubičasta", kolicina=2, cijena_po_komadu=2200.0)
    ]
    db.add_all(stavke)
    db.commit()
    print("Baza uspešno popunjena sa test podacima!")

if __name__ == "__main__":
    seed()