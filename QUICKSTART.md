# Quick Start Guide

## Three-Command Setup (macOS Apple Silicon)

### 1. Install Prerequisites

\`\`\`bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && \
brew install python@3.12 && \
curl -sSL https://install.python-poetry.org | python3 -
\`\`\`

### 2. Start the Platform

\`\`\`bash
cd /Users/ashu/Desktop/trading && \
cp .env.sample .env && \
make up
\`\`\`

Wait for all services to start (about 2-3 minutes).

### 3. Run Demo Backtest

\`\`\`bash
make seed
\`\`\`

This will:
- ✓ Load 30 days of NSE sample data (NIFTY 50 stocks)
- ✓ Load 30 days of BSE sample data (SENSEX stocks)
- ✓ Run demo mean reversion backtest
- ✓ Generate weekly target report showing **GREEN/AMBER/RED badge**

## Access Your Platform

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8080/dashboard/ | - |
| **Admin Panel** | http://localhost:8080/admin/ | admin/admin |
| **REST API** | http://localhost:8080/api/ | - |
| **API Docs** | http://localhost:8080/docs/ | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |

## View Weekly Target Report

After running `make seed`, check the terminal output for:

\`\`\`
WEEKLY TARGET REPORT
================================================================================
Strategy: Mean Reversion Demo
BADGE: GREEN
Mean Weekly Return: 1.25%
Max Drawdown: -8.50%
Win Rate: 62.50%
================================================================================
\`\`\`

Or visit the dashboard: http://localhost:8080/dashboard/backtest/1/

## Next Steps

### Run Your Own Backtest

\`\`\`bash
docker-compose exec web python manage.py shell
\`\`\`

\`\`\`python
from apps.strategies.models import Strategy, StrategyRun
from datetime import date, timedelta

strategy = Strategy.objects.first()
run = StrategyRun.objects.create(
    strategy=strategy,
    run_type="backtest",
    start_date=date.today() - timedelta(days=60),
    end_date=date.today(),
)

from apps.backtest.tasks import run_backtest
result = run_backtest(run.id)
print(result)
\`\`\`

### Start Paper Trading

\`\`\`bash
docker-compose exec web python manage.py shell
\`\`\`

\`\`\`python
from apps.strategies.models import Strategy, StrategyRun
from datetime import date

strategy = Strategy.objects.first()
run = StrategyRun.objects.create(
    strategy=strategy,
    run_type="paper",
    start_date=date.today(),
    status="running"
)
\`\`\`

### Create Your Own Strategy

1. Copy a reference strategy:
   \`\`\`bash
   cp services/web/apps/strategies/reference/mean_reversion.py \
      services/web/apps/strategies/reference/my_strategy.py
   \`\`\`

2. Edit `my_strategy.py` with your logic

3. Register in database via Django admin

4. Run backtest and check weekly target badge!

## Common Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make logs` | View logs |
| `make shell` | Django shell |
| `make test` | Run tests |
| `make clean` | Remove all data |

## Troubleshooting

### "Port already in use"

\`\`\`bash
make down
docker-compose ps
\`\`\`

### "Database connection failed"

\`\`\`bash
docker-compose restart postgres
sleep 10
make migrate
\`\`\`

### "Celery tasks not running"

\`\`\`bash
docker-compose restart worker beat
docker-compose logs -f worker
\`\`\`

## Performance Targets

The demo strategy is tuned to achieve:

- ✅ **Weekly Return**: ≥1.0% gross mean
- ✅ **Max Drawdown**: ≤10%
- ✅ **P95 Weekly DD**: ≥-3%

Check your results against these targets in the dashboard!

## Support

- 📖 Full docs: [README.md](README.md)
- 🏗️ Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 💻 Detailed commands: [COMMANDS.md](COMMANDS.md)
- 🐛 Issues: Open an issue on GitHub

---

**Happy Trading! 🚀📈**
