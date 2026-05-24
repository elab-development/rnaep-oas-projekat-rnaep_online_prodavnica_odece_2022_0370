import os
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
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
        raise HTTPException(status_code=401, detail="Nevazeći token")

async def forward_request(url: str, method: str, headers: dict, body: bytes = None):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            content=body
        )
    return response


@app.post("/api/users/register")
async def register(request: Request):
    body = await request.body()
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=body
    )
    return response.json()

@app.post("/api/users/login")
async def login(request: Request):
    body = await request.body()
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=body
    )
    return response.json()


@app.get("/api/users/profile")
async def get_profile(request: Request, payload: dict = Depends(verify_token)):
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/profile",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return response.json()

@app.put("/api/users/profile")
async def update_profile(request: Request, payload: dict = Depends(verify_token)):
    body = await request.body()
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/profile",
        method="PUT",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return response.json()


@app.get("/api/products")
async def get_products(request: Request):
    query = str(request.query_params)
    url = f"{PRODUCT_CATALOG_URL}/products"
    if query:
        url += f"?{query}"
    response = await forward_request(url=url, method="GET", headers={})
    return response.json()

@app.get("/api/products/{product_id}")
async def get_product(product_id: str, request: Request):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="GET",
        headers={}
    )
    return response.json()

@app.get("/api/categories")
async def get_categories(request: Request):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/categories",
        method="GET",
        headers={}
    )
    return response.json()



@app.post("/api/products")
async def create_product(request: Request, payload: dict = Depends(verify_token)):
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
    return response.json()

@app.put("/api/products/{product_id}")
async def update_product(product_id: str, request: Request, payload: dict = Depends(verify_token)):
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
    return response.json()

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, request: Request, payload: dict = Depends(verify_token)):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return response.json()



@app.get("/api/cart")
async def get_cart(request: Request, payload: dict = Depends(verify_token)):
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return response.json()

@app.post("/api/cart")
async def add_to_cart(request: Request, payload: dict = Depends(verify_token)):
    body = await request.body()
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return response.json()

@app.delete("/api/cart/{item_id}")
async def remove_from_cart(item_id: int, request: Request, payload: dict = Depends(verify_token)):
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{item_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return response.json()

@app.post("/api/orders")
async def create_order(request: Request, payload: dict = Depends(verify_token)):
    body = await request.body()
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=body
    )
    return response.json()

@app.get("/api/orders")
async def get_orders(request: Request, payload: dict = Depends(verify_token)):
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return response.json()

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, request: Request, payload: dict = Depends(verify_token)):
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{order_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return response.json()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}