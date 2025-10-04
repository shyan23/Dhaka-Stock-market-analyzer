"""
Unit tests for the main application in the Stock Market Analyzer
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from src.app import StockMarketApp


class TestStockMarketApp:
    """Test cases for the main StockMarketApp class"""
    
    @patch('src.app.Config')
    @patch('src.app.AuthService')
    @patch('src.app.DSEAPIService')
    @patch('src.app.DataManager')
    @patch('src.app.SessionManager')
    @patch('src.app.SettingsManager')
    def test_init(self, mock_settings_manager, mock_session_manager, mock_data_manager, 
                  mock_dse_api, mock_auth_service, mock_config):
        """Test StockMarketApp initialization"""
        # Mock the service instances
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        mock_dse_api_instance = Mock()
        mock_data_manager_instance = Mock()
        mock_session_manager_instance = Mock()
        mock_settings_manager_instance = Mock()
        
        # Assign mock instances
        mock_config.return_value = mock_config_instance
        mock_auth_service.return_value = mock_auth_instance
        mock_dse_api.return_value = mock_dse_api_instance
        mock_data_manager.return_value = mock_data_manager_instance
        mock_session_manager.return_value = mock_session_manager_instance
        mock_settings_manager.return_value = mock_settings_manager_instance
        
        app = StockMarketApp()
        
        # Check that all services were initialized
        assert app.config is not None
        assert app.auth_service is not None
        assert app.dse_api is not None
        assert app.data_manager is not None
        assert app.session_manager is not None
        assert app.settings_manager is not None
        
        # Check that UI components were initialized
        assert app.setup_wizard_ui is not None
        assert app.dashboard_ui is not None
        assert app.stock_selector_ui is not None
        assert app.portfolio_ui is not None
        assert app.transactions_ui is not None
        assert app.price_tracker_ui is not None
        assert app.dse_finance_ui is not None

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    @patch('src.app.DSEAPIService')
    @patch('src.app.DataManager')
    @patch('src.app.SessionManager')
    @patch('src.app.SettingsManager')
    @patch('src.app.SetupWizardUI')
    @patch('src.app.DashboardUI')
    @patch('src.app.StockSelectorUI')
    @patch('src.app.PortfolioUI')
    @patch('src.app.TransactionsUI')
    @patch('src.app.PriceTrackerUI')
    @patch('src.app.DSEFinanceUI')
    def test_run_authenticated_and_configured(self, mock_dse_finance_ui, mock_price_tracker_ui, 
                                              mock_transactions_ui, mock_portfolio_ui, mock_stock_selector_ui,
                                              mock_dashboard_ui, mock_setup_wizard_ui, mock_settings_manager, 
                                              mock_session_manager, mock_data_manager, mock_dse_api, 
                                              mock_auth_service, mock_config):
        """Test run method when user is authenticated and app is configured"""
        # Mock the service instances
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        mock_dse_api_instance = Mock()
        mock_data_manager_instance = Mock()
        mock_session_manager_instance = Mock()
        mock_settings_manager_instance = Mock()
        
        # Configure mocks
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = ('Test User', True, 'test_user')
        mock_auth_service.return_value = mock_auth_instance
        mock_dse_api.return_value = mock_dse_api_instance
        mock_data_manager.return_value = mock_data_manager_instance
        mock_session_manager.return_value = mock_session_manager_instance
        mock_settings_manager.return_value = mock_settings_manager_instance
        mock_setup_wizard_ui.return_value = Mock()
        mock_dashboard_ui.return_value = Mock()
        mock_stock_selector_ui.return_value = Mock()
        mock_portfolio_ui.return_value = Mock()
        mock_transactions_ui.return_value = Mock()
        mock_price_tracker_ui.return_value = Mock()
        mock_dse_finance_ui.return_value = Mock()
        
        # Mock data loader to indicate app is configured
        with patch('src.app.DataLoader') as mock_data_loader:
            mock_data_loader_instance = Mock()
            mock_data_loader_instance.is_configured.return_value = True
            mock_data_loader.return_value = mock_data_loader_instance
            
            app = StockMarketApp()
            
            # Mock the methods that would be called during run
            with patch.object(app, '_render_main_app') as mock_render_main_app:
                app.run()
                
                # Check that main app was rendered (since user is authenticated and configured)
                mock_render_main_app.assert_called_once()

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    @patch('src.app.DSEAPIService')
    @patch('src.app.DataManager')
    @patch('src.app.SessionManager')
    @patch('src.app.SettingsManager')
    @patch('src.app.SetupWizardUI')
    def test_run_not_configured(self, mock_setup_wizard_ui, mock_settings_manager, 
                                mock_session_manager, mock_data_manager, mock_dse_api, 
                                mock_auth_service, mock_config):
        """Test run method when app is not configured"""
        # Mock the service instances
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        mock_dse_api_instance = Mock()
        mock_data_manager_instance = Mock()
        mock_session_manager_instance = Mock()
        mock_settings_manager_instance = Mock()
        mock_setup_wizard_ui_instance = Mock()
        
        # Configure mocks
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = ('Test User', True, 'test_user')
        mock_auth_service.return_value = mock_auth_instance
        mock_dse_api.return_value = mock_dse_api_instance
        mock_data_manager.return_value = mock_data_manager_instance
        mock_session_manager.return_value = mock_session_manager_instance
        mock_settings_manager.return_value = mock_settings_manager_instance
        mock_setup_wizard_ui.return_value = mock_setup_wizard_ui_instance
        
        # Mock data loader to indicate app is not configured
        with patch('src.app.DataLoader') as mock_data_loader:
            mock_data_loader_instance = Mock()
            mock_data_loader_instance.is_configured.return_value = False
            mock_data_loader.return_value = mock_data_loader_instance
            
            app = StockMarketApp()
            
            # Mock the methods that would be called during run
            with patch.object(app, '_render_main_app') as mock_render_main_app:
                app.run()
                
                # Check that setup wizard was rendered (since not configured)
                mock_setup_wizard_ui_instance.render.assert_called_once()
                
                # Check that main app was NOT rendered
                mock_render_main_app.assert_not_called()

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    def test_handle_authentication_success(self, mock_auth_service, mock_config):
        """Test _handle_authentication method with successful authentication"""
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = ('Test User', True, 'test_user')
        mock_auth_service.return_value = mock_auth_instance
        
        app = StockMarketApp()
        
        result = app._handle_authentication()
        
        assert result is True

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    def test_handle_authentication_failure(self, mock_auth_service, mock_config):
        """Test _handle_authentication method with failed authentication"""
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = (None, False, None)  # Failed
        # Mock the get_demo_credentials method to return a proper dict
        mock_auth_instance.get_demo_credentials.return_value = {
            "Demo User": {"username": "demo_user", "password": "demo123"}
        }
        mock_auth_service.return_value = mock_auth_instance
        
        app = StockMarketApp()
        
        # Mock streamlit for error message
        with patch('src.app.st') as mock_st:
            mock_st.error = Mock()
            mock_st.warning = Mock()
            
            result = app._handle_authentication()
        
        assert result is False

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    def test_handle_authentication_none_status(self, mock_auth_service, mock_config):
        """Test _handle_authentication method with None authentication status"""
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = (None, None, None)  # None status
        # Mock the get_demo_credentials method to return a proper dict
        mock_auth_instance.get_demo_credentials.return_value = {
            "Demo User": {"username": "demo_user", "password": "demo123"}
        }
        mock_auth_service.return_value = mock_auth_instance
        
        app = StockMarketApp()
        
        # Mock streamlit for warning message
        with patch('src.app.st') as mock_st:
            mock_st.warning = Mock()
            
            result = app._handle_authentication()
        
        assert result is False

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    @patch('src.app.DataLoader')
    def test_is_configured(self, mock_data_loader, mock_auth_service, mock_config):
        """Test _is_configured method"""
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        mock_data_loader_instance = Mock()
        
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = ('Test User', True, 'test_user')
        mock_auth_service.return_value = mock_auth_instance
        mock_data_loader.return_value = mock_data_loader_instance
        
        app = StockMarketApp()
        
        # Test when configured
        mock_data_loader_instance.is_configured.return_value = True
        assert app._is_configured() is True
        
        # Test when not configured
        mock_data_loader_instance.is_configured.return_value = False
        assert app._is_configured() is False

    @patch('src.app.Config')
    @patch('src.app.AuthService')
    @patch('src.app.DSEAPIService')
    @patch('src.app.DataManager')
    @patch('src.app.SessionManager')
    @patch('src.app.SettingsManager')
    @patch('src.app.SetupWizardUI')
    @patch('src.app.DashboardUI')
    @patch('src.app.StockSelectorUI')
    @patch('src.app.PortfolioUI')
    @patch('src.app.TransactionsUI')
    @patch('src.app.PriceTrackerUI')
    @patch('src.app.DSEFinanceUI')
    def test_get_app_info(self, mock_dse_finance_ui, mock_price_tracker_ui, 
                          mock_transactions_ui, mock_portfolio_ui, mock_stock_selector_ui,
                          mock_dashboard_ui, mock_setup_wizard_ui, mock_settings_manager, 
                          mock_session_manager, mock_data_manager, mock_dse_api, 
                          mock_auth_service, mock_config):
        """Test get_app_info method"""
        # Mock the service instances
        mock_config_instance = Mock()
        mock_auth_instance = Mock()
        mock_dse_api_instance = Mock()
        mock_data_manager_instance = Mock()
        mock_session_manager_instance = Mock()
        mock_settings_manager_instance = Mock()
        
        # Configure mocks
        mock_config.return_value = mock_config_instance
        mock_auth_instance.login.return_value = ('Test User', True, 'test_user')
        mock_auth_service.return_value = mock_auth_instance
        mock_dse_api.return_value = mock_dse_api_instance
        mock_data_manager.return_value = mock_data_manager_instance
        mock_session_manager.return_value = mock_session_manager_instance
        mock_settings_manager.return_value = mock_settings_manager_instance
        mock_setup_wizard_ui.return_value = Mock()
        mock_dashboard_ui.return_value = Mock()
        mock_stock_selector_ui.return_value = Mock()
        mock_portfolio_ui.return_value = Mock()
        mock_transactions_ui.return_value = Mock()
        mock_price_tracker_ui.return_value = Mock()
        mock_dse_finance_ui.return_value = Mock()
        
        app = StockMarketApp()
        
        info = app.get_app_info()
        
        # Check that the returned info has the expected structure
        assert 'version' in info
        assert 'architecture' in info
        assert 'components' in info
        assert 'features' in info
        
        # Check version
        assert info['version'] == '2.0.0'
        
        # Check architecture
        assert info['architecture'] == 'Modular'
        
        # Check that components exist
        assert 'services' in info['components']
        assert 'ui_components' in info['components']
        
        # Check some expected services
        expected_services = [
            'AuthService', 'SessionManager', 'DataLoader',
            'DataManager', 'SettingsManager', 'DSEAPIService'
        ]
        for service in expected_services:
            assert service in info['components']['services']
        
        # Check some expected UI components
        expected_ui_components = [
            'DashboardUI', 'StockSelectorUI', 'PortfolioUI',
            'TransactionsUI', 'PriceTrackerUI', 'DSEFinanceUI'
        ]
        for component in expected_ui_components:
            assert component in info['components']['ui_components']
        
        # Check some expected features
        expected_features = [
            'Multi-user authentication',
            'User-specific data isolation',
            'Modular architecture'
        ]
        for feature in expected_features:
            assert feature in info['features']