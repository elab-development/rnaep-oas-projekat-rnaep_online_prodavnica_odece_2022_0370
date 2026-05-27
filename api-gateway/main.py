import os
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Velura API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL")
PRODUCT_CATALOG_URL = os.getenv("PRODUCT_CATALOG_URL")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Nevazeci token")

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials)
    if payload.get("rola") != "administrator":
        raise HTTPException(status_code=403, detail="Pristup dozvoljen samo administratorima")
    return payload

def verify_owner_or_admin(korisnik_id: int, payload: dict):
    token_user_id = payload.get("sub")
    if token_user_id is None:
        raise HTTPException(status_code=401, detail="Nevazeci token")
    if int(token_user_id) != korisnik_id and payload.get("rola") != "administrator":
        raise HTTPException(status_code=403, detail="Nemate pristup ovom resursu")

def proxied(response: httpx.Response) -> JSONResponse:
    return JSONResponse(content=response.json(), status_code=response.status_code)

async def forward_request(url: str, method: str, headers: dict, body: bytes = None):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
        return response
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Mikroservis nije odgovorio na vreme")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Mikroservis nije dostupan")


@app.post("/api/users/register")
async def register(request: Request):
    body = await request.body()
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/auth/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=body
    )
    return proxied(response)

@app.post("/api/users/login")
async def login(request: Request):
    body = await request.body()
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/auth/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=body
    )
    return proxied(response)

@app.get("/api/users/{korisnik_id}")
async def get_profile(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)

@app.post("/api/users/{korisnik_id}/adrese")
async def dodaj_adresu(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    body = await request.body()
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}/adrese",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return proxied(response)

@app.get("/api/users/{korisnik_id}/adrese")
async def get_adrese(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}/adrese",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/api/products")
async def get_products(request: Request):
    query = str(request.query_params)
    url = f"{PRODUCT_CATALOG_URL}/products"
    if query:
        url += f"?{query}"
    response = await forward_request(url=url, method="GET", headers={})
    return proxied(response)

@app.get("/api/products/search")
async def search_products(request: Request):
    query = str(request.query_params)
    url = f"{PRODUCT_CATALOG_URL}/products/search"
    if query:
        url += f"?{query}"
    response = await forward_request(url=url, method="GET", headers={})
    return proxied(response)

@app.get("/api/products/{product_id}")
async def get_product(product_id: str, request: Request):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="GET",
        headers={}
    )
    return proxied(response)

@app.get("/api/categories")
async def get_categories(request: Request):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/categories",
        method="GET",
        headers={}
    )
    return proxied(response)

@app.post("/api/products")
async def create_product(request: Request, payload: dict = Depends(verify_admin)):
    body = await request.body()
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return proxied(response)

@app.put("/api/products/{product_id}")
async def update_product(product_id: str, request: Request, payload: dict = Depends(verify_admin)):
    body = await request.body()
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="PUT",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return proxied(response)

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/api/cart/{korisnik_id}")
async def get_cart(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)

@app.post("/api/cart/{korisnik_id}/items")
async def add_to_cart(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    body = await request.body()
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}/items",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return proxied(response)

@app.delete("/api/cart/{korisnik_id}/items/{stavka_id}")
async def remove_from_cart(korisnik_id: int, stavka_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}/items/{stavka_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)

@app.post("/api/orders/{korisnik_id}")
async def create_order(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    body = await request.body()
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{korisnik_id}",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return proxied(response)

@app.get("/api/orders/{korisnik_id}")
async def get_orders(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{korisnik_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)

@app.get("/api/orders/{korisnik_id}/{narudzba_id}")
async def get_order(korisnik_id: int, narudzba_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{korisnik_id}/{narudzba_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/api/users")
async def get_all_users(request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users", # Ovo zahteva da tvoj users-service ima @app.get("/users")
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)
