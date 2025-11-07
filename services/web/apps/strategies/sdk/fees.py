from abc import ABC, abstractmethod
from decimal import Decimal


class FeeModel(ABC):
    @abstractmethod
    def calculate(self, price: float, quantity: int, side: str) -> float:
        pass


class IndianEquityFeeModel(FeeModel):
    def __init__(
        self,
        brokerage_bps: float = 3.0,
        stt_bps: float = 10.0,
        transaction_charge_bps: float = 0.345,
        sebi_charge_bps: float = 0.0001,
        stamp_duty_bps: float = 1.5,
        gst_pct: float = 18.0,
    ):
        self.brokerage_bps = brokerage_bps
        self.stt_bps = stt_bps
        self.transaction_charge_bps = transaction_charge_bps
        self.sebi_charge_bps = sebi_charge_bps
        self.stamp_duty_bps = stamp_duty_bps
        self.gst_pct = gst_pct

    def calculate(self, price: float, quantity: int, side: str) -> float:
        turnover = price * quantity

        brokerage = turnover * (self.brokerage_bps / 10000.0)

        stt = 0.0
        if side == "sell":
            stt = turnover * (self.stt_bps / 10000.0)

        transaction_charge = turnover * (self.transaction_charge_bps / 10000.0)
        sebi_charge = turnover * (self.sebi_charge_bps / 10000.0)

        stamp_duty = 0.0
        if side == "buy":
            stamp_duty = turnover * (self.stamp_duty_bps / 10000.0)

        taxable = brokerage + transaction_charge + sebi_charge
        gst = taxable * (self.gst_pct / 100.0)

        total_fees = brokerage + stt + transaction_charge + sebi_charge + stamp_duty + gst

        return round(total_fees, 2)


class SimpleFeeModel(FeeModel):
    def __init__(self, commission_bps: float = 5.0):
        self.commission_bps = commission_bps

    def calculate(self, price: float, quantity: int, side: str) -> float:
        turnover = price * quantity
        commission = turnover * (self.commission_bps / 10000.0)
        return round(commission, 2)
