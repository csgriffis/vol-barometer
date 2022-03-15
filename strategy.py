from typing import TypedDict, Literal, List

vol_level_literal = Literal['minimum', 'moderate', 'average', 'elevated', 'extreme']


class VolSymbols(TypedDict):
    """
    VolSymbols defines a dict of volatility levels to trade-able symbols
    """
    minimum: str
    moderate: str
    average: str
    elevated: str
    extreme: str


class WeightedStrategy(TypedDict):
    """
    Strategy defines a portfolio weight and VolSymbols dict for a single strategy
    """
    weight: float
    symbols: VolSymbols


class Strategy:
    def __init__(self, s: WeightedStrategy):
        self.strategy = s

    def get_symbol(self, vol_level: vol_level_literal) -> str:
        return self.strategy['symbols'][vol_level]

    def get_symbol_list(self) -> List[str]:
        return [self.strategy['symbols'][k] for k in self.strategy['symbols']]
