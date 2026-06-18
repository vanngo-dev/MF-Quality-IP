STREAMING_TOPICS := station.events sensor.readings quality.defects quality.alerts investigation.events
BROKER ?= localhost:19092
DOCKER_BROKER ?= redpanda:9092
RANDOM_COUNT ?= 100

.PHONY: install up down reset demo-infra demo-data demo-app demo migrate seed create-topics produce-demo-events produce-random-events produce-defect-spike run-worker test test-api test-worker test-event-generator test-frontend test-e2e run-ingestion-demo reindex-search logs status up-streaming

install:
	cd backend && pip install -e .
	cd worker && pip install -e .
	cd event-generator && pip install -e .
	cd frontend && npm install
	cd e2e && npm install

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v

up-streaming:
	docker compose up -d redpanda redpanda-console

demo-infra:
	docker compose up -d --wait postgres redpanda redpanda-console elasticsearch

demo-data: migrate seed create-topics produce-defect-spike

demo-app:
	docker compose up -d backend worker frontend

demo: demo-infra demo-data demo-app status

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	docker compose run --rm backend python -m app.db.seed

create-topics:
	-docker compose exec redpanda rpk topic create $(STREAMING_TOPICS)
	docker compose exec redpanda rpk topic list

produce-demo-events:
	docker compose --profile tools run --rm event-generator python -m app.main --mode deterministic --publish --broker $(DOCKER_BROKER)

produce-random-events:
	docker compose --profile tools run --rm event-generator python -m app.main --mode random --count $(RANDOM_COUNT) --publish --broker $(DOCKER_BROKER)

produce-defect-spike:
	docker compose --profile tools run --rm event-generator python -m app.main --mode defect-spike --publish --broker $(DOCKER_BROKER)

run-worker:
	cd worker && python -m app.main --broker $(BROKER)

test: test-api test-worker test-event-generator test-frontend

test-api:
	cd backend && pytest

test-worker:
	cd worker && pytest

test-event-generator:
	cd event-generator && pytest

test-frontend:
	cd frontend && npm run test:run

run-ingestion-demo: create-topics
	cd event-generator && python -m app.main --mode deterministic --publish --broker $(BROKER)

reindex-search:
	docker compose run --rm backend python -m app.search.reindex

test-e2e:
	cd e2e && npx playwright test

logs:
	docker compose logs -f

status:
	docker compose ps
