import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import psycopg2
from app import app, get_conn, update_items_count  # замените 'app' на имя вашего файла

client = TestClient(app)

# Моки для базы данных
@pytest.fixture
def mock_db():
    with patch('app.psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_connect, mock_conn, mock_cursor

def test_create_item(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = [1]
    
    response = client.post("/items", json={"name": "test item"})
    
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "test item"}
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO items (name) VALUES (%s) RETURNING id;", ("test item",)
    )
    mock_conn.commit.assert_called_once()

def test_get_items(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [(1, "item 1"), (2, "item 2")]
    
    response = client.get("/items")
    
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "item 1"},
        {"id": 2, "name": "item 2"}
    ]
    mock_cursor.execute.assert_called_once_with("SELECT id, name FROM items;")

def test_metrics_endpoint(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    
    # Сначала сделаем несколько запросов чтобы увеличить счетчики
    client.get("/items")
    client.post("/items", json={"name": "test item"})
    
    response = client.get("/metrics")
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain; version=0.0.4; charset=utf-8"
    
    # Проверяем наличие некоторых метрик в ответе
    metrics_content = response.text
    assert "request_count" in metrics_content
    assert "request_latency_seconds" in metrics_content
    assert "db_connections_total" in metrics_content

def test_request_count_metric(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    
    for _ in range(3):
        client.get("/items")
    
    response = client.get("/metrics")
    metrics_content = response.text
    
    lines = metrics_content.split('\n')
    get_items_count_line = [line for line in lines if 'request_count{method="GET"' in line and 'endpoint="/items"' in line]
    
    assert len(get_items_count_line) > 0
    assert '3.0' in get_items_count_line[0]

def test_db_connections_metric(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    
    client.get("/items")
    
    response = client.get("/metrics")
    metrics_content = response.text
    
    assert "db_connections_total" in metrics_content

def test_update_items_count(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = [5]
    
    update_items_count()
    
    mock_cursor.execute.assert_called_with("SELECT COUNT(*) FROM items;")

def test_middleware_records_metrics(mock_db):
    mock_connect, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    
    response = client.get("/items")
    
    response = client.get("/metrics")
    metrics_content = response.text
    
    assert 'request_count{method="GET",endpoint="/items",http_status="200"}' in metrics_content
    assert 'request_latency_seconds_bucket{method="GET",endpoint="/items"' in metrics_content

def test_invalid_endpoint_returns_404():
    response = client.get("/nonexistent")
    assert response.status_code == 404
    
    metrics_response = client.get("/metrics")
    metrics_content = metrics_response.text
    assert 'request_count{method="GET",endpoint="/nonexistent",http_status="404"}' in metrics_content
