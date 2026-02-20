# PDF Notes Retriever - Web App

Simple Flask app that:
- loads sentence-transformer embeddings for PDF filenames in `notes/`
- exposes `POST /api/search` to find the most relevant PDF
- serves a web UI at `/` to preview and download the matched PDF

## Local run

1. Install dependencies:
```powershell
python -m pip install -r requirements.txt
```

2. Put your `.pdf` files into `notes/`.

3. Start app:
```powershell
python app.py
```

4. Open `http://127.0.0.1:5000/`.

## Deploy (Render)

1. Push this project to GitHub.
2. In Render, create a new **Web Service** from the repo.
3. Use:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Deploy.

Files already included for deployment:
- `Procfile` -> `web: gunicorn app:app`
- `runtime.txt` -> Python version pin
- `requirements.txt` -> includes `gunicorn`

## Notes

- The first startup can be slower because model weights may download.
- `notes/` must contain PDFs in production too.
- Some hosts have ephemeral storage, so runtime file uploads may not persist.
