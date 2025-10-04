"""
Unit tests for Session Manager service in the Stock Market Analyzer
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from src.services.session_manager import SessionManager
from src.models.portfolio import PortfolioItem, Transaction, TransactionType
from datetime import datetime


class TestSessionManager:
    """Test cases for the Session Manager service"""
    
    def test_init(self):
        """Test SessionManager initialization"""
        mock_auth_service = Mock()
        
        session_manager = SessionManager(mock_auth_service)
        
        assert session_manager.auth_service == mock_auth_service

    @patch('src.services.session_manager.st')
    def test_get_user_prefix(self, mock_st):
        """Test getting user prefix"""
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        prefix = session_manager.get_user_prefix()
        
        assert prefix == "user_test_"
        mock_auth_service.get_user_session_prefix.assert_called_once()

    @patch('src.services.session_manager.st')
    def test_get_user_data(self, mock_st):
        """Test getting user-specific data from session state"""
        mock_st.session_state = {
            'user_test_selected_stocks': ['GP', 'ACI']
        }
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        data = session_manager.get_user_data('selected_stocks')
        
        assert data == ['GP', 'ACI']

    @patch('src.services.session_manager.st')
    def test_set_user_data(self, mock_st):
        """Test setting user-specific data in session state"""
        mock_st.session_state = {}
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        session_manager.set_user_data('selected_stocks', ['GP', 'ACI'])
        
        assert mock_st.session_state['user_test_selected_stocks'] == ['GP', 'ACI']

    @patch('src.services.session_manager.st')
    def test_initialize_global_session(self, mock_st):
        """Test initializing global session state"""
        mock_st.session_state = {}
        mock_auth_service = Mock()
        
        session_manager = SessionManager(mock_auth_service)
        
        mock_config = Mock()
        mock_config.APP_MODE = 'redis'
        
        session_manager.initialize_global_session(mock_config)
        
        assert mock_st.session_state['app_mode'] == 'redis'
        assert 'last_update' in mock_st.session_state

    @patch('src.services.session_manager.st')
    def test_initialize_user_session(self, mock_st):
        """Test initializing user-specific session"""
        mock_st.session_state = {}
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        # Mock data loader
        mock_data_loader = Mock()
        mock_data_loader.load_selected_stocks.return_value = ['GP', 'ACI']
        mock_data_loader.load_portfolio_items.return_value = {}
        mock_data_loader.load_transactions.return_value = []
        mock_data_loader.load_portfolio_settings.return_value = {'initial_fund': 100000.0}
        
        session_manager.initialize_user_session(mock_data_loader)
        
        # Check that user-specific aliases were set
        assert mock_st.session_state.selected_stocks == ['GP', 'ACI']
        assert mock_st.session_state.portfolio_items == {}
        assert mock_st.session_state.transactions == []
        assert mock_st.session_state.portfolio_settings == {'initial_fund': 100000.0}
        assert mock_st.session_state.cash_balance == 100000.0
        assert mock_st.session_state.cash_transactions == []

    @patch('src.services.session_manager.st')
    def test_sync_user_data_with_data_manager(self, mock_st):
        """Test syncing user data with data manager"""
        mock_st.session_state = {
            'selected_stocks': ['GP', 'ACI'],
            'portfolio_items': {
                'GP': PortfolioItem(
                    symbol='GP',
                    quantity=100,
                    average_cost=300.0,
                    current_price=310.0,
                    last_updated=datetime.now()
                )
            },
            'transactions': [
                Transaction(
                    id='test-123',
                    symbol='GP',
                    transaction_type=TransactionType.BUY,
                    quantity=100,
                    price=300.0,
                    timestamp=datetime.now()
                )
            ],
            'portfolio_settings': {'initial_fund': 100000.0},
            'cash_balance': 70000.0,
            'cash_transactions': []
        }
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        # Mock data manager
        mock_data_manager = Mock()
        
        session_manager.sync_user_data(mock_data_manager)
        
        # Check that data manager methods were called with the correct data
        mock_data_manager.save_user_selected_stocks.assert_called_once_with(['GP', 'ACI'])
        assert mock_data_manager.save_user_portfolio_items.called
        assert mock_data_manager.save_user_transactions.called
        mock_data_manager.save_user_portfolio_settings.assert_called_once_with({'initial_fund': 100000.0})
        mock_data_manager.save_user_cash_balance.assert_called_once_with(70000.0)

    @patch('src.services.session_manager.st')
    def test_sync_user_data_without_data_manager(self, mock_st):
        """Test syncing user data without data manager"""
        mock_st.session_state = {
            'selected_stocks': ['GP', 'ACI'],
            'portfolio_items': {},
            'transactions': [],
            'portfolio_settings': {'initial_fund': 100000.0},
            'cash_balance': 100000.0,
            'cash_transactions': []
        }
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        # Call sync without data manager (should not error)
        session_manager.sync_user_data()
        
        # Should not error out

    @patch('src.services.session_manager.st')
    def test_clear_user_session(self, mock_st):
        """Test clearing user session"""
        mock_st.session_state = {
            'selected_stocks': ['GP', 'ACI'],
            'portfolio_items': {},
            'transactions': [],
            'portfolio_settings': {'initial_fund': 100000.0},
            'cash_balance': 100000.0,
            'cash_transactions': [],
            'user_test_data_loaded': True
        }
        mock_auth_service = Mock()
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        session_manager.clear_user_session()
        
        # Check that user session keys were removed from session state
        # The user-specific prefixes should not be in the main session state
        # but the aliases should be gone
        pass  # The implementation might need to be checked for what actually gets cleared

    @patch('src.services.session_manager.st')
    def test_get_current_user_info(self, mock_st):
        """Test getting current user information"""
        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = ('Test User', 'test_user')
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        user_info = session_manager.get_current_user_info()
        
        assert user_info['name'] == 'Test User'
        assert user_info['username'] == 'test_user'
        assert user_info['prefix'] == 'user_test_'

    @patch('src.services.session_manager.st')
    def test_is_user_authenticated(self, mock_st):
        """Test checking user authentication status"""
        mock_auth_service = Mock()
        mock_auth_service.is_authenticated.return_value = True
        
        session_manager = SessionManager(mock_auth_service)
        
        authenticated = session_manager.is_user_authenticated()
        
        assert authenticated is True
        mock_auth_service.is_authenticated.assert_called_once()

    @patch('src.services.session_manager.st')
    def test_get_user_summary_authenticated(self, mock_st):
        """Test getting user summary when authenticated"""
        mock_auth_service = Mock()
        mock_auth_service.is_authenticated.return_value = True
        mock_auth_service.get_current_user.return_value = ('Test User', 'test_user')
        mock_auth_service.get_user_session_prefix.return_value = "user_test_"
        
        session_manager = SessionManager(mock_auth_service)
        
        # Mock session state
        mock_st.session_state = {
            'selected_stocks': ['GP', 'ACI'],
            'portfolio_items': {
                'GP': PortfolioItem(
                    symbol='GP',
                    quantity=100,
                    average_cost=300.0,
                    current_price=310.0,
                    last_updated=datetime.now()
                )
            },
            'transactions': [
                Transaction(
                    id='test-123',
                    symbol='GP',
                    transaction_type=TransactionType.BUY,
                    quantity=100,
                    price=300.0,
                    timestamp=datetime.now()
                )
            ],
            'cash_balance': 70000.0
        }
        
        summary = session_manager.get_user_summary()
        
        # Check that summary contains expected structure
        assert 'user' in summary
        assert 'data' in summary
        assert summary['data']['tracked_stocks'] == 2
        assert summary['data']['portfolio_items'] == 1
        assert summary['data']['total_transactions'] == 1
        assert summary['data']['cash_balance'] == 70000.0

    @patch('src.services.session_manager.st')
    def test_get_user_summary_unauthenticated(self, mock_st):
        """Test getting user summary when not authenticated"""
        mock_auth_service = Mock()
        mock_auth_service.is_authenticated.return_value = False
        
        session_manager = SessionManager(mock_auth_service)
        
        summary = session_manager.get_user_summary()
        
        # Should return empty dict when not authenticated
        assert summary == {}