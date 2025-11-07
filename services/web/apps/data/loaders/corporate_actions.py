from datetime import date
from typing import List

from django.db import transaction

from apps.data.models import Asset, CorporateAction


class CorporateActionsLoader:
    def load_actions(self, actions: List[dict]) -> int:
        created_count = 0

        with transaction.atomic():
            for action_data in actions:
                try:
                    asset = Asset.objects.get(
                        symbol=action_data["symbol"],
                        exchange__code=action_data.get("exchange", "NSE"),
                    )

                    CorporateAction.objects.update_or_create(
                        asset=asset,
                        action_type=action_data["action_type"],
                        ex_date=action_data["ex_date"],
                        defaults={
                            "record_date": action_data.get("record_date"),
                            "payment_date": action_data.get("payment_date"),
                            "ratio": action_data.get("ratio"),
                            "amount": action_data.get("amount"),
                            "details": action_data.get("details", {}),
                        },
                    )
                    created_count += 1

                except Asset.DoesNotExist:
                    continue

        return created_count

    def adjust_bars_for_splits(self, asset: Asset, split_date: date, ratio: float):
        from apps.data.models import Bar

        bars = Bar.objects.filter(asset=asset, timestamp__lt=split_date)

        with transaction.atomic():
            for bar in bars:
                bar.open = bar.open / ratio
                bar.high = bar.high / ratio
                bar.low = bar.low / ratio
                bar.close = bar.close / ratio
                bar.volume = int(bar.volume * ratio)
                bar.save()
