from django.core.management.base import BaseCommand

from apps.data.models import Asset


class Command(BaseCommand):
    help = "Build minute bars from tick data (placeholder)"

    def handle(self, *args, **options):
        assets = Asset.objects.filter(is_active=True)[:10]

        self.stdout.write(f"Building minute bars for {assets.count()} assets...")

        for asset in assets:
            self.stdout.write(f"  Processing {asset.symbol}...")

        self.stdout.write(self.style.SUCCESS("Minute bars building complete (simulated)"))
