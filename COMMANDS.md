# Complete Setup Commands for macOS Apple Silicon

## Prerequisites Installation

\`\`\`bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.12

curl -sSL https://install.python-poetry.org | python3 -

export PATH="$HOME/.local/bin:$PATH"
\`\`\`

## Repository Setup

\`\`\`bash
cd /Users/ashu/Desktop/trading

cp .env.sample .env
\`\`\`

## Start the Platform

\`\`\`bash
docker-compose up -d --build

docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@trading.com || true
\`\`\`

## Load Sample Data and Run Demo

\`\`\`bash
docker-compose exec web python manage.py load_nse_sample

docker-compose exec web python manage.py load_bse_sample

docker-compose exec web python manage.py build_minute_bars

docker-compose exec web python manage.py run_demo_backtest

docker-compose exec web python manage.py generate_weekly_report
\`\`\`

## Access the Platform

- Dashboard: http://localhost:8080/dashboard/
- Admin: http://localhost:8080/admin/ (admin/admin)
- API: http://localhost:8080/api/
- Docs: http://localhost:8080/docs/
- Grafana: http://localhost:3000 (admin/admin)

## View Logs

\`\`\`bash
docker-compose logs -f web
\`\`\`

## Stop Everything

\`\`\`bash
docker-compose down
\`\`\`

## Complete Reset

\`\`\`bash
docker-compose down -v
docker system prune -a --volumes
\`\`\`
