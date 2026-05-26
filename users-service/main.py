from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import Korisnik, Rola, Adresa, Mesto, KorisnikAdresa
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_lozinku(lozinka: str) -> str:
    return pwd_context.hash(lozinka)

def provjeri_lozinku(lozinka: str, hash: str) -> bool:
    return pwd_context.verify(lozinka, hash)

def kreiraj_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def dekoduj_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Nevažeći token")


class RegistracijaSchema(BaseModel):
    email: EmailStr
    lozinka: str
    ime: str
    prezime: str
    broj_telefona: Optional[str] = None

class LoginSchema(BaseModel):
    email: EmailStr
    lozinka: str

class MestoSchema(BaseModel):
    postanski_broj: str
    grad: str
    drzava: str

class AdresaSchema(BaseModel):
    ulica: str
    kucni_broj: str
    sprat: Optional[str] = None
    mesto: MestoSchema
    tip_adrese: Optional[str] = "kucna"
    je_podrazumijevana: Optional[bool] = False



@app.on_event("startup")
async def startup():
    db = next(get_db())
    # Kreiraj role ako ne postoje
    if not db.query(Rola).filter(Rola.naziv == "administrator").first():
        db.add(Rola(naziv="administrator"))
    if not db.query(Rola).filter(Rola.naziv == "korisnik").first():
        db.add(Rola(naziv="korisnik"))
    db.commit()


@app.post("/auth/register", status_code=201)
async def registracija(podaci: RegistracijaSchema, db: Session = Depends(get_db)):
    """
    FZ 2.1 — Kreiranje korisničkog naloga putem email adrese
    FZ 2.2 — Validacija emaila (EmailStr) i lozinke
    """
    # Provjeri da li email već postoji
    if db.query(Korisnik).filter(Korisnik.email == podaci.email).first():
        raise HTTPException(status_code=400, detail="Email već postoji")

    
    if len(podaci.lozinka) < 8:
        raise HTTPException(status_code=400, detail="Lozinka mora imati najmanje 8 karaktera")

    
    rola = db.query(Rola).filter(Rola.naziv == "korisnik").first()

    novi_korisnik = Korisnik(
        email=podaci.email,
        lozinka_hash=hash_lozinku(podaci.lozinka),
        ime=podaci.ime,
        prezime=podaci.prezime,
        broj_telefona=podaci.broj_telefona,
        rola_id=rola.id
    )
    db.add(novi_korisnik)
    db.commit()
    db.refresh(novi_korisnik)

    return {
        "message": "Korisnik uspješno registrovan",
        "id": novi_korisnik.id,
        "email": novi_korisnik.email,
        "ime": novi_korisnik.ime,
        "prezime": novi_korisnik.prezime
    }

