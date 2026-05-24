from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import Korpa, StavkaKorpe
from pydantic import BaseModel
from typing import Optional

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)



class StavkaSchema(BaseModel):
    proizvod_id: str
    naziv_proizvoda: str
    velicina: str
    boja: str
    kolicina: int
    cijena_po_komadu: float



@app.post("/cart/{korisnik_id}/items", status_code=201)
async def dodaj_u_korpu(korisnik_id: int, stavka: StavkaSchema, db: Session = Depends(get_db)):
    """
    FZ 4.1 — Dodavanje artikla u korpu uz definisanje boje i velicine
    """
    
    korpa = db.query(Korpa).filter(
        Korpa.korisnik_id == korisnik_id,
        Korpa.status == "aktivna"
    ).first()

    if not korpa:
        korpa = Korpa(korisnik_id=korisnik_id)
        db.add(korpa)
        db.commit()
        db.refresh(korpa)

    nova_stavka = StavkaKorpe(
        korpa_id=korpa.id,
        proizvod_id=stavka.proizvod_id,
        naziv_proizvoda=stavka.naziv_proizvoda,
        velicina=stavka.velicina,
        boja=stavka.boja,
        kolicina=stavka.kolicina,
        cijena_po_komadu=stavka.cijena_po_komadu
    )
    db.add(nova_stavka)
    db.commit()
    db.refresh(nova_stavka)

    return {
        "message": "Artikal dodan u korpu",
        "korpa_id": korpa.id,
        "stavka_id": nova_stavka.id
    }




@app.get("/cart/{korisnik_id}")
async def get_korpa(korisnik_id: int, db: Session = Depends(get_db)):
    """
    FZ 4.2 — Pregled sadržaja korpe
    """
    korpa = db.query(Korpa).filter(
        Korpa.korisnik_id == korisnik_id,
        Korpa.status == "aktivna"
    ).first()

    if not korpa:
        raise HTTPException(status_code=404, detail="Korpa nije pronađena")

    stavke = []
    ukupno = 0
    for stavka in korpa.stavke:
        stavke.append({
            "stavka_id": stavka.id,
            "proizvod_id": stavka.proizvod_id,
            "naziv": stavka.naziv_proizvoda,
            "velicina": stavka.velicina,
            "boja": stavka.boja,
            "kolicina": stavka.kolicina,
            "cijena_po_komadu": stavka.cijena_po_komadu,
            "ukupno_stavka": stavka.kolicina * stavka.cijena_po_komadu
        })
        ukupno += stavka.kolicina * stavka.cijena_po_komadu

    return {
        "korpa_id": korpa.id,
        "korisnik_id": korisnik_id,
        "stavke": stavke,
        "ukupno": ukupno
    }

@app.put("/cart/{korisnik_id}/items/{stavka_id}")
async def izmijeni_kolicinu(korisnik_id: int, stavka_id: int, kolicina: int, db: Session = Depends(get_db)):
    """
    FZ 4.2 — Izmjena količine artikla u korpi
    """
    stavka = db.query(StavkaKorpe).filter(StavkaKorpe.id == stavka_id).first()
    if not stavka:
        raise HTTPException(status_code=404, detail="Stavka nije pronađena")

    stavka.kolicina = kolicina
    db.commit()

    return {"message": "Količina ažurirana", "nova_kolicina": kolicina}

@app.delete("/cart/{korisnik_id}/items/{stavka_id}")
async def ukloni_iz_korpe(korisnik_id: int, stavka_id: int, db: Session = Depends(get_db)):
    """
    FZ 4.2 — Uklanjanje artikla iz korpe
    """
    stavka = db.query(StavkaKorpe).filter(StavkaKorpe.id == stavka_id).first()
    if not stavka:
        raise HTTPException(status_code=404, detail="Stavka nije pronađena")

    db.delete(stavka)
    db.commit()

    return {"message": "Artikal uklonjen iz korpe"}





class NarudzbaSchema(BaseModel):
    adresa_isporuke: str

@app.post("/orders/{korisnik_id}", status_code=201)
async def kreiraj_narudzbu(korisnik_id: int, podaci: NarudzbaSchema, db: Session = Depends(get_db)):
    """
    FZ 5.1 — Kreiranje narudžbine iz aktivne korpe
    """
    korpa = db.query(Korpa).filter(
        Korpa.korisnik_id == korisnik_id,
        Korpa.status == "aktivna"
    ).first()

    if not korpa:
        raise HTTPException(status_code=404, detail="Aktivna korpa nije pronađena")

    if not korpa.stavke:
        raise HTTPException(status_code=400, detail="Korpa je prazna")

    ukupno = sum(s.kolicina * s.cijena_po_komadu for s in korpa.stavke)

    narudzba = Narudzba(
        korisnik_id=korisnik_id,
        korpa_id=korpa.id,
        ukupan_iznos=ukupno,
        adresa_isporuke=podaci.adresa_isporuke
    )
    db.add(narudzba)

    korpa.status = "zatvorena"
    db.commit()
    db.refresh(narudzba)

    return {
        "message": "Narudžbina kreirana",
        "narudzba_id": narudzba.id,
        "ukupan_iznos": narudzba.ukupan_iznos,
        "status": narudzba.status
    }



Commit 7 — FZ 6.1 praćenje statusa narudžbine
Dodaj u main.py ispred health checka:
python# ----------------------------------------------------------
# PRAĆENJE NARUDŽBINE — FZ 6.1
# ----------------------------------------------------------

@app.get("/orders/{korisnik_id}")
async def get_narudzbe(korisnik_id: int, db: Session = Depends(get_db)):
    """
    FZ 6.1 — Pregled svih narudžbina korisnika
    """
    narudzbe = db.query(Narudzba).filter(
        Narudzba.korisnik_id == korisnik_id
    ).all()

    if not narudzbe:
        raise HTTPException(status_code=404, detail="Nema narudžbina")

    return [
        {
            "narudzba_id": n.id,
            "ukupan_iznos": n.ukupan_iznos,
            "status": n.status,
            "adresa_isporuke": n.adresa_isporuke,
            "kreirana": n.kreirana
        }
        for n in narudzbe
    ]

@app.get("/orders/{korisnik_id}/{narudzba_id}")
async def get_narudzba(korisnik_id: int, narudzba_id: int, db: Session = Depends(get_db)):
    """
    FZ 6.1 — Detalji i trenutni status jedne narudžbine
    """
    narudzba = db.query(Narudzba).filter(
        Narudzba.id == narudzba_id,
        Narudzba.korisnik_id == korisnik_id
    ).first()

    if not narudzba:
        raise HTTPException(status_code=404, detail="Narudžbina nije pronađena")

    korpa = db.query(Korpa).filter(Korpa.id == narudzba.korpa_id).first()

    stavke = []
    for stavka in korpa.stavke:
        stavke.append({
            "naziv": stavka.naziv_proizvoda,
            "velicina": stavka.velicina,
            "boja": stavka.boja,
            "kolicina": stavka.kolicina,
            "cijena_po_komadu": stavka.cijena_po_komadu
        })

    return {
        "narudzba_id": narudzba.id,
        "status": narudzba.status,
        "ukupan_iznos": narudzba.ukupan_iznos,
        "adresa_isporuke": narudzba.adresa_isporuke,
        "kreirana": narudzba.kreirana,
        "stavke": stavke
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "orders-service"}



