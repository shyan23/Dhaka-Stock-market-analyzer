import os
import sys
import pytest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules that will be commonly used in tests
from config import Config
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import Transaction, TransactionType, PortfolioItem, PortfolioSnapshot


@pytest.fixture
def config():
    """Fixture to provide a Config instance"""
    return Config()


@pytest.fixture
def sample_stock():
    """Fixture to provide a sample Stock instance"""
    return Stock(
        symbol="GP",
        name="Grameenphone Ltd",
        current_price=100.0,
        previous_close=95.0,
        volume=1000000,
        high=102.0,
        low=98.0,
        open_price=99.0
    )


@pytest.fixture
def sample_transaction():
    """Fixture to provide a sample Transaction instance"""
    from datetime import datetime
    return Transaction(
        id="test-123",
        symbol="GP",
        transaction_type=TransactionType.BUY,
        quantity=100,
        price=100.0,
        timestamp=datetime.now(),
        notes="Test transaction"
    )


@pytest.fixture
def sample_portfolio_item():
    """Fixture to provide a sample PortfolioItem instance"""
    from datetime import datetime
    return PortfolioItem(
        symbol="GP",
        quantity=100,
        average_cost=100.0,
        current_price=105.0,
        last_updated=datetime.now()
    )


@pytest.fixture
def mock_dse_api():
    """Fixture to provide a mock DSE API service"""
    with patch('src.services.dse_api.DSEAPIService') as mock:
        yield mock


@pytest.fixture
def mock_data_manager():
    """Fixture to provide a mock Data Manager"""
    with patch('src.services.data_manager.DataManager') as mock:
        yield mock


@pytest.fixture
def temp_data_dir():
    """Fixture to provide a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)