@app.post("/auth/login")
async def login(podaci: LoginSchema, db: Session = Depends(get_db)):
    """
    FZ 3.1 — Bezbjedna prijava korisnika putem kredencijala
    """
    korisnik = db.query(Korisnik).filter(Korisnik.email == podaci.email).first()

    if not korisnik or not provjeri_lozinku(podaci.lozinka, korisnik.lozinka_hash):
        raise HTTPException(status_code=401, detail="Pogrešan email ili lozinka")

    if not korisnik.je_aktivan:
        raise HTTPException(status_code=403, detail="Nalog je deaktiviran")

    token = kreiraj_token({
        "sub": str(korisnik.id),
        "email": korisnik.email,
        "rola": korisnik.rola.naziv
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "korisnik": {
            "id": korisnik.id,
            "email": korisnik.email,
            "ime": korisnik.ime,
            "prezime": korisnik.prezime,
            "rola": korisnik.rola.naziv
        }
    }


@app.get("/users/{korisnik_id}")
async def get_profil(korisnik_id: int, db: Session = Depends(get_db)):
    """
    FZ 3.2 — Pristup ličnom profilu nakon uspješne prijave
    """
    korisnik = db.query(Korisnik).filter(Korisnik.id == korisnik_id).first()
    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")

    return {
        "id": korisnik.id,
        "email": korisnik.email,
        "ime": korisnik.ime,
        "prezime": korisnik.prezime,
        "broj_telefona": korisnik.broj_telefona,
        "rola": korisnik.rola.naziv,
        "kreiran": korisnik.kreiran
    }



@app.post("/users/{korisnik_id}/adrese", status_code=201)
async def dodaj_adresu(korisnik_id: int, adresa: AdresaSchema, db: Session = Depends(get_db)):
    """
    Dodavanje adrese isporuke korisniku
    Koristi REST Countries API za validaciju države — eksterni API
    """
    korisnik = db.query(Korisnik).filter(Korisnik.id == korisnik_id).first()
    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")

    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{os.getenv('REST_COUNTRIES_URL')}/name/{adresa.mesto.drzava}",
                timeout=5.0
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Država '{adresa.mesto.drzava}' nije validna")
        except httpx.TimeoutException:
            # Ako API nije dostupan, nastavljamo bez validacije
            pass

    
    mesto = db.query(Mesto).filter(
        Mesto.grad == adresa.mesto.grad,
        Mesto.drzava == adresa.mesto.drzava
    ).first()

    if not mesto:
        mesto = Mesto(
            postanski_broj=adresa.mesto.postanski_broj,
            grad=adresa.mesto.grad,
            drzava=adresa.mesto.drzava
        )
        db.add(mesto)
        db.commit()
        db.refresh(mesto)

   
    nova_adresa = Adresa(
        ulica=adresa.ulica,
        kucni_broj=adresa.kucni_broj,
        sprat=adresa.sprat,
        mesto_id=mesto.id
    )
    db.add(nova_adresa)
    db.commit()
    db.refresh(nova_adresa)

    
    korisnik_adresa = KorisnikAdresa(
        korisnik_id=korisnik_id,
        adresa_id=nova_adresa.id,
        tip_adrese=adresa.tip_adrese,
        je_podrazumijevana=adresa.je_podrazumijevana
    )
    db.add(korisnik_adresa)
    db.commit()

    return {
        "message": "Adresa uspješno dodana",
        "adresa_id": nova_adresa.id,
        "ulica": nova_adresa.ulica,
        "kucni_broj": nova_adresa.kucni_broj,
        "grad": mesto.grad,
        "drzava": mesto.drzava
    }

@app.get("/users/{korisnik_id}/adrese")
async def get_adrese(korisnik_id: int, db: Session = Depends(get_db)):
    """Vraća sve adrese korisnika"""
    korisnik = db.query(Korisnik).filter(Korisnik.id == korisnik_id).first()
    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")

    rezultat = []
    for ka in korisnik.adrese:
        rezultat.append({
            "adresa_id": ka.adresa.id,
            "ulica": ka.adresa.ulica,
            "kucni_broj": ka.adresa.kucni_broj,
            "sprat": ka.adresa.sprat,
            "grad": ka.adresa.mesto.grad,
            "postanski_broj": ka.adresa.mesto.postanski_broj,
            "drzava": ka.adresa.mesto.drzava,
            "tip_adrese": ka.tip_adrese,
            "je_podrazumijevana": ka.je_podrazumijevana
        })
    return rezultat


@app.get("/auth/validate")
async def validiraj_token(token: str):
    """
    Endpoint koji api-gateway poziva da provjeri JWT token
    """
    payload = dekoduj_token(token)
    return {
        "korisnik_id": payload.get("sub"),
        "email": payload.get("email"),
        "rola": payload.get("rola")
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "users-service"}

@app.get("/users")
async def get_svi_korisnici(db: Session = Depends(get_db)):
    korisnici = db.query(Korisnik).all()
    return [{"id": k.id, "ime": k.ime, "prezime": k.prezime, "email": k.email} for k in korisnici]