from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from database import products_collection, categories_collection
from models import ProductCreate, ProductUpdate, CategoryCreate
from bson import ObjectId
from typing import Optional
from datetime import datetime

app = FastAPI(title="Product Catalog Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----------------------------------------------------------
# POMOCNE FUNKCIJE
# ----------------------------------------------------------

def serialize_product(product) -> dict:
    """Konvertuje MongoDB dokument u JSON-serializovani recnik"""
    product["id"] = str(product["_id"])
    del product["_id"]
    return product

def serialize_category(category) -> dict:
    category["id"] = str(category["_id"])
    del category["_id"]
    return category

# ----------------------------------------------------------
# PROIZVODI — FZ 1.3, 7.1, 7.2, 7.3
# ----------------------------------------------------------

@app.get("/products")
async def get_all_products():
    """Vraca sve aktivne proizvode"""
    products = []
    async for product in products_collection.find({"is_active": True}):
        products.append(serialize_product(product))
    return products

@app.get("/products/search")
async def search_products(
    q: Optional[str] = Query(None, description="Kljucna rijec za pretragu"),
    category: Optional[str] = Query(None, description="Filtriranje po kategoriji"),
    collection: Optional[str] = Query(None, description="Filtriranje po kolekciji"),
    min_price: Optional[float] = Query(None, description="Minimalna cijena"),
    max_price: Optional[float] = Query(None, description="Maksimalna cijena")
):
    """
    FZ 1.1 — Pretraga proizvoda putem kljucnih rijeci
    FZ 1.2 — Filtriranje po kategorijama, kolekciji i cijeni
    """
    query = {"is_active": True}

    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]

    if category:
        query["category"] = {"$regex": category, "$options": "i"}

    if collection:
        query["collection"] = {"$regex": collection, "$options": "i"}

    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price

    products = []
    async for product in products_collection.find(query):
        products.append(serialize_product(product))
    return products

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """
    FZ 1.3 — Detalji proizvoda: slike, cijena, materijal, dostupne velicine
    """
    try:
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
    except:
        raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")

    if not product:
        raise HTTPException(status_code=404, detail="Proizvod nije pronađen")

    return serialize_product(product)

@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    """
    FZ 7.1 — Administrator dodaje novi artikal sa svim atributima i slikama
    """
    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()

    result = await products_collection.insert_one(product_dict)
    created = await products_collection.find_one({"_id": result.inserted_id})
    return serialize_product(created)

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductUpdate):
    """
    FZ 7.2 — Administrator azurira cijenu, opis i zalihe u realnom vremenu
    """
    try:
        oid = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")

    update_data = {k: v for k, v in product.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    result = await products_collection.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Proizvod nije pronađen")

    updated = await products_collection.find_one({"_id": oid})
    return serialize_product(updated)

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """
    FZ 7.3 — Administrator deaktivira ili trajno brise artikal
    Koristimo soft delete (is_active=False) da sacuvamo historiju narudzbi
    """
    try:
        oid = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")

    result = await products_collection.update_one(
        {"_id": oid},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Proizvod nije pronađen")

    return {"message": "Proizvod uspješno deaktiviran"}

# ----------------------------------------------------------
# KATEGORIJE — FZ 1.2
# ----------------------------------------------------------

@app.get("/categories")
async def get_categories():
    """Vraca sve kategorije sa hijerarhijskom strukturom"""
    categories = []
    async for category in categories_collection.find():
        categories.append(serialize_category(category))
    return categories

@app.post("/categories", status_code=201)
async def create_category(category: CategoryCreate):
    """Kreira novu kategoriju, opciono sa parent_id za hijerarhiju"""
    category_dict = category.model_dump()
    category_dict["created_at"] = datetime.utcnow()

    result = await categories_collection.insert_one(category_dict)
    created = await categories_collection.find_one({"_id": result.inserted_id})
    return serialize_category(created)

# ----------------------------------------------------------
# HEALTH CHECK
# ----------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "product-catalog-service"}