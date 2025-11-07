from django.core.management.base import BaseCommand

from apps.backtest.evaluator import WeeklyTargetEvaluator
from apps.strategies.models import StrategyRun


class Command(BaseCommand):
    help = "Generate weekly target report for completed backtests"

    def handle(self, *args, **options):
        recent_runs = StrategyRun.objects.filter(
            run_type="backtest", status="completed"
        ).order_by("-completed_at")[:5]

        if not recent_runs.exists():
            self.stdout.write(self.style.WARNING("No completed backtests found"))
            return

        evaluator = WeeklyTargetEvaluator()

        self.stdout.write("=" * 80)
        self.stdout.write("WEEKLY TARGET REPORT")
        self.stdout.write("=" * 80)

        for run in recent_runs:
            result = evaluator.evaluate(run)

            self.stdout.write(f"\nStrategy: {run.strategy.name}")
            self.stdout.write(f"Run ID: {run.id}")
            self.stdout.write(f"Period: {run.start_date} to {run.end_date}")
            self.stdout.write("-" * 80)

            badge_color = {
                "green": self.style.SUCCESS,
                "amber": self.style.WARNING,
                "red": self.style.ERROR,
            }[result["badge"]]

            self.stdout.write(badge_color(f"BADGE: {result['badge'].upper()}"))
            self.stdout.write(f"Mean Weekly Return: {result['mean_weekly_return']:.2%}")
            self.stdout.write(f"Median Weekly Return: {result['median_weekly_return']:.2%}")
            self.stdout.write(f"Max Drawdown: {result['max_drawdown']:.2%}")
            self.stdout.write(f"Win Rate: {result['win_rate']:.2%}")
            self.stdout.write(f"Payoff Ratio: {result['payoff_ratio']:.2f}")
            self.stdout.write(f"Total Weeks: {result['total_weeks']}")

            self.stdout.write("\nTarget Criteria:")
            self.stdout.write(
                f"  Return Target (≥{result['target_weekly_return']:.2%}): {'✓' if result['meets_return_target'] else '✗'}"
            )
            self.stdout.write(
                f"  Drawdown Target: {'✓' if result['meets_drawdown_target'] else '✗'}"
            )
            self.stdout.write(
                f"  P95 Target: {'✓' if result['meets_p95_target'] else '✗'}"
            )

        self.stdout.write("\n" + "=" * 80)
