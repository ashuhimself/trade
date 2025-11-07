from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.data.models import Asset
from apps.strategies.models import Strategy, StrategyRun


class Command(BaseCommand):
    help = "Run demo backtest on NSE sample data"

    def handle(self, *args, **options):
        self.stdout.write("Creating demo strategy...")

        strategy, created = Strategy.objects.get_or_create(
            name="Mean Reversion Demo",
            defaults={
                "description": "Demo mean reversion strategy on NIFTY 50 constituents",
                "class_path": "apps.strategies.reference.MeanReversionVWAPStrategy",
                "parameters": {
                    "lookback_periods": 20,
                    "entry_std": 2.0,
                    "exit_std": 0.5,
                },
                "universe": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR"],
                "is_active": True,
            },
        )

        self.stdout.write(f"Strategy: {strategy.name}")

        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        strategy_run = StrategyRun.objects.create(
            strategy=strategy,
            run_type="backtest",
            status="pending",
            start_date=start_date,
            end_date=end_date,
            parameters=strategy.parameters,
        )

        self.stdout.write(f"Created strategy run: {strategy_run.id}")

        from apps.backtest.tasks import run_backtest

        self.stdout.write("Running backtest...")
        result = run_backtest(strategy_run.id)

        if result["status"] == "completed":
            self.stdout.write(self.style.SUCCESS(f"Backtest completed successfully"))
            self.stdout.write(f"Weekly Target Badge: {result['result']['badge']}")
            self.stdout.write(
                f"Mean Weekly Return: {result['result']['mean_weekly_return']:.2%}"
            )
            self.stdout.write(f"Max Drawdown: {result['result']['max_drawdown']:.2%}")
        else:
            self.stdout.write(self.style.ERROR(f"Backtest failed: {result.get('error')}"))
