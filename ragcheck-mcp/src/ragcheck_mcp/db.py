import sqlite3
import os
import json
from pathlib import Path

class WorkspaceDB:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.ragcheck_dir = self.workspace_dir / ".ragcheck"
        self.ragcheck_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.ragcheck_dir / "ragcheck.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    metadata TEXT,
                    content TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER,
                    chunk_index INTEGER,
                    content TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    context TEXT,
                    answer TEXT,
                    difficulty TEXT
                )
            ''')
            conn.commit()

    def insert_document(self, file_path: str, content: str, metadata: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM documents WHERE file_path = ?', (file_path,))
            existing = cursor.fetchone()
            if existing:
                doc_id = existing[0]
                cursor.execute(
                    'UPDATE documents SET metadata = ?, content = ? WHERE id = ?',
                    (json.dumps(metadata), content, doc_id)
                )
                cursor.execute('DELETE FROM chunks WHERE doc_id = ?', (doc_id,))
                return doc_id
            cursor.execute(
                'INSERT INTO documents (file_path, metadata, content) VALUES (?, ?, ?)',
                (file_path, json.dumps(metadata), content)
            )
            return cursor.lastrowid

    def insert_chunks(self, doc_id: int, chunks: list[str]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chunks WHERE doc_id = ?', (doc_id,))
            for i, chunk in enumerate(chunks):
                cursor.execute(
                    'INSERT INTO chunks (doc_id, chunk_index, content) VALUES (?, ?, ?)',
                    (doc_id, i, chunk)
                )
            conn.commit()

    def get_all_chunks(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content FROM chunks')
            return [row[0] for row in cursor.fetchall()]

    def save_test(self, question: str, context: str, answer: str, difficulty: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO generated_tests (question, context, answer, difficulty) VALUES (?, ?, ?, ?)',
                (question, context, answer, difficulty)
            )
            conn.commit()
