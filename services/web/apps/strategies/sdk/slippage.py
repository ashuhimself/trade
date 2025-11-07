from abc import ABC, abstractmethod


class SlippageModel(ABC):
    @abstractmethod
    def apply(self, price: float, quantity: int, side: str, volume: int = 0) -> float:
        pass


class FixedSlippageModel(SlippageModel):
    def __init__(self, slippage_bps: float = 5.0):
        self.slippage_bps = slippage_bps

    def apply(self, price: float, quantity: int, side: str, volume: int = 0) -> float:
        slippage_factor = self.slippage_bps / 10000.0
        if side == "buy":
            return price * (1 + slippage_factor)
        else:
            return price * (1 - slippage_factor)


class VolumeSlippageModel(SlippageModel):
    def __init__(self, base_bps: float = 2.0, volume_impact_factor: float = 0.1):
        self.base_bps = base_bps
        self.volume_impact_factor = volume_impact_factor

    def apply(self, price: float, quantity: int, side: str, volume: int = 0) -> float:
        base_slippage = self.base_bps / 10000.0

        volume_impact = 0.0
        if volume > 0:
            participation_rate = quantity / volume
            volume_impact = self.volume_impact_factor * participation_rate

        total_slippage = base_slippage + volume_impact

        if side == "buy":
            return price * (1 + total_slippage)
        else:
            return price * (1 - total_slippage)
