.PHONY: help dev up down seed test lint clean logs shell migrate

help:
	@echo "Available targets:"
	@echo "  dev      - Set up environment and run migrations"
	@echo "  up       - Bring stack up"
	@echo "  down     - Stop containers"
	@echo "  seed     - Load NSE/BSE samples and run demo backtest"
	@echo "  test     - Run tests with coverage"
	@echo "  lint     - Run ruff, black, mypy"
	@echo "  logs     - Tail logs from all services"
	@echo "  shell    - Django shell"
	@echo "  migrate  - Run Django migrations"
	@echo "  clean    - Remove containers and volumes"

dev:
	@echo "Setting up development environment..."
	cd services/web && poetry install
	cd services/exec && poetry install
	docker-compose up -d postgres redis
	@echo "Waiting for postgres..."
	sleep 5
	$(MAKE) migrate
	@echo "Development environment ready"

up:
	docker-compose up -d
	@echo "Stack is up. Web UI: http://localhost:8080"
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

down:
	docker-compose down

seed:
	@echo "Loading sample data and running demo backtest..."
	docker-compose exec web python manage.py load_nse_sample
	docker-compose exec web python manage.py load_bse_sample
	docker-compose exec web python manage.py build_minute_bars
	docker-compose exec web python manage.py run_demo_backtest
	docker-compose exec web python manage.py generate_weekly_report
	@echo "Demo backtest complete. Check http://localhost:8080/dashboard/backtest"

test:
	cd services/web && poetry run pytest --cov=apps --cov-report=html --cov-report=term-missing

lint:
	cd services/web && poetry run ruff check apps
	cd services/web && poetry run black --check apps
	cd services/web && poetry run mypy apps
	cd services/exec && poetry run ruff check app
	cd services/exec && poetry run black --check app

migrate:
	docker-compose exec web python manage.py migrate

shell:
	docker-compose exec web python manage.py shell

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf services/web/staticfiles
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
