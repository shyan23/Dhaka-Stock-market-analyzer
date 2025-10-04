"""
Unit tests for configuration management in the Stock Market Analyzer
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from config import Config


class TestConfig:
    """Test cases for the Config class"""
    
    def test_init(self):
        """Test Config initialization"""
        config = Config()
        
        # Check that config properties exist
        assert hasattr(config, 'REDIS_HOST')
        assert hasattr(config, 'REDIS_PORT')
        assert hasattr(config, 'REDIS_PASSWORD')
        assert hasattr(config, 'APP_MODE')
        assert hasattr(config, 'DSE_BASE_URL')
        assert hasattr(config, 'DSE_API_ENDPOINTS')
        
    def test_redis_config_from_env_vars(self):
        """Test Redis configuration from environment variables"""
        with patch.dict(os.environ, {
            'REDIS_HOST': 'test_host',
            'REDIS_PORT': '1234',
            'REDIS_PASSWORD': 'test_password'
        }):
            config = Config()
            
            assert config.REDIS_HOST == 'test_host'
            assert config.REDIS_PORT == 1234
            assert config.REDIS_PASSWORD == 'test_password'

    def test_redis_config_defaults(self):
        """Test Redis configuration with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            # Check default values
            assert config.REDIS_HOST == 'localhost'
            assert config.REDIS_PORT == 6379
            assert config.REDIS_PASSWORD == ''

    def test_redis_config_from_st_streamlit_secrets(self):
        """Test Redis configuration from Streamlit secrets"""
        # Mock Streamlit secrets
        mock_st = Mock()
        mock_st.secrets = {
            "redis": {
                "host": "st_host",
                "port": 5678,
                "password": "st_password"
            }
        }
        
        with patch('config.st', mock_st):
            config = Config()
            
            assert config.REDIS_HOST == 'st_host'
            assert config.REDIS_PORT == 5678
            assert config.REDIS_PASSWORD == 'st_password'

    def test_redis_config_from_st_streamlit_secrets_url(self):
        """Test Redis configuration from Streamlit secrets with URL format"""
        # Mock Streamlit secrets with URL format
        mock_st = Mock()
        mock_st.secrets = {
            "redis": {
                "url": "redis://:password@redis-host:6380"
            }
        }
        
        with patch('config.st', mock_st):
            config = Config()
            
            assert config.REDIS_HOST == 'redis-host'
            assert config.REDIS_PORT == 6380
            assert config.REDIS_PASSWORD == 'password'

    def test_stock_data_config(self):
        """Test stock data configuration"""
        config = Config()
        
        assert hasattr(config, 'YAHOO_FINANCE_ENABLED')
        assert hasattr(config, 'UPDATE_INTERVAL_MINUTES')
        
        # Check default values
        assert isinstance(config.YAHOO_FINANCE_ENABLED, bool)
        assert isinstance(config.UPDATE_INTERVAL_MINUTES, int)

    def test_app_config(self):
        """Test app configuration"""
        config = Config()
        
        assert hasattr(config, 'APP_MODE')
        # APP_MODE should be either 'google_sheets' or 'redis'
        assert config.APP_MODE in ['google_sheets', 'redis']

    def test_sheet_names_config(self):
        """Test Google Sheets configuration"""
        config = Config()
        
        assert hasattr(config, 'MAIN_SHEET')
        assert hasattr(config, 'HISTORICAL_SHEET')
        assert hasattr(config, 'TRANSACTIONS_SHEET')
        assert hasattr(config, 'PORTFOLIO_SHEET')
        assert hasattr(config, 'PORTFOLIO_HISTORY_SHEET')
        
        # Check that sheet names are strings
        assert isinstance(config.MAIN_SHEET, str)
        assert isinstance(config.HISTORICAL_SHEET, str)
        assert isinstance(config.TRANSACTIONS_SHEET, str)
        assert isinstance(config.PORTFOLIO_SHEET, str)
        assert isinstance(config.PORTFOLIO_HISTORY_SHEET, str)

    def test_dse_api_config(self):
        """Test DSE API configuration"""
        config = Config()
        
        assert hasattr(config, 'DSE_BASE_URL')
        assert hasattr(config, 'DSE_API_ENDPOINTS')
        
        # Check that base URL is a string starting with https
        assert isinstance(config.DSE_BASE_URL, str)
        assert config.DSE_BASE_URL.startswith('https')
        
        # Check that endpoints is a dictionary
        assert isinstance(config.DSE_API_ENDPOINTS, dict)
        assert 'quotes_txt' in config.DSE_API_ENDPOINTS
        assert 'company_details' in config.DSE_API_ENDPOINTS
        assert 'top_20_shares' in config.DSE_API_ENDPOINTS
        assert 'historical_archive' in config.DSE_API_ENDPOINTS
        assert 'latest_by_ltp' in config.DSE_API_ENDPOINTS
        assert 'latest_by_change' in config.DSE_API_ENDPOINTS
        assert 'latest_by_value' in config.DSE_API_ENDPOINTS
        assert 'suggest_list' in config.DSE_API_ENDPOINTS

    @patch('config.load_dotenv')
    def test_config_reloads_env_vars(self, mock_load_dotenv):
        """Test that config reloads environment variables on initialization"""
        config = Config()
        
        # Check that load_dotenv was called with override=True
        mock_load_dotenv.assert_called_once_with(override=True)

    def test_config_values_with_env_vars(self):
        """Test config values with environment variables set"""
        # Set some environment variables
        with patch.dict(os.environ, {
            'APP_MODE': 'redis',
            'REDIS_HOST': 'custom_host',
            'REDIS_PORT': '9999',
            'YAHOO_FINANCE_ENABLED': 'false',
            'UPDATE_INTERVAL_MINUTES': '10'
        }):
            config = Config()
            
            assert config.APP_MODE == 'redis'
            assert config.REDIS_HOST == 'custom_host'
            assert config.REDIS_PORT == 9999
            assert config.YAHOO_FINANCE_ENABLED is False
            assert config.UPDATE_INTERVAL_MINUTES == 10

    def test_config_values_with_env_vars_true(self):
        """Test config values with environment variables set to true"""
        # Set environment variables to true values
        with patch.dict(os.environ, {
            'YAHOO_FINANCE_ENABLED': 'true',
            'UPDATE_INTERVAL_MINUTES': '5'
        }):
            config = Config()
            
            assert config.YAHOO_FINANCE_ENABLED is True
            assert config.UPDATE_INTERVAL_MINUTES == 5

    @patch('config.st')
    def test_redis_config_fallback_on_error(self, mock_st):
        """Test that Redis config falls back to environment variables if secrets fail"""
        # Make secrets access raise an exception
        mock_st.__dict__ = {}
        type(mock_st).secrets = property(lambda self: (_ for _ in ()).throw(Exception("Secrets error")))
        
        with patch.dict(os.environ, {
            'REDIS_HOST': 'fallback_host',
            'REDIS_PORT': '5555',
            'REDIS_PASSWORD': 'fallback_password'
        }):
            config = Config()
            
            assert config.REDIS_HOST == 'fallback_host'
            assert config.REDIS_PORT == 5555
            assert config.REDIS_PASSWORD == 'fallback_password'

    @patch('config.st')
    def test_redis_config_fallback_to_defaults(self, mock_st):
        """Test that Redis config falls back to defaults if both secrets and env vars fail"""
        # Make secrets access raise an exception and clear environment
        mock_st.__dict__ = {}
        type(mock_st).secrets = property(lambda self: (_ for _ in ()).throw(Exception("Secrets error")))
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            assert config.REDIS_HOST == 'localhost'
            assert config.REDIS_PORT == 6379
            assert config.REDIS_PASSWORD == ''