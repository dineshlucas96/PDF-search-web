from flask import Flask, request, jsonify, send_from_directory, render_template, abort
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_NOTES_FOLDER = os.path.join(BASE_DIR, "notes")
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Runtime state, initialized at startup.
model = None
model_error = None
pdf_files = []
pdf_names = []
pdf_embeddings = np.array([])


def load_pdfs(folder):
    files = []
    names = []
    if not os.path.isdir(folder):
        return files, names

    for file in os.listdir(folder):
        if file.lower().endswith('.pdf'):
            files.append(file)
            names.append(file.replace('_', ' ').replace('.pdf', ''))
    return files, names


def init_resources():
    global model, model_error, pdf_files, pdf_names, pdf_embeddings

    notes_folder = os.environ.get('NOTES_FOLDER', DEFAULT_NOTES_FOLDER)
    model_name = os.environ.get('EMBED_MODEL_NAME', DEFAULT_MODEL_NAME)

    pdf_files, pdf_names = load_pdfs(notes_folder)

    try:
        model = SentenceTransformer(model_name)
        if pdf_names:
            pdf_embeddings = model.encode(pdf_names)
        else:
            pdf_embeddings = np.array([])
        model_error = None
    except Exception as exc:
        model = None
        model_error = str(exc)
        pdf_embeddings = np.array([])


# Initialize on import so gunicorn workers are ready to serve requests.
init_resources()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/healthz')
def healthz():
    status = {
        'ok': model is not None,
        'model_loaded': model is not None,
        'pdf_count': len(pdf_files),
    }
    if model_error:
        status['error'] = model_error
    return jsonify(status), (200 if model is not None else 503)


@app.route('/api/search', methods=['POST'])
def search():
    if model is None:
        return jsonify({'error': 'model_unavailable', 'details': model_error}), 503

    data = request.get_json() or {}
    query = (data.get('query') or '').strip()
    if not query:
        return jsonify({'error': 'empty query'}), 400
    if pdf_embeddings.size == 0:
        return jsonify({'error': 'no_pdfs_found'}), 400

    q_emb = model.encode([query])
    sims = cosine_similarity(q_emb, pdf_embeddings)[0]
    idx = int(np.argmax(sims))
    filename = pdf_files[idx]
    name = pdf_names[idx]
    url = f'/pdf/{filename}'
    download_url = f'/download/{filename}'
    return jsonify({'name': name, 'url': url, 'download_url': download_url})


@app.route('/pdf/<path:filename>')
def serve_pdf(filename):
    notes_folder = os.environ.get('NOTES_FOLDER', DEFAULT_NOTES_FOLDER)
    if filename not in pdf_files:
        abort(404)
    return send_from_directory(notes_folder, filename)


@app.route('/download/<path:filename>')
def download_pdf(filename):
    notes_folder = os.environ.get('NOTES_FOLDER', DEFAULT_NOTES_FOLDER)
    if filename not in pdf_files:
        abort(404)
    return send_from_directory(notes_folder, filename, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host=host, port=port, debug=debug)
