from django.shortcuts import get_object_or_404, render

from apps.backtest.evaluator import WeeklyTargetEvaluator
from apps.backtest.models import BacktestMetrics, EquityCurve
from apps.strategies.models import Strategy, StrategyRun


def overview(request):
    recent_runs = StrategyRun.objects.all().order_by("-created_at")[:10]

    context = {
        "recent_runs": recent_runs,
        "title": "Overview",
    }
    return render(request, "dashboard/index.html", context)


def strategies_list(request):
    strategies = Strategy.objects.all()

    context = {
        "strategies": strategies,
        "title": "Strategies",
    }
    return render(request, "dashboard/strategies_list.html", context)


def strategy_detail(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk)
    runs = strategy.runs.all().order_by("-created_at")

    context = {
        "strategy": strategy,
        "runs": runs,
        "title": f"Strategy: {strategy.name}",
    }
    return render(request, "dashboard/strategy_detail.html", context)


def backtest_results(request, run_id):
    strategy_run = get_object_or_404(StrategyRun, pk=run_id)

    try:
        metrics = BacktestMetrics.objects.get(strategy_run=strategy_run)
    except BacktestMetrics.DoesNotExist:
        metrics = None

    equity_curve = EquityCurve.objects.filter(strategy_run=strategy_run).order_by("timestamp")

    evaluator = WeeklyTargetEvaluator()
    evaluation = evaluator.evaluate(strategy_run)

    context = {
        "strategy_run": strategy_run,
        "metrics": metrics,
        "equity_curve": list(equity_curve),
        "evaluation": evaluation,
        "title": f"Backtest: {strategy_run.strategy.name}",
    }
    return render(request, "dashboard/backtest_results.html", context)


def live_monitor(request):
    live_runs = StrategyRun.objects.filter(run_type__in=["live", "paper"], status="running")

    context = {
        "live_runs": live_runs,
        "title": "Live Monitor",
    }
    return render(request, "dashboard/live_monitor.html", context)


def data_browser(request):
    from apps.data.models import Asset

    assets = Asset.objects.filter(is_active=True)[:100]

    context = {
        "assets": assets,
        "title": "Data Browser",
    }
    return render(request, "dashboard/data_browser.html", context)
