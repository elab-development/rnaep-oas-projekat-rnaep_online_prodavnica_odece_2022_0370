from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from database import products_collection, categories_collection
from models import ProductCreate, ProductUpdate, CategoryCreate
from bson import ObjectId
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

app = FastAPI(title="Product Catalog Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def serialize_product(product) -> dict:
    product["id"] = str(product["_id"])
    del product["_id"]
    return product

def serialize_category(category) -> dict:
    category["id"] = str(category["_id"])
    del category["_id"]
    return category

@app.get("/products")
async def get_all_products():
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
    try:
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
    except:
        raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")

    if not product:
        raise HTTPException(status_code=404, detail="Proizvod nije pronađen")

    return serialize_product(product)

@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()

    result = await products_collection.insert_one(product_dict)
    created = await products_collection.find_one({"_id": result.inserted_id})
    return serialize_product(created)

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductUpdate):
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

@app.get("/categories")
async def get_categories():
    categories = []
    async for category in categories_collection.find():
        categories.append(serialize_category(category))
    return categories

@app.post("/categories", status_code=201)
async def create_category(category: CategoryCreate):
    category_dict = category.model_dump()
    category_dict["created_at"] = datetime.utcnow()

    result = await categories_collection.insert_one(category_dict)
    created = await categories_collection.find_one({"_id": result.inserted_id})
    return serialize_category(created)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "product-catalog-service"}


