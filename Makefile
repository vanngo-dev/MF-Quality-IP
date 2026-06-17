STREAMING_TOPICS := station.events sensor.readings quality.defects quality.alerts investigation.events
BROKER ?= localhost:19092
RANDOM_COUNT ?= 100

.PHONY: up-streaming create-topics produce-demo-events produce-random-events produce-defect-spike run-worker test-worker run-ingestion-demo reindex-search

up-streaming:
	docker compose up redpanda redpanda-console

create-topics:
	docker compose exec redpanda rpk topic create $(STREAMING_TOPICS)
	docker compose exec redpanda rpk topic list

produce-demo-events:
	cd event-generator && python -m app.main --mode deterministic --publish --broker $(BROKER)

produce-random-events:
	cd event-generator && python -m app.main --mode random --count $(RANDOM_COUNT) --publish --broker $(BROKER)

produce-defect-spike:
	cd event-generator && python -m app.main --mode defect-spike --publish --broker $(BROKER)

run-worker:
	cd worker && python -m app.main --broker $(BROKER)

test-worker:
	cd worker && pytest

run-ingestion-demo: create-topics
	cd event-generator && python -m app.main --mode deterministic --publish --broker $(BROKER)

reindex-search:
	cd backend && python -m app.search.reindex
