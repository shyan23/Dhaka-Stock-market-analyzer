"""
Unit tests for data models in the Stock Market Analyzer
"""
import pytest
from datetime import datetime
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import Transaction, TransactionType, PortfolioItem, PortfolioSnapshot


class TestStockModel:
    """Test cases for the Stock model"""
    
    def test_stock_creation(self):
        """Test creating a basic Stock instance"""
        stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=295.0,
            volume=1000000
        )
        
        assert stock.symbol == "GP"
        assert stock.name == "Grameenphone Ltd"
        assert stock.current_price == 300.0
        assert stock.previous_close == 295.0
        assert stock.volume == 1000000

    def test_stock_price_change(self):
        """Test the price_change property"""
        stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=295.0,
            volume=1000000
        )
        
        assert stock.price_change == 5.0

    def test_stock_price_change_percent(self):
        """Test the price_change_percent property"""
        stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=295.0,
            volume=1000000
        )
        
        expected_change = (5.0 / 295.0) * 100
        assert abs(stock.price_change_percent - expected_change) < 0.01

    def test_stock_price_change_percent_zero_division(self):
        """Test price_change_percent when previous_close is 0"""
        stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=0.0,
            volume=1000000
        )
        
        assert stock.price_change_percent == 0.0

    def test_stock_to_dict(self):
        """Test converting Stock to dictionary"""
        stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=295.0,
            volume=1000000,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        data = stock.to_dict()
        
        assert data["symbol"] == "GP"
        assert data["name"] == "Grameenphone Ltd"
        assert data["current_price"] == 300.0
        assert data["previous_close"] == 295.0
        assert data["volume"] == 1000000
        assert data["last_updated"] == "2023-01-01T12:00:00"

    def test_stock_from_dict(self):
        """Test creating Stock from dictionary"""
        data = {
            "symbol": "GP",
            "name": "Grameenphone Ltd",
            "current_price": 300.0,
            "previous_close": 295.0,
            "volume": 1000000,
            "last_updated": "2023-01-01T12:00:00"
        }
        
        stock = Stock.from_dict(data)
        
        assert stock.symbol == "GP"
        assert stock.name == "Grameenphone Ltd"
        assert stock.current_price == 300.0
        assert stock.previous_close == 295.0
        assert stock.volume == 1000000
        assert stock.last_updated == datetime(2023, 1, 1, 12, 0, 0)


class TestStockPriceHistoryModel:
    """Test cases for the StockPriceHistory model"""
    
    def test_stock_price_history_creation(self):
        """Test creating a StockPriceHistory instance"""
        history = StockPriceHistory(
            symbol="GP",
            date=datetime(2023, 1, 1),
            open_price=290.0,
            high=305.0,
            low=288.0,
            close_price=300.0,
            volume=1500000
        )
        
        assert history.symbol == "GP"
        assert history.date == datetime(2023, 1, 1)
        assert history.open_price == 290.0
        assert history.high == 305.0
        assert history.low == 288.0
        assert history.close_price == 300.0
        assert history.volume == 1500000

    def test_stock_price_history_to_dict(self):
        """Test converting StockPriceHistory to dictionary"""
        history = StockPriceHistory(
            symbol="GP",
            date=datetime(2023, 1, 1),
            open_price=290.0,
            high=305.0,
            low=288.0,
            close_price=300.0,
            volume=1500000
        )
        
        data = history.to_dict()
        
        assert data["symbol"] == "GP"
        assert data["date"] == "2023-01-01T00:00:00"
        assert data["open_price"] == 290.0
        assert data["high"] == 305.0
        assert data["low"] == 288.0
        assert data["close_price"] == 300.0
        assert data["volume"] == 1500000

    def test_stock_price_history_from_dict(self):
        """Test creating StockPriceHistory from dictionary"""
        data = {
            "symbol": "GP",
            "date": "2023-01-01T00:00:00",
            "open_price": 290.0,
            "high": 305.0,
            "low": 288.0,
            "close_price": 300.0,
            "volume": 1500000
        }
        
        history = StockPriceHistory.from_dict(data)
        
        assert history.symbol == "GP"
        assert history.date == datetime(2023, 1, 1)
        assert history.open_price == 290.0
        assert history.high == 305.0
        assert history.low == 288.0
        assert history.close_price == 300.0
        assert history.volume == 1500000


class TestTransactionModel:
    """Test cases for the Transaction model"""
    
    def test_transaction_creation(self):
        """Test creating a Transaction instance"""
        from datetime import datetime
        
        transaction = Transaction(
            id="test-123",
            symbol="GP",
            transaction_type=TransactionType.BUY,
            quantity=100,
            price=300.0,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            notes="Test transaction"
        )
        
        assert transaction.id == "test-123"
        assert transaction.symbol == "GP"
        assert transaction.transaction_type == TransactionType.BUY
        assert transaction.quantity == 100
        assert transaction.price == 300.0
        assert transaction.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert transaction.notes == "Test transaction"

    def test_transaction_total_amount(self):
        """Test the total_amount property"""
        from datetime import datetime
        
        transaction = Transaction(
            id="test-123",
            symbol="GP",
            transaction_type=TransactionType.BUY,
            quantity=100,
            price=300.0,
            timestamp=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert transaction.total_amount == 30000.0

    def test_transaction_to_dict(self):
        """Test converting Transaction to dictionary"""
        from datetime import datetime
        
        transaction = Transaction(
            id="test-123",
            symbol="GP",
            transaction_type=TransactionType.BUY,
            quantity=100,
            price=300.0,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            notes="Test transaction"
        )
        
        data = transaction.to_dict()
        
        assert data["id"] == "test-123"
        assert data["symbol"] == "GP"
        assert data["transaction_type"] == "BUY"
        assert data["quantity"] == 100
        assert data["price"] == 300.0
        assert data["timestamp"] == "2023-01-01T12:00:00"
        assert data["notes"] == "Test transaction"

    def test_transaction_from_dict(self):
        """Test creating Transaction from dictionary"""
        from datetime import datetime
        
        data = {
            "id": "test-123",
            "symbol": "GP",
            "transaction_type": "BUY",
            "quantity": 100,
            "price": 300.0,
            "timestamp": "2023-01-01T12:00:00",
            "notes": "Test transaction"
        }
        
        transaction = Transaction.from_dict(data)
        
        assert transaction.id == "test-123"
        assert transaction.symbol == "GP"
        assert transaction.transaction_type == TransactionType.BUY
        assert transaction.quantity == 100
        assert transaction.price == 300.0
        assert transaction.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert transaction.notes == "Test transaction"


class TestPortfolioItemModel:
    """Test cases for the PortfolioItem model"""
    
    def test_portfolio_item_creation(self):
        """Test creating a PortfolioItem instance"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert item.symbol == "GP"
        assert item.quantity == 100
        assert item.average_cost == 300.0
        assert item.current_price == 310.0
        assert item.last_updated == datetime(2023, 1, 1, 12, 0, 0)

    def test_portfolio_item_total_cost(self):
        """Test the total_cost property"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert item.total_cost == 30000.0

    def test_portfolio_item_current_value(self):
        """Test the current_value property"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert item.current_value == 31000.0

    def test_portfolio_item_gain_loss(self):
        """Test the gain_loss property"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert item.gain_loss == 1000.0

    def test_portfolio_item_gain_loss_percent(self):
        """Test the gain_loss_percent property"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert item.gain_loss_percent == pytest.approx(3.33, rel=0.01)

    def test_portfolio_item_gain_loss_percent_zero_division(self):
        """Test gain_loss_percent when total_cost is 0"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=0.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        assert item.gain_loss_percent == 0.0

    def test_portfolio_item_to_dict(self):
        """Test converting PortfolioItem to dictionary"""
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        data = item.to_dict()
        
        assert data["symbol"] == "GP"
        assert data["quantity"] == 100
        assert data["average_cost"] == 300.0
        assert data["current_price"] == 310.0
        assert data["last_updated"] == "2023-01-01T12:00:00"

    def test_portfolio_item_from_dict(self):
        """Test creating PortfolioItem from dictionary"""
        from datetime import datetime
        
        data = {
            "symbol": "GP",
            "quantity": 100,
            "average_cost": 300.0,
            "current_price": 310.0,
            "last_updated": "2023-01-01T12:00:00"
        }
        
        item = PortfolioItem.from_dict(data)
        
        assert item.symbol == "GP"
        assert item.quantity == 100
        assert item.average_cost == 300.0
        assert item.current_price == 310.0
        assert item.last_updated == datetime(2023, 1, 1, 12, 0, 0)


class TestPortfolioSnapshotModel:
    """Test cases for the PortfolioSnapshot model"""
    
    def test_portfolio_snapshot_creation(self):
        """Test creating a PortfolioSnapshot instance"""
        from datetime import datetime
        from src.models.portfolio import PortfolioItem
        
        items = [
            PortfolioItem(
                symbol="GP",
                quantity=100,
                average_cost=300.0,
                current_price=310.0,
                last_updated=datetime(2023, 1, 1)
            )
        ]
        
        snapshot = PortfolioSnapshot(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            total_value=31000.0,
            total_cost=30000.0,
            total_gain_loss=1000.0,
            total_gain_loss_percent=3.33,
            items=items
        )
        
        assert snapshot.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert snapshot.total_value == 31000.0
        assert snapshot.total_cost == 30000.0
        assert snapshot.total_gain_loss == 1000.0
        assert snapshot.total_gain_loss_percent == 3.33
        assert len(snapshot.items) == 1
        assert snapshot.items[0].symbol == "GP"

    def test_portfolio_snapshot_gain_loss(self):
        """Test the gain_loss property"""
        from datetime import datetime
        from src.models.portfolio import PortfolioItem
        
        items = [
            PortfolioItem(
                symbol="GP",
                quantity=100,
                average_cost=300.0,
                current_price=310.0,
                last_updated=datetime(2023, 1, 1)
            )
        ]
        
        snapshot = PortfolioSnapshot(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            total_value=31000.0,
            total_cost=30000.0,
            total_gain_loss=1000.0,
            total_gain_loss_percent=3.33,
            items=items
        )
        
        # The gain_loss property should be the same as total_gain_loss
        assert snapshot.gain_loss == 1000.0

    def test_portfolio_snapshot_to_dict(self):
        """Test converting PortfolioSnapshot to dictionary"""
        from datetime import datetime
        from src.models.portfolio import PortfolioItem
        
        items = [
            PortfolioItem(
                symbol="GP",
                quantity=100,
                average_cost=300.0,
                current_price=310.0,
                last_updated=datetime(2023, 1, 1)
            )
        ]
        
        snapshot = PortfolioSnapshot(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            total_value=31000.0,
            total_cost=30000.0,
            total_gain_loss=1000.0,
            total_gain_loss_percent=3.33,
            items=items
        )
        
        data = snapshot.to_dict()
        
        assert data["timestamp"] == "2023-01-01T12:00:00"
        assert data["total_value"] == 31000.0
        assert data["total_cost"] == 30000.0
        assert data["total_gain_loss"] == 1000.0
        assert data["total_gain_loss_percent"] == 3.33
        assert len(data["items"]) == 1
        assert data["items"][0]["symbol"] == "GP"

    def test_portfolio_snapshot_from_dict(self):
        """Test creating PortfolioSnapshot from dictionary"""
        from datetime import datetime
        
        data = {
            "timestamp": "2023-01-01T12:00:00",
            "total_value": 31000.0,
            "total_cost": 30000.0,
            "total_gain_loss": 1000.0,
            "total_gain_loss_percent": 3.33,
            "items": [
                {
                    "symbol": "GP",
                    "quantity": 100,
                    "average_cost": 300.0,
                    "current_price": 310.0,
                    "last_updated": "2023-01-01T00:00:00"
                }
            ]
        }
        
        snapshot = PortfolioSnapshot.from_dict(data)
        
        assert snapshot.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert snapshot.total_value == 31000.0
        assert snapshot.total_cost == 30000.0
        assert snapshot.total_gain_loss == 1000.0
        assert snapshot.total_gain_loss_percent == 3.33
        assert len(snapshot.items) == 1
        assert snapshot.items[0].symbol == "GP"
        assert snapshot.items[0].quantity == 100