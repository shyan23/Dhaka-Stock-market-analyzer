"""
Unit tests for Data Manager service in the Stock Market Analyzer
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from src.services.data_manager import DataManager
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import Transaction, TransactionType, PortfolioItem, PortfolioSnapshot


class TestDataManager:
    """Test cases for the Data Manager service"""
    
    def test_init_redis_mode(self):
        """Test Data Manager initialization in Redis mode"""
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            with patch('redis.Redis') as mock_redis:
                mock_redis_instance = Mock()
                mock_redis_instance.ping.return_value = True
                mock_redis.return_value = mock_redis_instance
                
                data_manager = DataManager()
                
                assert data_manager.app_mode == 'redis'
                assert data_manager.redis_client is not None

    def test_init_sheets_mode(self):
        """Test Data Manager initialization in Google Sheets mode"""
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'google_sheets'
            mock_config.return_value = mock_config_instance
            
            with patch('src.services.google_sheets.GoogleSheetsService') as mock_sheets:
                mock_sheets_instance = Mock()
                mock_sheets_instance.is_connected.return_value = True
                mock_sheets.return_value = mock_sheets_instance
                
                data_manager = DataManager()
                
                assert data_manager.app_mode == 'google_sheets'
                assert data_manager.sheets_service is not None

    @patch('redis.Redis')
    def test_redis_methods(self, mock_redis_class):
        """Test Redis-related methods"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            # Test saving and retrieving stock data
            stock = Stock(
                symbol="GP",
                name="Grameenphone Ltd",
                current_price=300.0,
                previous_close=295.0,
                volume=1000000,
                last_updated=datetime(2023, 1, 1)
            )
            
            # Save stock
            result = data_manager._save_stock_to_redis(stock)
            mock_redis_instance.set.assert_called_once()
            assert result == mock_redis_instance.set.return_value
            
            # Test getting stock
            mock_redis_instance.get.return_value = json.dumps(stock.to_dict())
            retrieved_stock = data_manager._get_stock_from_redis("GP")
            assert retrieved_stock.symbol == "GP"
            assert retrieved_stock.current_price == 300.0

    @patch('redis.Redis')
    def test_save_stock_data_redis(self, mock_redis_class):
        """Test saving stock data in Redis mode"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            stock = Stock(
                symbol="GP",
                name="Grameenphone Ltd",
                current_price=300.0,
                previous_close=295.0,
                volume=1000000
            )
            
            result = data_manager.save_stock_data(stock)
            
            # Should call Redis set method
            assert mock_redis_instance.set.called
            assert result is True

    def test_save_stock_data_sheets(self):
        """Test saving stock data in Google Sheets mode"""
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'google_sheets'
            mock_config.return_value = mock_config_instance
            
            with patch('src.services.google_sheets.GoogleSheetsService') as mock_sheets:
                mock_sheets_instance = Mock()
                mock_sheets_instance.is_connected.return_value = True
                mock_sheets_instance.save_stock_data.return_value = True
                mock_sheets.return_value = mock_sheets_instance
                
                data_manager = DataManager()
                
                stock = Stock(
                    symbol="GP",
                    name="Grameenphone Ltd",
                    current_price=300.0,
                    previous_close=295.0,
                    volume=1000000
                )
                
                result = data_manager.save_stock_data(stock)
                
                assert mock_sheets_instance.save_stock_data.called
                assert result is True

    @patch('redis.Redis')
    def test_save_transaction_redis(self, mock_redis_class):
        """Test saving transaction in Redis mode"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            transaction = Transaction(
                id="test-123",
                symbol="GP",
                transaction_type=TransactionType.BUY,
                quantity=100,
                price=300.0,
                timestamp=datetime(2023, 1, 1)
            )
            
            result = data_manager.save_transaction(transaction)
            
            # Should call Redis set method
            assert mock_redis_instance.set.called
            assert result is True

    @patch('redis.Redis')
    def test_get_transactions_redis(self, mock_redis_class):
        """Test getting transactions from Redis"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.keys.return_value = ["transaction:test-123"]
        mock_redis_instance.get.return_value = json.dumps({
            'id': 'test-123',
            'symbol': 'GP',
            'transaction_type': 'BUY',
            'quantity': 100,
            'price': 300.0,
            'timestamp': '2023-01-01T00:00:00'
        })
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            transactions = data_manager.get_transactions()
            
            # Should call Redis keys and get methods
            assert mock_redis_instance.keys.called
            assert mock_redis_instance.get.called
            assert isinstance(transactions, list)

    @patch('redis.Redis')
    def test_save_historical_data_redis(self, mock_redis_class):
        """Test saving historical data in Redis mode"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            history = [
                StockPriceHistory(
                    symbol="GP",
                    date=datetime(2023, 1, 1),
                    open_price=290.0,
                    high=300.0,
                    low=288.0,
                    close_price=295.0,
                    volume=1000000
                )
            ]
            
            result = data_manager.save_historical_data("GP", history)
            
            # Should call Redis set method
            assert mock_redis_instance.set.called
            assert result is True

    @patch('redis.Redis')
    def test_get_historical_data_redis(self, mock_redis_class):
        """Test getting historical data from Redis"""
        history_data = [
            StockPriceHistory(
                symbol="GP",
                date=datetime(2023, 1, 1),
                open_price=290.0,
                high=300.0,
                low=288.0,
                close_price=295.0,
                volume=1000000
            )
        ]
        
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = json.dumps([item.to_dict() for item in history_data])
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            history = data_manager.get_historical_data("GP")
            
            # Should call Redis get method
            assert mock_redis_instance.get.called
            assert isinstance(history, list)
            if history:
                assert history[0].symbol == "GP"

    @patch('redis.Redis')
    def test_save_portfolio_snapshot_redis(self, mock_redis_class):
        """Test saving portfolio snapshot in Redis mode"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            snapshot = PortfolioSnapshot(
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                total_value=31000.0,
                total_cost=30000.0,
                total_gain_loss=1000.0,
                total_gain_loss_percent=3.33,
                items=[]
            )
            
            result = data_manager.save_portfolio_snapshot(snapshot)
            
            # Should call Redis set method
            assert mock_redis_instance.set.called
            assert result is True

    @patch('redis.Redis')
    def test_user_specific_methods_redis(self, mock_redis_class):
        """Test user-specific data management methods in Redis mode"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = json.dumps(["GP", "ACI"])
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            # Mock session manager with a test user
            mock_session_manager = Mock()
            mock_session_manager.get_user_prefix.return_value = "user_test_"
            
            data_manager = DataManager(session_manager=mock_session_manager)
            
            # Test loading user selected stocks
            stocks = data_manager.load_user_selected_stocks()
            
            # Should call Redis get method with user prefix
            mock_redis_instance.get.assert_called_with("user_test_selected_stocks")
            assert isinstance(stocks, list)

    @patch('redis.Redis')
    def test_save_user_portfolio_items(self, mock_redis_class):
        """Test saving user's portfolio items to Redis"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            # Mock session manager with a test user
            mock_session_manager = Mock()
            mock_session_manager.get_user_prefix.return_value = "user_test_"
            
            data_manager = DataManager(session_manager=mock_session_manager)
            
            portfolio_items = {
                "GP": PortfolioItem(
                    symbol="GP",
                    quantity=100,
                    average_cost=300.0,
                    current_price=310.0,
                    last_updated=datetime(2023, 1, 1)
                )
            }
            
            result = data_manager.save_user_portfolio_items(portfolio_items)
            
            # Should call Redis set method with user prefix
            mock_redis_instance.set.assert_called_with(
                "user_test_portfolio_items",
                json.dumps({symbol: item.to_dict() for symbol, item in portfolio_items.items()})
            )
            assert result is True

    @patch('redis.Redis')
    def test_load_user_portfolio_items(self, mock_redis_class):
        """Test loading user's portfolio items from Redis"""
        portfolio_data = {
            "GP": {
                "symbol": "GP",
                "quantity": 100,
                "average_cost": 300.0,
                "current_price": 310.0,
                "last_updated": "2023-01-01T00:00:00"
            }
        }
        
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = json.dumps(portfolio_data)
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            # Mock session manager with a test user
            mock_session_manager = Mock()
            mock_session_manager.get_user_prefix.return_value = "user_test_"
            
            data_manager = DataManager(session_manager=mock_session_manager)
            
            portfolio_items = data_manager.load_user_portfolio_items()
            
            # Should call Redis get method with user prefix
            mock_redis_instance.get.assert_called_with("user_test_portfolio_items")
            assert isinstance(portfolio_items, dict)
            if portfolio_items:
                assert "GP" in portfolio_items
                assert portfolio_items["GP"].symbol == "GP"

    @patch('redis.Redis')
    def test_reset_user_transactions_redis(self, mock_redis_class):
        """Test resetting user transactions in Redis mode"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            # Mock session manager with a test user
            mock_session_manager = Mock()
            mock_session_manager.get_user_prefix.return_value = "user_test_"
            
            data_manager = DataManager(session_manager=mock_session_manager)
            
            result = data_manager.reset_user_transactions()
            
            # Should call Redis delete methods with user prefix
            assert mock_redis_instance.delete.called
            assert result is True

    def test_test_redis_connection_not_redis_mode(self):
        """Test Redis connection test in non-Redis mode"""
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'google_sheets'
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            result = data_manager.test_redis_connection()
            
            assert result['connected'] is False
            assert 'Not in Redis mode' in result['error']

    @patch('redis.Redis')
    def test_test_redis_connection_success(self, mock_redis_class):
        """Test Redis connection test in Redis mode with successful connection"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.set.return_value = True
        mock_redis_instance.get.return_value = "Redis is working!"
        mock_redis_class.return_value = mock_redis_instance
        
        with patch('config.Config') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.APP_MODE = 'redis'
            mock_config_instance.REDIS_HOST = 'localhost'
            mock_config_instance.REDIS_PORT = 6379
            mock_config_instance.REDIS_PASSWORD = None
            mock_config.return_value = mock_config_instance
            
            data_manager = DataManager()
            
            result = data_manager.test_redis_connection()
            
            assert result['connected'] is True
            assert result['test_result'] == "Redis is working!"
            assert result['config']['host'] == 'localhost'