# Trading Platform Architecture

## Overview

This document describes the architecture of the production-grade algorithmic trading platform.

## System Components

### 1. Data Layer

**PostgreSQL + TimescaleDB**
- Stores all time-series data (bars, ticks)
- Manages reference data (assets, exchanges, corporate actions)
- Handles transactional data (orders, trades, positions)
- TimescaleDB extension for time-series optimization

**Redis**
- Session storage
- Celery message broker
- Cache layer
- Real-time data pub/sub

### 2. Application Layer

**Django Web Service**
- REST API via Django REST Framework
- Django admin interface
- Template-based dashboard
- WebSocket server via Django Channels
- Background task coordination

**Celery Workers**
- Data ingestion tasks
- Backtest execution
- Report generation
- Scheduled jobs via Celery Beat

**FastAPI Execution Gateway**
- Low-latency order routing
- Broker adapter management
- Real-time quote handling
- Metrics collection

### 3. Strategy Framework

**SDK Components**
- DataFeed: Historical and live data access
- Signal: Trading signal generation
- RiskSizer: Position sizing algorithms
- ExecutionModel: Order generation
- SlippageModel: Execution slippage simulation
- FeeModel: Transaction cost calculation

### 4. Broker Integration

**Paper Broker**
- Simulated exchange matching
- Order book simulation
- Position tracking
- PnL calculation

**Zerodha Kite Adapter**
- Order placement and management
- Quote streaming
- Position synchronization
- Account management

**Upstox Adapter**
- Order placement and management
- Quote streaming
- Position synchronization

### 5. Monitoring & Observability

**Prometheus**
- Metrics collection
- Time-series database
- Alerting rules

**Grafana**
- Dashboard visualization
- Real-time monitoring
- Historical analysis

**Structured Logging**
- JSON log format
- Centralized log aggregation
- Request/response tracking

### 6. Infrastructure

**NGINX**
- Reverse proxy
- Load balancing
- Static file serving
- WebSocket proxying

**Docker**
- Containerization
- Service isolation
- Resource management
- Apple Silicon optimization

## Data Flow

### Backtesting Flow

1. User creates strategy and strategy run
2. Celery task triggered
3. Historical data loaded from PostgreSQL
4. Backtesting engine simulates trading
5. Metrics calculated and stored
6. Weekly evaluation performed
7. Results displayed in dashboard

### Live Trading Flow

1. Strategy run started in live/paper mode
2. Broker connection established
3. Market data streamed via WebSocket
4. Signals generated in real-time
5. Orders submitted to FastAPI gateway
6. Gateway routes to broker adapter
7. Executions reported back
8. Positions and PnL updated
9. Metrics pushed to Prometheus
10. Dashboard updated via WebSocket

## Security Architecture

- Environment-based configuration
- No hardcoded credentials
- Role-based access control
- CSRF protection
- Session security
- CORS configuration
- API authentication

## Scalability Considerations

- Horizontal scaling of Celery workers
- Database read replicas
- Redis clustering
- Connection pooling
- Async I/O for real-time data
- Efficient database indexing

## Performance Optimizations

- TimescaleDB for time-series queries
- Redis caching
- Database query optimization
- Celery task queues
- WebSocket for real-time updates
- Compiled numba functions for calculations
