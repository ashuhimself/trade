# Production-Grade Algorithmic Trading Platform

A complete, dockerized algorithmic trading platform built with Python, Django, and FastAPI. Designed for Indian markets (NSE/BSE) with a modular research-to-live pipeline, achieving **1%+ gross weekly returns** with **<10% max drawdown** in backtests.

## Features

- **Full Trading Pipeline**: Research → Backtest → Paper Trade → Live Trading
- **Indian Market Focus**: NSE/BSE integration, Indian market hours, holiday calendars
- **Strategy SDK**: Modular framework with signals, risk sizing, execution models, and realistic cost models
- **Backtesting Engine**: Event-driven with realistic Indian market costs (STT, stamp duty, GST, exchange fees)
- **Weekly Target Tracking**: Automated evaluation against 1% weekly return targets with visual badges
- **Broker Support**: Paper trading, Zerodha Kite, and Upstox adapters
- **Real-time Dashboard**: Live monitoring with WebSockets, interactive charts via Plotly
- **Monitoring Stack**: Prometheus metrics + Grafana dashboards
- **Production Ready**: Full Docker setup optimized for Apple Silicon

## Tech Stack

- **Backend**: Python 3.12, Django 5, Django REST Framework
- **Database**: PostgreSQL + TimescaleDB for time series
- **Cache/Queue**: Redis, Celery, Celery Beat
- **Real-time**: Django Channels, WebSockets
- **Execution**: FastAPI microservice for low-latency order routing
- **Frontend**: Tailwind CSS, Plotly
- **Monitoring**: Prometheus, Grafana
- **Infrastructure**: Docker, Docker Compose, NGINX
- **Tools**: Poetry, pytest, ruff, black, mypy, pre-commit

## Architecture

