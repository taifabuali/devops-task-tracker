import os

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)
_table_ready = False


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "taskuser"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "tasks"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def ensure_table(conn):
    global _table_ready
    if _table_ready:
        return
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "title VARCHAR(255) NOT NULL,"
            "done BOOLEAN NOT NULL DEFAULT FALSE,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
    _table_ready = True


@app.get("/health")
def health():
    return jsonify(status="ok", version=os.getenv("APP_VERSION", "dev"))


@app.get("/api/tasks")
def list_tasks():
    conn = get_db()
    try:
        ensure_table(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    conn = get_db()
    try:
        ensure_table(conn)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
            return jsonify(id=cur.lastrowid, title=title, done=False), 201
    finally:
        conn.close()


@app.put("/api/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    conn = get_db()
    try:
        ensure_table(conn)
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s", (task_id,))
            return jsonify(updated=cur.rowcount)
    finally:
        conn.close()


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    conn = get_db()
    try:
        ensure_table(conn)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return jsonify(deleted=cur.rowcount)
    finally:
        conn.close()
