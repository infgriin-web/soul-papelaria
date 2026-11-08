import os
import sqlite3
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.path.join(os.path.dirname(__file__), "soul_papelaria.db")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Default admin credentials
ADMIN_USER = "admin"
ADMIN_PASS = "soul123"
ADMIN_TOKEN = "soul-papelaria-secure-session-token-2024"

app = FastAPI(title="SOUL Papelaria Personalizada API")

# Allow CORS so it can be accessed from any client/domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Store settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            icon TEXT DEFAULT '🎁',
            theme TEXT DEFAULT 'default'
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_slug TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            badge TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Seed default settings
    default_settings = {
        "store_name": "SOUL PAPELARIA PERSONALIZADA",
        "tagline": "Encanto, afeto e sofisticação em papelaria fina",
        "whatsapp": "5511999999999",
        "primary_color": "#6A1A24",
        "bg_color": "#FAF7F2",
        "christmas_mode": "true",
        "welcome_message": "Olá! Gostaria de fazer uma encomenda na Soul Papelaria:"
    }
    for k, v in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
    # Seed default categories
    cursor.execute("SELECT count(*) as cnt FROM categories")
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute("INSERT INTO categories (name, slug, icon, theme) VALUES (?, ?, ?, ?)", 
                       ("Especial de Natal", "natal", "🎄", "natal"))
        cursor.execute("INSERT INTO categories (name, slug, icon, theme) VALUES (?, ?, ?, ?)", 
                       ("Papelaria Criativa", "papelaria", "✒️", "papelaria"))
        cursor.execute("INSERT INTO categories (name, slug, icon, theme) VALUES (?, ?, ?, ?)", 
                       ("Planners & Agendas", "planners", "📖", "papelaria"))
        cursor.execute("INSERT INTO categories (name, slug, icon, theme) VALUES (?, ?, ?, ?)", 
                       ("Lembrancinhas & Mimos", "lembrancinhas", "🎀", "papelaria"))

    # Seed initial products
    cursor.execute("SELECT count(*) as cnt FROM products")
    if cursor.fetchone()["cnt"] == 0:
        initial_products = [
            (
                "Caixa Cartão de Natal com Mini Vela Aromática",
                "natal",
                34.90,
                "Caixa personalizada em papel fosco nobre off-white com gravação bordô e dourada, contendo mini vela perfumada de especiarias natalinas e laço de cetim bordô.",
                "https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=600&auto=format&fit=crop&q=80",
                "Mais Pedido de Natal"
            ),
            (
                "Kit Tags Natalinas Exclusivas (12 unidades)",
                "natal",
                18.50,
                "Tags para presentes recortadas à laser em papel vergê 240g, detalhes metalizados e cordão rústico de algodão cru.",
                "https://images.unsplash.com/photo-1543257580-7269da773bf5?w=600&auto=format&fit=crop&q=80",
                "Edição de Natal"
            ),
            (
                "Planner Anual Soul 2025 - Capa Bordô Clássica",
                "planners",
                89.90,
                "Planner com capa dura aveludada bordô, foil dourado com seu nome gravado, folhas 120g que não transferem tinta, divisórias com abas e cartela de adesivos.",
                "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=600&auto=format&fit=crop&q=80",
                "Destaque"
            ),
            (
                "Caderno Universitário Personalizado Minimalista",
                "papelaria",
                48.00,
                "Caderno encadernado em wire-o dourado, miolo pautado ou pontilhado, bolsa interna de papel kraft e elástico bordô para fechamento.",
                "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
                "Novo"
            ),
            (
                "Bloco de Notas de Mesa 'Lista de Tarefas & Gratidão'",
                "papelaria",
                24.90,
                "Blocado com 80 folhas off-white destacáveis com acabamento premium e detalhe floral nobre.",
                "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=600&auto=format&fit=crop&q=80",
                ""
            ),
            (
                "Kit Bolinhas de Natal Acrílicas Personalizadas (Kit com 4)",
                "natal",
                52.00,
                "Bolinhas acrílicas transparentes com glitter ouro/prata, nome da família ou palavras de bênção em caligrafia moderna e laço bordô.",
                "https://images.unsplash.com/photo-1514517220017-8ce97a34a7b6?w=600&auto=format&fit=crop&q=80",
                "Edição Limitada"
            )
        ]
        cursor.executemany(
            "INSERT INTO products (title, category_slug, price, description, image_url, badge) VALUES (?, ?, ?, ?, ?, ?)",
            initial_products
        )
    conn.commit()
    conn.close()

init_db()

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class ProductCreate(BaseModel):
    title: str
    category_slug: str
    price: float
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    badge: Optional[str] = ""

class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = "✨"
    theme: Optional[str] = "default"

class SettingsUpdate(BaseModel):
    store_name: Optional[str] = None
    tagline: Optional[str] = None
    whatsapp: Optional[str] = None
    christmas_mode: Optional[str] = None

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    return True

# API Routes
@app.post("/api/login")
def login(creds: LoginRequest):
    if creds.username.strip() == ADMIN_USER and creds.password.strip() == ADMIN_PASS:
        return {"success": True, "token": ADMIN_TOKEN, "username": ADMIN_USER}
    raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

@app.get("/api/config")
def get_config():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()
    return settings

@app.post("/api/config")
def update_config(data: SettingsUpdate, authorized: bool = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    if data.store_name is not None:
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'store_name'", (data.store_name,))
    if data.tagline is not None:
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'tagline'", (data.tagline,))
    if data.whatsapp is not None:
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'whatsapp'", (data.whatsapp,))
    if data.christmas_mode is not None:
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'christmas_mode'", (data.christmas_mode,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/categories")
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY id ASC")
    rows = cursor.fetchall()
    categories = [dict(row) for row in rows]
    conn.close()
    return categories

@app.post("/api/categories")
def add_category(cat: CategoryCreate, authorized: bool = Depends(verify_token)):
    slug = cat.name.lower().strip().replace(" ", "-").replace("ã", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c")
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (name, slug, icon, theme) VALUES (?, ?, ?, ?)",
            (cat.name.strip(), slug, cat.icon or "✨", cat.theme or "default")
        )
        conn.commit()
        cat_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Esta categoria já existe!")
    conn.close()
    return {"success": True, "id": cat_id, "slug": slug}

@app.delete("/api/categories/{cat_id}")
def delete_category(cat_id: int, authorized: bool = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/products")
def get_products(category: Optional[str] = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    if category and category != "all":
        cursor.execute("SELECT * FROM products WHERE is_active = 1 AND category_slug = ? ORDER BY id DESC", (category,))
    else:
        cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY id DESC")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

@app.post("/api/products")
def create_product(prod: ProductCreate, authorized: bool = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (title, category_slug, price, description, image_url, badge) VALUES (?, ?, ?, ?, ?, ?)",
        (prod.title.strip(), prod.category_slug, prod.price, prod.description, prod.image_url, prod.badge)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"success": True, "id": new_id}

@app.delete("/api/products/{prod_id}")
def delete_product(prod_id: int, authorized: bool = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (prod_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# Static routes
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/admin")
def serve_admin():
    return FileResponse(os.path.join(STATIC_DIR, "admin.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