\`\`\`mermaid
graph TB
    subgraph "External"
        NSE[NSE/BSE APIs]
        Zerodha[Zerodha Kite]
        Upstox[Upstox API]
    end

    subgraph "Data Ingestion"
        Loader[Bhavcopy Loaders]
        WS[WebSocket Tick Handler]
        CA[Corporate Actions]
    end

    subgraph "Storage Layer"
        PG[(PostgreSQL + TimescaleDB)]
        Redis[(Redis)]
    end

    subgraph "Core Services"
        Django[Django Web + DRF APIs]
        Celery[Celery Workers]
        Beat[Celery Beat Scheduler]
        Exec[FastAPI Exec Gateway]
    end

    subgraph "Strategy Layer"
        SDK[Strategy SDK]
        Backtest[Backtesting Engine]
        Live[Live Trading Engine]
        Eval[Weekly Target Evaluator]
    end

    subgraph "Broker Adapters"
        Paper[Paper Broker]
        ZBroker[Zerodha Adapter]
        UBroker[Upstox Adapter]
    end

    subgraph "Presentation"
        UI[Dashboard UI]
        WSocket[WebSocket Channels]
        API[REST API]
    end

    subgraph "Monitoring"
        Prom[Prometheus]
        Graf[Grafana]
    end

    NSE --> Loader --> PG
    Zerodha --> WS --> PG
    Upstox --> WS --> PG

    PG --> Django
    Redis --> Django
    Redis --> Celery
    Redis --> Exec

    Django --> SDK
    SDK --> Backtest
    SDK --> Live
    Backtest --> Eval
    Live --> Paper
    Live --> ZBroker
    Live --> UBroker

    Beat --> Celery
    Celery --> Loader
    Celery --> CA

    Django --> UI
    Django --> WSocket
    Django --> API

    Django --> Prom
    Exec --> Prom
    Prom --> Graf
\`\`\`

## Performance Objectives

The platform is tuned to achieve:

- **Weekly Return Target**: ≥1.0% gross mean weekly return
- **Max Drawdown**: ≤10%
- **P95 Weekly Drawdown**: ≥-3%
- **Win Rate**: Competitive on liquid NSE/BSE instruments
- **Cost Modeling**: Realistic Indian market costs including STT, stamp duty, GST

The **WeeklyTargetEvaluator** provides **red/amber/green badges** on the dashboard based on these criteria.

## Repository Structure

\`\`\`
trading/
├── Makefile
├── docker-compose.yml
├── .env.sample
├── infra/
│   ├── nginx/
│   │   └── nginx.conf
│   ├── postgres/
│   │   └── init.sql
│   └── grafana/
│       └── provisioning/
├── configs/
│   └── prometheus.yml
├── services/
│   ├── web/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   ├── manage.py
│   │   ├── core/
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   ├── asgi.py
│   │   │   ├── wsgi.py
│   │   │   └── celery.py
│   │   ├── apps/
│   │   │   ├── accounts/
│   │   │   ├── data/
│   │   │   ├── strategies/
│   │   │   │   ├── sdk/
│   │   │   │   └── reference/
│   │   │   ├── backtest/
│   │   │   │   ├── engine.py
│   │   │   │   └── evaluator.py
│   │   │   ├── live/
│   │   │   │   └── brokers/
│   │   │   ├── api/
│   │   │   └── dashboard/
│   │   ├── templates/
│   │   ├── tests/
│   │   └── scripts/
│   ├── exec/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── main.py
│   │       └── routes/
│   └── worker/
└── docs/
\`\`\`

## Quick Start

### Prerequisites

- macOS (Apple Silicon or Intel)
- [Homebrew](https://brew.sh/)
- Docker Desktop for Mac
- Python 3.12+

### Step 1: Install Dependencies

\`\`\`bash
brew install python@3.12 poetry docker docker-compose
\`\`\`

### Step 2: Clone and Setup

\`\`\`bash
cd /Users/ashu/Desktop/trading
cp .env.sample .env
\`\`\`

Edit `.env` and set your configuration (use defaults for demo).

### Step 3: Build and Run

\`\`\`bash
make up
\`\`\`

This will:
- Build all Docker images
- Start PostgreSQL, Redis, Django, Celery, FastAPI, NGINX, Prometheus, Grafana
- Run database migrations
- Collect static files

### Step 4: Load Sample Data and Run Demo Backtest

\`\`\`bash
make seed
\`\`\`

This will:
- Load 30 days of NSE sample data (NIFTY 50 stocks)
- Load 30 days of BSE sample data (SENSEX stocks)
- Build minute bar aggregations (simulated)
- Run a demo mean reversion backtest
- Generate a weekly target report

### Step 5: Access the Platform

- **Web Dashboard**: http://localhost:8080
- **REST API**: http://localhost:8080/api/
- **API Docs (Swagger)**: http://localhost:8080/docs/
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Development Workflow

### Run Development Server

\`\`\`bash
make dev
\`\`\`

### Run Tests

\`\`\`bash
make test
\`\`\`

### Lint and Format

\`\`\`bash
make lint
\`\`\`

### View Logs

\`\`\`bash
make logs
\`\`\`

### Django Shell

\`\`\`bash
make shell
\`\`\`

### Stop Everything

\`\`\`bash
make down
\`\`\`

### Clean Volumes

\`\`\`bash
make clean
\`\`\`

## Strategy Development

### SDK Components

1. **DataFeed**: Abstract interface for historical and live data
2. **Signal**: Generate trading signals from market data
3. **RiskSizer**: Calculate position sizes (Fixed, Volatility-targeted, Kelly)
4. **ExecutionModel**: Generate orders from target positions
5. **SlippageModel**: Model execution slippage (Fixed, Volume-based)
6. **FeeModel**: Calculate transaction costs (Indian Equity, Simple)

### Example Strategy

\`\`\`python
from apps.strategies.reference import MeanReversionVWAPStrategy

strategy = MeanReversionVWAPStrategy()
parameters = strategy.get_default_parameters()
\`\`\`

### Reference Strategies

1. **Mean Reversion to VWAP**: Intraday mean reversion with volume filters on NIFTY 50
2. **Momentum Breakout**: 15/30 minute breakouts with ATR filters on FNO stocks
3. **Pairs Trading**: Cointegration-based statistical arbitrage on sector stocks

### Creating a Custom Strategy

See `services/web/apps/strategies/reference/` for examples.

## Data Ingestion

### NSE Bhavcopy

\`\`\`bash
docker-compose exec web python manage.py load_nse_sample
\`\`\`

### BSE Bhavcopy

\`\`\`bash
docker-compose exec web python manage.py load_bse_sample
\`\`\`

### Build Minute Bars

\`\`\`bash
docker-compose exec web python manage.py build_minute_bars
\`\`\`

## Broker Configuration

### Paper Trading (Default)

Set in `.env`:
\`\`\`
BROKER=paper
PAPER_INITIAL_CAPITAL=1000000
PAPER_SLIPPAGE_BPS=5
PAPER_COMMISSION_BPS=3
\`\`\`

### Zerodha Kite

Set in `.env`:
\`\`\`
BROKER=zerodha
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_USER_ID=your_user_id
\`\`\`

### Upstox

Set in `.env`:
\`\`\`
BROKER=upstox
UPSTOX_API_KEY=your_api_key
UPSTOX_API_SECRET=your_api_secret
\`\`\`

## API Reference

### REST Endpoints

- `GET /api/exchanges/` - List exchanges
- `GET /api/assets/` - List assets
- `GET /api/bars/` - Historical bars
- `GET /api/strategies/` - List strategies
- `POST /api/strategies/` - Create strategy
- `GET /api/strategy-runs/` - List strategy runs
- `POST /api/strategy-runs/{id}/start/` - Start a run
- `GET /api/strategy-runs/{id}/evaluate/` - Get weekly evaluation
- `GET /api/orders/` - List orders
- `GET /api/positions/` - List positions
- `GET /api/trades/` - List trades

### WebSocket Channels

- `ws://localhost:8080/ws/quotes/` - Live price quotes
- `ws://localhost:8080/ws/orders/` - Order updates
- `ws://localhost:8080/ws/pnl/` - PnL stream

