import os
import sys
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGODB_URL", "mongodb://catalog_admin:catalog_password123@localhost:27017/velura_catalog?authSource=admin")

try:
    client = MongoClient(MONGO_URI)
    db = client.velura_catalog
    collection = db.products

    dummy_products = [
        {"name": "Letnja haljina", "price": 2500, "category": "Odeca"},
        {"name": "Farmerke plave", "price": 3500, "category": "Odeca"},
        {"name": "Zimska jakna", "price": 8000, "category": "Odeca"},
        {"name": "Patike sportske", "price": 5000, "category": "Obuca"},
        {"name": "Kožna jakna", "price": 9500, "category": "Odeca"},
        {"name": "Bela majica", "price": 800, "category": "Odeca"},
        {"name": "Crne čizme", "price": 6000, "category": "Obuca"},
        {"name": "Duks sa kapuljačom", "price": 2200, "category": "Odeca"},
        {"name": "Elegantne cipele", "price": 7500, "category": "Obuca"},
        {"name": "Šorts za plažu", "price": 1200, "category": "Odeca"},
        {"name": "Vuneni džemper", "price": 3200, "category": "Odeca"},
        {"name": "Sandale kožne", "price": 4000, "category": "Obuca"},
        {"name": "Trenerka komplet", "price": 4500, "category": "Odeca"},
        {"name": "Kaiš kožni", "price": 1500, "category": "Dodaci"},
        {"name": "Kapa vunena", "price": 900, "category": "Dodaci"},
        {"name": "Rukavice kožne", "price": 2000, "category": "Dodaci"},
        {"name": "Pantalone chino", "price": 3800, "category": "Odeca"},
        {"name": "Majica polo", "price": 1800, "category": "Odeca"},
        {"name": "Baletanke", "price": 2800, "category": "Obuca"},
        {"name": "Jakna vetrovka", "price": 4200, "category": "Odeca"}
    ]

    
    collection.delete_many({})
    collection.insert_many(dummy_products)
    print(f"Uspešno dodato {len(dummy_products)} proizvoda u bazu!")
except Exception as e:
    print(f"Greška pri seedovanju MongoDB: {e}")
    sys.exit(1)