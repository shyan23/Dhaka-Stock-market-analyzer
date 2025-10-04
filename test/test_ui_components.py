"""
Unit tests for UI components in the Stock Market Analyzer
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from datetime import datetime
from src.ui.dashboard import DashboardUI
from src.ui.stock_selector import StockSelectorUI
from src.ui.portfolio import PortfolioUI
from src.ui.transactions import TransactionsUI


class TestDashboardUI:
    """Test cases for the Dashboard UI component"""
    
    @patch('src.ui.dashboard.st')
    def test_init(self, mock_st):
        """Test DashboardUI initialization"""
        # Mock required dependencies
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        assert dashboard_ui.dse_api == mock_dse_api
        assert dashboard_ui.data_manager == mock_data_manager
        assert dashboard_ui.time_range_selector is not None

    @patch('src.ui.dashboard.st')
    @patch('src.ui.dashboard.go')
    @patch('src.ui.dashboard.px')
    @patch('src.ui.dashboard.pd')
    def test_render(self, mock_pd, mock_px, mock_go, mock_st):
        """Test DashboardUI render method"""
        # Mock required dependencies
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        # Mock session state to have selected stocks
        mock_st.session_state = {
            'selected_stocks': ['GP', 'ACI'],
            'portfolio_items': {}
        }
        
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Mock the stock API call
        mock_stock = Mock()
        mock_stock.current_price = 300.0
        mock_stock.price_change = 5.0
        mock_stock.price_change_percent = 1.67
        mock_stock.name = "Grameenphone Ltd"
        mock_stock.volume = 1000000
        mock_dse_api.get_stock_by_symbol.return_value = mock_stock
        
        # Mock the render methods
        with patch.object(dashboard_ui, '_render_market_status_bar'), \
             patch.object(dashboard_ui, '_render_portfolio_summary'), \
             patch.object(dashboard_ui, '_render_price_charts'), \
             patch.object(dashboard_ui, '_render_portfolio_performance'), \
             patch.object(dashboard_ui, '_render_holdings_distribution'), \
             patch.object(dashboard_ui, '_render_stock_details'):
            
            # Call render
            dashboard_ui.render()
            
            # Check that title was set
            mock_st.title.assert_called_once_with("📈 Portfolio Dashboard")

    @patch('src.ui.dashboard.st')
    def test_render_no_selected_stocks(self, mock_st):
        """Test DashboardUI render with no selected stocks"""
        # Mock required dependencies
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        # Mock session state with no selected stocks
        mock_st.session_state = {
            'selected_stocks': [],
            'portfolio_items': {}
        }
        
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Call render
        dashboard_ui.render()
        
        # Check that warning was shown
        mock_st.warning.assert_called_once_with("⚠️ No stocks selected for tracking. Please go to 'Stock Selector' to add stocks.")

    @patch('src.ui.dashboard.st')
    def test_render_market_status_bar(self, mock_st):
        """Test _render_market_status_bar method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Mock the market status service
        with patch('src.ui.dashboard.MarketStatusService') as mock_market_status_service:
            mock_service_instance = Mock()
            mock_service_instance.get_market_status.return_value = {
                'is_open': True,
                'status': 'OPEN',
                'current_time': '10:30 AM',
                'next_change': 'Close',
                'time_until_change': '4 hours',
                'market_hours': '10:30 AM - 2:30 PM'
            }
            mock_market_status_service.return_value = mock_service_instance
            
            # Mock container and columns
            mock_container = Mock()
            mock_col1, mock_col2, mock_col3, mock_col4 = Mock(), Mock(), Mock(), Mock()
            mock_st.container.return_value = mock_container
            mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3, mock_col4]
            
            # Call the method
            dashboard_ui._render_market_status_bar()
            
            # Check that container was created
            mock_st.container.assert_called_once()

    @patch('src.ui.dashboard.st')
    def test_render_portfolio_summary(self, mock_st):
        """Test _render_portfolio_summary method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Mock session state
        mock_st.session_state = {
            'selected_stocks': ['GP'],
            'portfolio_items': {
                'GP': Mock(quantity=100, average_cost=300.0, current_price=310.0)
            }
        }
        
        # Mock stock data
        mock_stock = Mock()
        mock_stock.current_price = 310.0
        mock_stock.price_change = 10.0
        mock_stock.price_change_percent = 3.33
        mock_stock.name = "Grameenphone Ltd"
        mock_dse_api.get_stock_by_symbol.return_value = mock_stock
        
        # Mock columns
        mock_col1, mock_col2, mock_col3, mock_col4 = Mock(), Mock(), Mock(), Mock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3, mock_col4]
        
        # Call the method
        dashboard_ui._render_portfolio_summary()
        
        # Check that columns were created
        mock_st.columns.assert_called_once_with(4)

    @patch('src.ui.dashboard.st')
    def test_create_line_chart(self, mock_st):
        """Test _create_line_chart method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Mock data
        from src.models.stock import StockPriceHistory
        mock_history = [
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
        
        # Mock the chart libraries
        with patch('src.ui.dashboard.go.Figure') as mock_fig_class, \
             patch('src.ui.dashboard.pd.DataFrame') as mock_df_class:
            
            mock_fig = Mock()
            mock_fig_class.return_value = mock_fig
            mock_df_class.return_value = Mock()
            
            # Call the method
            dashboard_ui._create_line_chart("GP", mock_history)
            
            # Check that Figure was created
            mock_fig_class.assert_called_once()

    @patch('src.ui.dashboard.st')
    def test_create_candlestick_chart(self, mock_st):
        """Test _create_candlestick_chart method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Mock data
        from src.models.stock import StockPriceHistory
        mock_history = [
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
        
        # Mock the chart libraries
        with patch('src.ui.dashboard.make_subplots') as mock_make_subplots, \
             patch('src.ui.dashboard.pd.DataFrame') as mock_df_class:
            
            mock_fig = Mock()
            mock_make_subplots.return_value = mock_fig
            mock_df_class.return_value = Mock()
            
            # Call the method
            dashboard_ui._create_candlestick_chart("GP", mock_history)
            
            # Check that make_subplots was called
            mock_make_subplots.assert_called()

    @patch('src.ui.dashboard.st')
    def test_create_bar_chart(self, mock_st):
        """Test _create_bar_chart method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        
        # Mock data
        from src.models.stock import StockPriceHistory
        mock_history = [
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
        
        # Mock the chart libraries
        with patch('src.ui.dashboard.go.Figure') as mock_fig_class, \
             patch('src.ui.dashboard.pd.DataFrame') as mock_df_class:
            
            mock_fig = Mock()
            mock_fig_class.return_value = mock_fig
            mock_df_class.return_value = Mock()
            
            # Call the method
            dashboard_ui._create_bar_chart("GP", mock_history)
            
            # Check that Figure was created
            mock_fig_class.assert_called_once()


class TestStockSelectorUI:
    """Test cases for the Stock Selector UI component"""
    
    @patch('src.ui.stock_selector.st')
    def test_init(self, mock_st):
        """Test StockSelectorUI initialization"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        stock_selector_ui = StockSelectorUI(mock_dse_api, mock_data_manager)
        
        assert stock_selector_ui.dse_api == mock_dse_api
        assert stock_selector_ui.data_manager == mock_data_manager

    @patch('src.ui.stock_selector.st')
    def test_render(self, mock_st):
        """Test StockSelectorUI render method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        stock_selector_ui = StockSelectorUI(mock_dse_api, mock_data_manager)
        
        # Mock session state
        mock_st.session_state = {'selected_stocks': []}
        
        # Mock the search functionality
        with patch.object(stock_selector_ui, '_render_search_interface'):
            stock_selector_ui.render()
            
            mock_st.title.assert_called_once_with("🔍 Stock Search & Selection")


class TestPortfolioUI:
    """Test cases for the Portfolio UI component"""
    
    @patch('src.ui.portfolio.st')
    def test_init(self, mock_st):
        """Test PortfolioUI initialization"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        portfolio_ui = PortfolioUI(mock_dse_api, mock_data_manager)
        
        assert portfolio_ui.dse_api == mock_dse_api
        assert portfolio_ui.data_manager == mock_data_manager

    @patch('src.ui.portfolio.st')
    def test_render(self, mock_st):
        """Test PortfolioUI render method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        portfolio_ui = PortfolioUI(mock_dse_api, mock_data_manager)
        
        # Mock session state
        mock_st.session_state = {
            'portfolio_items': {},
            'transactions': [],
            'selected_stocks': []
        }
        
        # Mock the render methods
        with patch.object(portfolio_ui, '_render_portfolio_overview'), \
             patch.object(portfolio_ui, '_render_portfolio_holdings'), \
             patch.object(portfolio_ui, '_render_performance_metrics'):
            
            portfolio_ui.render()
            
            mock_st.title.assert_called_once_with("💼 Portfolio Management")


class TestTransactionsUI:
    """Test cases for the Transactions UI component"""
    
    @patch('src.ui.transactions.st')
    def test_init(self, mock_st):
        """Test TransactionsUI initialization"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        transactions_ui = TransactionsUI(mock_dse_api, mock_data_manager)
        
        assert transactions_ui.dse_api == mock_dse_api
        assert transactions_ui.data_manager == mock_data_manager

    @patch('src.ui.transactions.st')
    def test_render(self, mock_st):
        """Test TransactionsUI render method"""
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        transactions_ui = TransactionsUI(mock_dse_api, mock_data_manager)
        
        # Mock session state
        mock_st.session_state = {
            'transactions': [],
            'portfolio_items': {},
            'cash_balance': 100000.0
        }
        
        # Mock the render methods
        with patch.object(transactions_ui, '_render_transaction_form'), \
             patch.object(transactions_ui, '_render_transaction_history'), \
             patch.object(transactions_ui, '_render_cash_management'):
            
            transactions_ui.render()
            
            mock_st.title.assert_called_once_with("📋 Transaction Management")


class TestUIIntegration:
    """Integration tests for UI components"""
    
    @patch('src.ui.dashboard.st')
    @patch('src.ui.stock_selector.st')
    @patch('src.ui.portfolio.st')
    @patch('src.ui.transactions.st')
    def test_all_ui_components_init(self, mock_st1, mock_st2, mock_st3, mock_st4):
        """Test that all UI components can be initialized without errors"""
        # Mock dependencies
        mock_dse_api = Mock()
        mock_data_manager = Mock()
        
        # Initialize all UI components
        dashboard_ui = DashboardUI(mock_dse_api, mock_data_manager)
        stock_selector_ui = StockSelectorUI(mock_dse_api, mock_data_manager)
        portfolio_ui = PortfolioUI(mock_dse_api, mock_data_manager)
        transactions_ui = TransactionsUI(mock_dse_api, mock_data_manager)
        
        # Verify they were created
        assert dashboard_ui is not None
        assert stock_selector_ui is not None
        assert portfolio_ui is not None
        assert transactions_ui is not None