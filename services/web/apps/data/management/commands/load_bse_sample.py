from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.data.loaders import BSEBhavcopyLoader


class Command(BaseCommand):
    help = "Load BSE sample data for last 30 trading days"

    def handle(self, *args, **options):
        loader = BSEBhavcopyLoader()

        end_date = date.today()
        start_date = end_date - timedelta(days=45)

        total_bars = 0
        trading_days = 0

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:
                self.stdout.write(f"Loading BSE data for {current_date}...")
                bars_created = loader.load_date(current_date)
                total_bars += bars_created
                trading_days += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Created {bars_created} bars for {current_date}")
                )

            current_date += timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded {total_bars} bars across {trading_days} trading days"
            )
        )
