"""
Start paper trading session with simulated live market data.
This allows backtesting strategies in real-time with realistic market conditions.
"""
import time
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.data.models import Asset, Bar
from apps.live.brokers.paper import PaperBroker
from apps.live.models import Order, Position
from apps.strategies.models import Strategy, StrategyRun


class Command(BaseCommand):
    help = "Start paper trading with simulated live market data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--strategy",
            type=str,
            default="mean_reversion",
            help="Strategy to use (momentum/mean_reversion)",
        )
        parser.add_argument(
            "--capital", type=float, default=1000000, help="Initial capital in INR"
        )
        parser.add_argument(
            "--symbols",
            type=str,
            default="RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK",
            help="Comma-separated list of symbols to trade",
        )
        parser.add_argument(
            "--interval", type=int, default=5, help="Update interval in seconds"
        )
        parser.add_argument(
            "--duration", type=int, default=60, help="Trading duration in minutes"
        )

    def handle(self, *args, **options):
        strategy_type = options["strategy"]
        initial_capital = Decimal(str(options["capital"]))
        symbols = [s.strip() for s in options["symbols"].split(",")]
        interval = options["interval"]
        duration_minutes = options["duration"]

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*80}\nPAPER TRADING SESSION\n{'='*80}"
            )
        )
        self.stdout.write(f"Strategy: {strategy_type}")
        self.stdout.write(f"Initial Capital: ₹{initial_capital:,.0f}")
        self.stdout.write(f"Symbols: {', '.join(symbols)}")
        self.stdout.write(f"Update Interval: {interval}s")
        self.stdout.write(f"Duration: {duration_minutes} minutes")
        self.stdout.write(f"{'='*80}\n")

        # Get or create strategy
        strategy, created = Strategy.objects.get_or_create(
            name=f"{strategy_type.replace('_', ' ').title()} Paper",
            defaults={
                "description": f"Paper trading session for {strategy_type}",
                "is_active": True,
                "parameters": self._get_strategy_params(strategy_type),
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created strategy: {strategy.name}"))

        # Create strategy run
        strategy_run = StrategyRun.objects.create(
            strategy=strategy,
            run_type="paper",
            status="running",
            start_date=timezone.now().date(),
            started_at=timezone.now(),
            parameters={
                "initial_capital": float(initial_capital),
                "symbols": symbols,
                "interval": interval,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(f"Created strategy run ID: {strategy_run.id}")
        )

        # Initialize paper broker
        broker = PaperBroker(
            initial_capital=float(initial_capital),
            slippage_bps=5,
            commission_bps=3,
        )

        # Get assets
        assets = {
            symbol: Asset.objects.filter(symbol=symbol, is_active=True).first()
            for symbol in symbols
        }
        assets = {k: v for k, v in assets.items() if v is not None}

        if not assets:
            self.stdout.write(
                self.style.ERROR(
                    f"No assets found for symbols: {symbols}. Please load sample data first with 'make seed'"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"\nFound {len(assets)} assets: {', '.join(assets.keys())}")
        )
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("STARTING LIVE SIMULATION...")
        self.stdout.write(f"{'='*80}\n")

        # Main trading loop
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        tick_count = 0

        try:
            while datetime.now() < end_time:
                tick_count += 1
                current_time = timezone.now()

                self.stdout.write(
                    f"\n[Tick {tick_count}] {current_time.strftime('%H:%M:%S')}"
                )

                # Get latest prices for each asset (simulate live data)
                market_data = {}
                for symbol, asset in assets.items():
                    # Get recent bar
                    recent_bar = (
                        Bar.objects.filter(asset=asset).order_by("-timestamp").first()
                    )

                    if recent_bar:
                        # Simulate price movement (+/- 0.5%)
                        import random

                        price_change = random.uniform(-0.005, 0.005)
                        current_price = float(recent_bar.close) * (1 + price_change)

                        market_data[symbol] = {
                            "price": current_price,
                            "high": current_price * 1.002,
                            "low": current_price * 0.998,
                            "volume": random.randint(1000, 10000),
                        }

                        self.stdout.write(
                            f"  {symbol:12s} ₹{current_price:10.2f} ({price_change*100:+.2f}%)"
                        )

                # Generate signals using simple strategy logic
                signals = self._generate_signals(
                    strategy_type, market_data, broker.positions
                )

                # Execute signals
                for signal in signals:
                    symbol = signal["symbol"]
                    side = signal["side"]  # BUY or SELL
                    quantity = signal["quantity"]
                    price = market_data[symbol]["price"]

                    # Create order
                    order = Order.objects.create(
                        strategy_run=strategy_run,
                        asset=assets[symbol],
                        order_type="MARKET",
                        side=side,
                        quantity=quantity,
                        price=Decimal(str(price)),
                        status="pending",
                    )

                    # Execute with broker
                    execution = broker.place_order(
                        symbol=symbol,
                        side=side.lower(),
                        quantity=quantity,
                        price=price,
                    )

                    if execution:
                        order.status = "filled"
                        order.filled_quantity = quantity
                        order.average_price = Decimal(str(execution["price"]))
                        order.save()

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ {side} {quantity} {symbol} @ ₹{execution['price']:.2f}"
                            )
                        )

                # Update broker with current prices (for MTM)
                broker.update_positions(market_data)

                # Display portfolio summary
                self._display_portfolio(broker, tick_count)

                # Wait for next tick
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n\nTrading interrupted by user"))

        finally:
            # Close all positions
            self.stdout.write(f"\n\n{'='*80}")
            self.stdout.write("CLOSING ALL POSITIONS...")
            self.stdout.write(f"{'='*80}\n")

            for symbol, position in broker.positions.items():
                if position["quantity"] != 0:
                    side = "SELL" if position["quantity"] > 0 else "BUY"
                    quantity = abs(position["quantity"])
                    price = market_data.get(symbol, {}).get("price", position["avg_price"])

                    broker.place_order(
                        symbol=symbol, side=side.lower(), quantity=quantity, price=price
                    )

                    self.stdout.write(
                        self.style.SUCCESS(f"  Closed position: {symbol}")
                    )

            # Update strategy run
            strategy_run.status = "completed"
            strategy_run.completed_at = timezone.now()
            strategy_run.result = {
                "final_capital": broker.cash + broker.get_portfolio_value(market_data),
                "total_pnl": broker.realized_pnl + broker.unrealized_pnl,
                "realized_pnl": broker.realized_pnl,
                "unrealized_pnl": broker.unrealized_pnl,
                "total_trades": len(broker.trade_history),
                "total_commission": broker.total_commission,
            }
            strategy_run.save()

            # Final summary
            self._display_final_summary(broker, strategy_run, initial_capital)

    def _get_strategy_params(self, strategy_type):
        if strategy_type == "momentum":
            return {
                "fast_period": 15,
                "slow_period": 30,
                "volume_sma_period": 20,
                "volume_multiplier": 2.0,
                "atr_period": 14,
                "atr_multiplier": 1.5,
            }
        else:  # mean_reversion
            return {
                "lookback_periods": 20,
                "entry_std": 2.0,
                "exit_std": 0.5,
                "volume_filter_multiplier": 1.5,
            }

    def _generate_signals(self, strategy_type, market_data, current_positions):
        """Simple signal generation logic for demonstration"""
        import random

        signals = []

        for symbol, data in market_data.items():
            # Simple random walk strategy for demonstration
            # In production, this would use the actual strategy logic
            if random.random() > 0.8:  # 20% chance of signal
                current_qty = current_positions.get(symbol, {}).get("quantity", 0)

                if current_qty == 0:  # No position - enter
                    side = "BUY" if random.random() > 0.5 else "SELL"
                    quantity = random.randint(10, 50)
                    signals.append(
                        {"symbol": symbol, "side": side, "quantity": quantity}
                    )
                elif abs(current_qty) >= 10:  # Has position - maybe exit
                    if random.random() > 0.7:  # 30% chance to exit
                        side = "SELL" if current_qty > 0 else "BUY"
                        quantity = abs(current_qty)
                        signals.append(
                            {"symbol": symbol, "side": side, "quantity": quantity}
                        )

        return signals

    def _display_portfolio(self, broker, tick_count):
        """Display current portfolio status"""
        if tick_count % 5 == 0:  # Display every 5 ticks
            self.stdout.write(f"\n  Portfolio Status:")
            self.stdout.write(f"    Cash: ₹{broker.cash:,.2f}")
            self.stdout.write(f"    Realized P&L: ₹{broker.realized_pnl:,.2f}")
            self.stdout.write(f"    Unrealized P&L: ₹{broker.unrealized_pnl:,.2f}")
            self.stdout.write(f"    Total Trades: {len(broker.trade_history)}")

            if broker.positions:
                self.stdout.write(f"\n  Open Positions:")
                for symbol, pos in broker.positions.items():
                    if pos["quantity"] != 0:
                        self.stdout.write(
                            f"    {symbol:12s} Qty: {pos['quantity']:4.0f} Avg: ₹{pos['avg_price']:.2f}"
                        )

    def _display_final_summary(self, broker, strategy_run, initial_capital):
        """Display final trading session summary"""
        final_value = broker.cash
        total_pnl = broker.realized_pnl
        total_return = (total_pnl / float(initial_capital)) * 100

        self.stdout.write(f"\n\n{'='*80}")
        self.stdout.write("FINAL SUMMARY")
        self.stdout.write(f"{'='*80}")
        self.stdout.write(f"\nStrategy Run ID: {strategy_run.id}")
        self.stdout.write(f"Initial Capital: ₹{initial_capital:,.2f}")
        self.stdout.write(f"Final Capital: ₹{final_value:,.2f}")
        self.stdout.write(f"Total P&L: ₹{total_pnl:,.2f}")
        self.stdout.write(f"Total Return: {total_return:+.2f}%")
        self.stdout.write(f"\nTotal Trades: {len(broker.trade_history)}")
        self.stdout.write(f"Total Commission: ₹{broker.total_commission:,.2f}")

        if broker.trade_history:
            winning_trades = sum(1 for t in broker.trade_history if t["pnl"] > 0)
            win_rate = (winning_trades / len(broker.trade_history)) * 100
            self.stdout.write(f"Win Rate: {win_rate:.1f}%")

        self.stdout.write(f"\n{'='*80}\n")
        self.stdout.write(
            self.style.SUCCESS(
                f"\nPaper trading session completed successfully!\nRun ID: {strategy_run.id}"
            )
        )
