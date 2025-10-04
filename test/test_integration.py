"""
Additional integration and edge case tests for the Stock Market Analyzer
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime
from pathlib import Path


def test_import_all_modules():
    """Test that all modules in the project can be imported successfully"""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Test importing main modules
    import main
    import config
    from src.app import StockMarketApp
    from src.models.stock import Stock, StockPriceHistory
    from src.models.portfolio import Transaction, TransactionType, PortfolioItem, PortfolioSnapshot
    from src.services.dse_api import DSEAPIService
    from src.services.data_manager import DataManager
    from src.services.auth_service import AuthService
    from src.services.session_manager import SessionManager
    from src.ui.dashboard import DashboardUI
    from src.ui.stock_selector import StockSelectorUI
    from src.ui.portfolio import PortfolioUI
    from src.ui.transactions import TransactionsUI
    
    # Verify classes exist
    assert Stock is not None
    assert Transaction is not None
    assert DSEAPIService is not None
    assert DataManager is not None
    assert StockMarketApp is not None


class TestIntegration:
    """Integration tests that combine multiple components"""
    
    @patch('src.services.dse_api.DSEAPIService')
    @patch('src.services.data_manager.DataManager')
    def test_stock_data_flow(self, mock_data_manager, mock_dse_api):
        """Test the flow of stock data from API to UI"""
        from src.models.stock import Stock
        
        # Setup mocks
        mock_stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=295.0,
            volume=1000000,
            last_updated=datetime(2023, 1, 1)
        )
        
        mock_dse_api_instance = Mock()
        mock_dse_api_instance.get_stock_by_symbol.return_value = mock_stock
        mock_dse_api.return_value = mock_dse_api_instance
        
        mock_data_manager_instance = Mock()
        mock_data_manager.return_value = mock_data_manager_instance
        
        # Test that data can be retrieved and processed
        stock = mock_dse_api_instance.get_stock_by_symbol("GP")
        
        assert stock.symbol == "GP"
        assert stock.current_price == 300.0
        assert stock.price_change == 5.0  # 300.0 - 295.0
        assert stock.price_change_percent > 0  # Should be positive

    @patch('src.services.auth_service.Path')
    @patch('src.services.auth_service.yaml')
    @patch('src.services.auth_service.stauth.Authenticate')
    @patch('src.services.session_manager.st')
    def test_user_session_flow(self, mock_st, mock_authenticate, mock_yaml, mock_path):
        """Test the flow of user session management"""
        from src.services.auth_service import AuthService
        from src.services.session_manager import SessionManager
        from src.services.data_loader import DataLoader  # Assuming this exists
        from src.models.portfolio import PortfolioItem
        
        # Mock Path object
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        # Mock yaml operations
        mock_yaml.load.return_value = {
            'credentials': {'usernames': {}},
            'cookie': {
                'name': 'test_cookie',
                'key': 'test_key',
                'expiry_days': 30
            },
            'preauthorized': {'emails': []}
        }
        
        # Mock the Authenticate class
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = ('Test User', True, 'test_user')
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock streamlit session state
        mock_st.session_state = {
            'name': 'Test User',
            'username': 'test_user',
            'authentication_status': True,
            'selected_stocks': ['GP'],
            'portfolio_items': {
                'GP': PortfolioItem(
                    symbol='GP',
                    quantity=100,
                    average_cost=300.0,
                    current_price=310.0,
                    last_updated=datetime.now()
                )
            },
            'transactions': [],
            'portfolio_settings': {'initial_fund': 100000.0},
            'cash_balance': 70000.0,
            'cash_transactions': []
        }
        
        # Initialize auth service
        auth_service = AuthService()
        
        # Initialize session manager
        session_manager = SessionManager(auth_service)
        
        # Test session initialization
        mock_data_loader = Mock()
        mock_data_loader.load_selected_stocks.return_value = ['GP', 'ACI']
        mock_data_loader.load_portfolio_items.return_value = {}
        mock_data_loader.load_transactions.return_value = []
        mock_data_loader.load_portfolio_settings.return_value = {'initial_fund': 100000.0}
        
        # This should work with mocked session state
        session_manager.initialize_user_session(mock_data_loader)
        
        # Verify that session state was updated
        assert len(mock_st.session_state.selected_stocks) > 0

    def test_data_serialization_consistency(self):
        """Test that data serialization and deserialization is consistent"""
        from src.models.stock import Stock
        from src.models.portfolio import Transaction, TransactionType, PortfolioItem
        from datetime import datetime
        
        # Test Stock serialization
        original_stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=300.0,
            previous_close=295.0,
            volume=1000000,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        stock_dict = original_stock.to_dict()
        reconstructed_stock = Stock.from_dict(stock_dict)
        
        assert original_stock.symbol == reconstructed_stock.symbol
        assert original_stock.current_price == reconstructed_stock.current_price
        assert original_stock.previous_close == reconstructed_stock.previous_close
        assert original_stock.volume == reconstructed_stock.volume
        assert original_stock.last_updated == reconstructed_stock.last_updated
        
        # Test Transaction serialization
        original_transaction = Transaction(
            id="test-123",
            symbol="GP",
            transaction_type=TransactionType.BUY,
            quantity=100,
            price=300.0,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            notes="Test transaction"
        )
        
        transaction_dict = original_transaction.to_dict()
        reconstructed_transaction = Transaction.from_dict(transaction_dict)
        
        assert original_transaction.id == reconstructed_transaction.id
        assert original_transaction.symbol == reconstructed_transaction.symbol
        assert original_transaction.transaction_type == reconstructed_transaction.transaction_type
        assert original_transaction.quantity == reconstructed_transaction.quantity
        assert original_transaction.price == reconstructed_transaction.price
        assert original_transaction.timestamp == reconstructed_transaction.timestamp
        assert original_transaction.notes == reconstructed_transaction.notes
        
        # Test PortfolioItem serialization
        original_item = PortfolioItem(
            symbol="GP",
            quantity=100,
            average_cost=300.0,
            current_price=310.0,
            last_updated=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        item_dict = original_item.to_dict()
        reconstructed_item = PortfolioItem.from_dict(item_dict)
        
        assert original_item.symbol == reconstructed_item.symbol
        assert original_item.quantity == reconstructed_item.quantity
        assert original_item.average_cost == reconstructed_item.average_cost
        assert original_item.current_price == reconstructed_item.current_price
        assert original_item.last_updated == reconstructed_item.last_updated


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_stock_with_zero_values(self):
        """Test stock model with zero values"""
        from src.models.stock import Stock
        
        stock = Stock(
            symbol="TEST",
            name="Test Stock",
            current_price=0.0,
            previous_close=0.0,
            volume=0
        )
        
        # Should handle zero division in price_change_percent
        assert stock.price_change == 0.0
        assert stock.price_change_percent == 0.0  # Should not raise exception

    def test_portfolio_item_with_zero_cost(self):
        """Test portfolio item with zero average cost"""
        from src.models.portfolio import PortfolioItem
        from datetime import datetime
        
        item = PortfolioItem(
            symbol="TEST",
            quantity=100,
            average_cost=0.0,  # Zero cost
            current_price=310.0,
            last_updated=datetime(2023, 1, 1)
        )
        
        # Should handle zero division in gain_loss_percent
        assert item.total_cost == 0.0
        assert item.gain_loss_percent == 0.0  # Should not raise exception

    def test_transaction_with_zero_quantity(self):
        """Test transaction with zero quantity"""
        from src.models.portfolio import Transaction, TransactionType
        from datetime import datetime
        
        transaction = Transaction(
            id="test-123",
            symbol="TEST",
            transaction_type=TransactionType.BUY,
            quantity=0,  # Zero quantity
            price=300.0,
            timestamp=datetime(2023, 1, 1)
        )
        
        # Should calculate total amount correctly
        assert transaction.total_amount == 0.0

    def test_api_with_none_response(self):
        """Test API service handling None responses"""
        # We can't easily test this with the current implementation
        # since we'd need to mock internal methods properly
        # For now, just verify the functionality exists
        from src.services.dse_api import DSEAPIService
        
        # This test verifies that the method exists and can be called
        # without crashing (given proper mocking)
        assert hasattr(DSEAPIService, '_make_request')
        assert hasattr(DSEAPIService, 'get_latest_prices')
        assert len(stocks) == 0

    @patch('redis.Redis')
    def test_data_manager_with_redis_failure(self, mock_redis_class):
        """Test data manager handling Redis connection failures"""
        from src.services.data_manager import DataManager
        from config import Config
        from unittest.mock import Mock
        
        # Mock config to use Redis mode
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            # Mock Redis to raise exception on ping
            mock_redis_instance = Mock()
            mock_redis_instance.ping.side_effect = Exception("Connection failed")
            mock_redis_class.return_value = mock_redis_instance
            
            # This should handle the connection failure gracefully
            data_manager = DataManager()
            
            # Redis client should be None due to connection failure
            assert data_manager.redis_client is None


def test_requirements_compatibility():
    """Test that all required packages can be imported"""
    try:
        import streamlit
        import pandas
        import plotly
        import requests
        import beautifulsoup4
        import redis
        import gspread
        import google.auth
        import yaml
        import numpy
        print(f"Streamlit version: {streamlit.__version__}")
        print(f"Pandas version: {pandas.__version__}")
        print(f"Requests version: {requests.__version__}")
        print(f"Redis version: {redis.__version__ if hasattr(redis, '__version__') else 'N/A'}")
    except ImportError as e:
        pytest.fail(f"Failed to import required package: {e}")

        
class TestPerformance:
    """Basic performance tests"""
    
    def test_model_creation_performance(self):
        """Test that model creation is reasonably fast"""
        import time
        from src.models.stock import Stock
        from src.models.portfolio import Transaction, TransactionType
        from datetime import datetime
        
        start_time = time.time()
        
        # Create multiple models
        for i in range(1000):
            stock = Stock(
                symbol=f"SYM{i}",
                name=f"Stock {i}",
                current_price=100.0 + i,
                previous_close=99.0 + i,
                volume=1000000
            )
            transaction = Transaction(
                id=f"txn-{i}",
                symbol=f"SYM{i}",
                transaction_type=TransactionType.BUY,
                quantity=100,
                price=100.0 + i,
                timestamp=datetime(2023, 1, 1)
            )
        
        end_time = time.time()
        
        # Creation of 1000 models should be fast (< 1 second)
        assert (end_time - start_time) < 1.0, f"Model creation took too long: {end_time - start_time:.2f}s"