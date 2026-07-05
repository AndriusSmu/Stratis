"""Currency conversion service."""

from typing import Dict
from ..models.enums import Currency


class CurrencyService:
    """Service for currency conversion and formatting."""
    
    CONVERSION_RATES: Dict[Currency, float] = {
        Currency.USD: 1.0,
        Currency.EUR: 1.08,
        Currency.GBP: 1.27,
    }
    
    CURRENCY_SYMBOLS: Dict[Currency, str] = {
        Currency.USD: "$",
        Currency.EUR: "€",
        Currency.GBP: "£",
    }
    
    @classmethod
    def to_usd(cls, amount: float, currency: Currency) -> float:
        rate = cls.CONVERSION_RATES.get(currency, 1.0)
        return round(amount * rate, 2)
    
    @classmethod
    def get_symbol(cls, currency: Currency) -> str:
        return cls.CURRENCY_SYMBOLS.get(currency, currency.value)
