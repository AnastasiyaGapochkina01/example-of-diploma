from fastapi import FastAPI, Request
from pydantic import BaseModel
import psycopg2
import os
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from starlette.responses import Response

app = FastAPI()

# Метрики
REQUEST_COUNT = Counter(
    'request_count', 
    'Total request count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency',
    ['method', 'endpoint']
)
DB_CONNECTIONS = Gauge(
    'db_connections_total',
    'Total number of database connections'
)
ITEMS_COUNT = Gauge(
    'items_total',
    'Total number of items in database'
)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def get_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    DB_CONNECTIONS.inc()  # Увеличиваем счетчик подключений
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    DB_CONNECTIONS.dec()  # Уменьшаем счетчик подключений

init_db()

class Item(BaseModel):
    name: str

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response

@app.post("/items")
def create_item(item: Item):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id;", (item.name,))
    item_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    DB_CONNECTIONS.dec()
    
    # Обновляем счетчик items
    update_items_count()
    
    return {"id": item_id, "name": item.name}

@app.get("/items")
def get_items():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    DB_CONNECTIONS.dec()
    
    # Обновляем счетчик items
    update_items_count()
    
    return [{"id": r[0], "name": r[1]} for r in rows]

def update_items_count():
    """Обновляет метрику с количеством items в базе"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM items;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    DB_CONNECTIONS.dec()
    ITEMS_COUNT.set(count)

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )
