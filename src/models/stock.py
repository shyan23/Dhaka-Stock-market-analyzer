from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Stock:
    symbol: str
    name: str
    current_price: float
    previous_close: float
    volume: int
    market_cap: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open_price: Optional[float] = None
    last_updated: Optional[datetime] = None
    
    @property
    def price_change(self) -> float:
        return self.current_price - self.previous_close
    
    @property
    def price_change_percent(self) -> float:
        if self.previous_close == 0:
            return 0.0
        return (self.price_change / self.previous_close) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price,
            'previous_close': self.previous_close,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'high': self.high,
            'low': self.low,
            'open_price': self.open_price,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stock':
        return cls(
            symbol=data['symbol'],
            name=data['name'],
            current_price=data['current_price'],
            previous_close=data['previous_close'],
            volume=data['volume'],
            market_cap=data.get('market_cap'),
            high=data.get('high'),
            low=data.get('low'),
            open_price=data.get('open_price'),
            last_updated=datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else None
        )

@dataclass
class StockPriceHistory:
    symbol: str
    date: datetime
    open_price: float
    high: float
    low: float
    close_price: float
    volume: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'open_price': self.open_price,
            'high': self.high,
            'low': self.low,
            'close_price': self.close_price,
            'volume': self.volume
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockPriceHistory':
        return cls(
            symbol=data['symbol'],
            date=datetime.fromisoformat(data['date']),
            open_price=data['open_price'],
            high=data['high'],
            low=data['low'],
            close_price=data['close_price'],
            volume=data['volume']
        )


