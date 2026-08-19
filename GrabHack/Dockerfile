FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Serve through gunicorn, not `python app.py`. Flask's built-in server is
# single-threaded and not intended for production traffic. Render injects PORT,
# so fall back to 8000 for plain `docker run` / docker-compose.
# One worker: SQLite is a single file here, and concurrent writers from multiple
# processes would contend on the write lock.
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 120"]
