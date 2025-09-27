from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Transaction:
    id: str
    symbol: str
    transaction_type: TransactionType
    quantity: int
    price: float
    timestamp: datetime
    notes: Optional[str] = None
    
    @property
    def total_amount(self) -> float:
        return self.quantity * self.price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'transaction_type': self.transaction_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            id=data['id'],
            symbol=data['symbol'],
            transaction_type=TransactionType(data['transaction_type']),
            quantity=data['quantity'],
            price=data['price'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            notes=data.get('notes')
        )

@dataclass
class PortfolioItem:
    symbol: str
    quantity: int
    average_cost: float
    current_price: float
    last_updated: datetime
    
    @property
    def total_cost(self) -> float:
        return self.quantity * self.average_cost
    
    @property
    def current_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def gain_loss(self) -> float:
        return self.current_value - self.total_cost
    
    @property
    def gain_loss_percent(self) -> float:
        if self.total_cost == 0:
            return 0.0
        return (self.gain_loss / self.total_cost) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'average_cost': self.average_cost,
            'current_price': self.current_price,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PortfolioItem':
        return cls(
            symbol=data['symbol'],
            quantity=data['quantity'],
            average_cost=data['average_cost'],
            current_price=data['current_price'],
            last_updated=datetime.fromisoformat(data['last_updated'])
        )

@dataclass
class PortfolioSnapshot:
    timestamp: datetime
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float
    items: List[PortfolioItem]
    
    @property
    def gain_loss(self) -> float:
        return self.total_value - self.total_cost
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_value': self.total_value,
            'total_cost': self.total_cost,
            'total_gain_loss': self.total_gain_loss,
            'total_gain_loss_percent': self.total_gain_loss_percent,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PortfolioSnapshot':
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            total_value=data['total_value'],
            total_cost=data['total_cost'],
            total_gain_loss=data['total_gain_loss'],
            total_gain_loss_percent=data['total_gain_loss_percent'],
            items=[PortfolioItem.from_dict(item) for item in data['items']]
        )


