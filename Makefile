RUN_PYTHON=docker-compose run --rm python

.PHONY: install
install:
	@test -f .env || (echo "🔨 Generating .env file using .env.dist" && cp .env.dist .env) || true
	docker-compose build
	docker-compose up -d localstack python  # Démarre tous les services nécessaires en arrière-plan

.PHONY: sh
sh:
	${RUN_PYTHON} sh

.PHONY: manage_buckets
manage_buckets:
	${RUN_PYTHON} env PYTHONPATH=/app python src/command/manage_buckets.py --empty=$(empty) --repo=$(repo) --dataset_name=$(dataset_name) --bucket_name=$(bucket_name)
