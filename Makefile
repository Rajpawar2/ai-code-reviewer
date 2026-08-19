.PHONY: install test run-backend run-frontend migrate lint build docker-up docker-down

install:
	cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

test:
	cd backend && source .venv/bin/activate && pytest -v

lint:
	cd backend && source .venv/bin/activate && ruff check .

migrate:
	cd backend && source .venv/bin/activate && alembic upgrade head

run-backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