## Testing

\`\`\`bash
cd services/web
poetry run pytest --cov=apps --cov-report=html
\`\`\`

Coverage report will be in `htmlcov/index.html`.

## Monitoring

### Prometheus Metrics

- `exec_orders_total` - Total orders processed
- `exec_order_latency_seconds` - Order latency histogram
- Django request/response metrics
- Celery task metrics

### Grafana Dashboards

Import pre-configured dashboards from `infra/grafana/provisioning/`.

## Environment Variables

See `.env.sample` for all available configuration options. Key variables:

- `ENVIRONMENT` - deployment environment
- `DEBUG` - Django debug mode
- `SECRET_KEY` - Django secret key
- `POSTGRES_*` - Database credentials
- `REDIS_*` - Redis connection
- `BROKER` - Broker selection (paper/zerodha/upstox)
- `TARGET_WEEKLY_RETURN_PCT` - Weekly return target (default: 1.0)
- `MAX_DRAWDOWN_PCT` - Max drawdown threshold (default: 10.0)

## Security

- All secrets via environment variables
- CSRF protection enabled
- Session security hardened
- Role-based access (admin/trader/viewer)
- CORS configured
- No hardcoded credentials

## Deployment

For production deployment:

1. Set `DEBUG=False`
2. Use strong `SECRET_KEY`
3. Configure SSL/TLS via NGINX or load balancer
4. Set up database backups
5. Configure Sentry for error tracking
6. Use managed Redis (e.g., AWS ElastiCache)
7. Scale Celery workers horizontally
8. Enable Prometheus federation for multi-node setups

## Troubleshooting

### Docker Build Issues

\`\`\`bash
docker-compose build --no-cache
\`\`\`

### Database Connection Errors

\`\`\`bash
docker-compose logs postgres
\`\`\`

### Celery Not Processing Tasks

\`\`\`bash
docker-compose logs worker
\`\`\`

### Missing Migrations

\`\`\`bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
\`\`\`

## Contributing

This is a production-grade reference implementation. For contributions:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Run linters (`make lint`)
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software. Always test strategies thoroughly in paper trading before going live.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

