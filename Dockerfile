FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Need Node for the local npx MCP server demo
RUN apt-get update && apt-get install -y nodejs npm

COPY . .

# Cloud Run requires listening on PORT environment variable (default 8080)
ENV PORT=8080
CMD uvicorn app.main:api --host 0.0.0.0 --port $PORT
