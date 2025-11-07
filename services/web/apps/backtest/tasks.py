from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.backtest.engine import BacktestEngine
from apps.backtest.evaluator import WeeklyTargetEvaluator
from apps.data.models import Asset
from apps.strategies.models import StrategyRun
from apps.strategies.sdk import FeeModel, SlippageModel
from apps.strategies.sdk.fees import IndianEquityFeeModel
from apps.strategies.sdk.slippage import FixedSlippageModel


@shared_task(queue="backtest")
def run_backtest(strategy_run_id: int):
    try:
        strategy_run = StrategyRun.objects.get(id=strategy_run_id)
        strategy_run.status = "running"
        strategy_run.started_at = datetime.now()
        strategy_run.save()

        universe_symbols = strategy_run.strategy.universe
        universe = Asset.objects.filter(symbol__in=universe_symbols)

        slippage_model = FixedSlippageModel(
            slippage_bps=settings.PAPER_SLIPPAGE_BPS
        )
        fee_model = IndianEquityFeeModel(brokerage_bps=settings.PAPER_COMMISSION_BPS)

        engine = BacktestEngine(
            strategy_run=strategy_run,
            initial_capital=settings.PAPER_INITIAL_CAPITAL,
            slippage_model=slippage_model,
            fee_model=fee_model,
        )

        def simple_callback(timestamp, bars_dict, positions):
            signals = []
            return signals

        engine.run(
            universe=list(universe),
            start_date=strategy_run.start_date,
            end_date=strategy_run.end_date or timezone.now().date(),
            on_bar_callback=simple_callback,
        )

        evaluator = WeeklyTargetEvaluator()
        result = evaluator.evaluate(strategy_run)

        strategy_run.status = "completed"
        strategy_run.completed_at = timezone.now()
        strategy_run.result = result
        strategy_run.save()

        return {"strategy_run_id": strategy_run_id, "status": "completed", "result": result}

    except Exception as e:
        strategy_run.status = "failed"
        strategy_run.error_message = str(e)
        strategy_run.completed_at = timezone.now()
        strategy_run.save()

        return {"strategy_run_id": strategy_run_id, "status": "failed", "error": str(e)}
