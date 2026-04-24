.PHONY: install backend frontend test clean

install:
	cd backend && uv pip install -r requirements.txt
	cd frontend && bun install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && bun run dev

dev: backend frontend

clean:
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	cd frontend && rm -rf node_modules dist
