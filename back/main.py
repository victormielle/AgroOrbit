from flask import Flask, jsonify, request
import psycopg
import os
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer
from flask_cors import CORS
import PyPDF2

app = Flask(__name__)
CORS(app, origins=["*"], allow_headers="*", supports_credentials=True)
load_dotenv()

def get_conn():
    db_host = os.getenv("DB_HOST")
    sslmode = "disable" if db_host in ("localhost", "127.0.0.1") else "require"
    conn = psycopg.connect(
        host=db_host,
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=sslmode
    )
    return conn

VECTOR_DIM = 384  # Exemplo para OpenAI ada-002

def init_vector_table():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename TEXT,
                    content TEXT,
                    embedding vector({VECTOR_DIM})
                );
            ''')
            conn.commit()

@app.route('/api/data', methods=['GET'])
def get_data():
    # Your code to retrieve and return data
    return jsonify({"message": "Hello, World!"})

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def split_chunks(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size].strip())
        start += size - overlap
    return [c for c in chunks if c]

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            content = "\n".join(page.extract_text() or '' for page in pdf_reader.pages)
        except Exception as e:
            return jsonify({'error': f'Erro ao ler PDF: {e}'}), 400
    else:
        content = file.read().decode('utf-8')

    chunks = split_chunks(content)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE filename = %s", (file.filename,))
            for chunk in chunks:
                emb = get_embedding(chunk)
                cur.execute(
                    "INSERT INTO documents (filename, content, embedding) VALUES (%s, %s, %s)",
                    (file.filename, chunk, emb.tolist())
                )
            conn.commit()
    return jsonify({'message': f'File uploaded and indexed in {len(chunks)} chunks'})

# Carregue o modelo uma vez (fora da função)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    emb = embedder.encode([text])[0]
    return np.array(emb)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')
    doc_id = data.get('doc_id')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    if not doc_id:
        return jsonify({'error': 'No document selected'}), 400
    # Resolve filename pelo id (qualquer chunk do doc)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT filename FROM documents WHERE id = %s", (doc_id,))
            row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Document not found'}), 404
    filename = row[0]
    q_emb = get_embedding(question)
    vector_str = '[' + ','.join(str(x) for x in q_emb.tolist()) + ']'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, content, embedding <-> %s::vector AS distance
                FROM documents
                WHERE filename = %s
                ORDER BY embedding <-> %s::vector ASC
                LIMIT 3
                """,
                (vector_str, filename, vector_str)
            )
            results = cur.fetchall()
    docs = [{'filename': r[0], 'content': r[1], 'distance': float(r[2])} for r in results]
    return jsonify({'matches': docs})

@app.route('/ask_all', methods=['POST'])
def ask_all():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    q_emb = get_embedding(question)
    vector_str = '[' + ','.join(str(x) for x in q_emb.tolist()) + ']'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, content, embedding <-> %s::vector AS distance
                FROM documents
                ORDER BY embedding <-> %s::vector ASC
                LIMIT 3
                """,
                (vector_str, vector_str)
            )
            results = cur.fetchall()
    docs = [
        {'filename': r[0], 'content': r[1], 'distance': float(r[2])}
        for r in results
    ]
    return jsonify({'matches': docs})

@app.route('/documents', methods=['GET'])
def list_documents():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT MIN(id), filename FROM documents GROUP BY filename ORDER BY MIN(id) DESC")
            docs = [{'id': row[0], 'filename': row[1]} for row in cur.fetchall()]
    return jsonify({'documents': docs})

# Inicializar tabela vetorial ao iniciar
init_vector_table()

# Exemplo de uso:
if __name__ == "__main__":
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(cur.fetchone())
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)
