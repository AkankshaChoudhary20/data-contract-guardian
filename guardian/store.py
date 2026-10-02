import json
from contextlib import contextmanager
import sqlite3
from pathlib import Path

@contextmanager
def connect(path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(path,timeout=10)
    conn.row_factory=sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS contracts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, version INTEGER NOT NULL, schema TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(name,version))')
    try:
        with conn: yield conn
    finally: conn.close()

def save(path,name,schema):
    with connect(path) as conn:
        conn.execute('BEGIN IMMEDIATE')
        version=conn.execute('SELECT COALESCE(MAX(version),0)+1 FROM contracts WHERE name=?',(name,)).fetchone()[0]
        cur=conn.execute('INSERT INTO contracts(name,version,schema) VALUES (?,?,?)',(name,version,json.dumps(schema)))
        return get_row(conn.execute('SELECT * FROM contracts WHERE id=?',(cur.lastrowid,)).fetchone())

def get_row(row):
    return {**dict(row),'schema':json.loads(row['schema'])}

def list_all(path):
    with connect(path) as conn: return [get_row(r) for r in conn.execute('SELECT * FROM contracts ORDER BY id DESC')]

def get(path,id):
    with connect(path) as conn:
        row=conn.execute('SELECT * FROM contracts WHERE id=?',(id,)).fetchone()
        return get_row(row) if row else None
