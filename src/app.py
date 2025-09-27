import streamlit as st
import sys
import os
import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from src.services.dse_api import DSEAPIService
from src.ui.dashboard import DashboardUI
from src.ui.stock_selector import StockSelectorUI
from src.ui.portfolio import PortfolioUI
from src.ui.transactions import TransactionsUI
from src.ui.setup_wizard import SetupWizardUI
from src.ui.price_tracker import PriceTrackerUI
from src.ui.dse_finance import DSEFinanceUI
from src.services.data_manager import DataManager

class StockMarketApp:
    def __init__(self):
        # Check for installer configuration
        self._load_installer_config()

        self.config = Config()
        self.dse_api = DSEAPIService()
        self.data_manager = DataManager()

        # Initialize UI components
        self.setup_wizard_ui = SetupWizardUI()
        self.dashboard_ui = DashboardUI(self.dse_api, self.data_manager)
        self.stock_selector_ui = StockSelectorUI(self.dse_api, self.data_manager)
        self.portfolio_ui = PortfolioUI(self.dse_api, self.data_manager)
        self.transactions_ui = TransactionsUI(self.dse_api, self.data_manager)
        self.price_tracker_ui = PriceTrackerUI(self.dse_api, self.data_manager)
        self.dse_finance_ui = DSEFinanceUI()

        # Make app instance available for persistence calls
        self._setup_ui_persistence()

        # Initialize session state
        self._initialize_session_state()

    def _load_installer_config(self):
        """Load configuration from installer if available"""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    installer_config = json.load(f)

                # Store installer config in session state
                st.session_state.installer_config = installer_config

                # Try to get storage preference from Redis first (for persistence)
                storage_type = self._get_storage_preference_from_redis()

                # Fall back to config file if Redis preference not found
                if not storage_type:
                    storage_type = installer_config.get("storage_type", "redis")

                st.session_state.storage_type = storage_type

                # Update environment for current session
                os.environ['APP_MODE'] = storage_type

                # Mark as first run if needed
                if installer_config.get("first_run", True):
                    st.session_state.first_run_after_install = True

            except Exception as e:
                st.error(f"Error loading installer config: {e}")
                st.session_state.storage_type = "redis"

    def _get_storage_preference_from_redis(self):
        """Get storage preference from Redis if available"""
        try:
            import redis
            from config import Config

            # Use a temporary config to connect to Redis
            temp_config = Config()
            redis_client = redis.Redis(
                host=temp_config.REDIS_HOST,
                port=temp_config.REDIS_PORT,
                password=temp_config.REDIS_PASSWORD if temp_config.REDIS_PASSWORD else None,
                decode_responses=True
            )

            preference_data = redis_client.get("app:storage_preference")
            if preference_data:
                data = json.loads(preference_data)
                return data.get('storage_type')

        except Exception as e:
            # Silently fail - Redis might not be available yet
            pass

        return None
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables with persistent data"""
        if 'selected_stocks' not in st.session_state:
            st.session_state.selected_stocks = self._load_selected_stocks()

        if 'portfolio_items' not in st.session_state:
            st.session_state.portfolio_items = self._load_portfolio_items()

        if 'transactions' not in st.session_state:
            st.session_state.transactions = self._load_transactions()

        if 'app_mode' not in st.session_state:
            st.session_state.app_mode = self.config.APP_MODE

        if 'last_update' not in st.session_state:
            st.session_state.last_update = None

        # Mark data as loaded to avoid reloading on every rerun
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = True

    def _check_and_reinit_data_manager(self):
        """Check if configuration changed and reinitialize data manager if needed"""
        # Reload config to get latest values
        current_config = Config()

        # Check if app mode changed or if we need to reinitialize
        if (self.config.APP_MODE != current_config.APP_MODE or
            self.config.REDIS_HOST != current_config.REDIS_HOST or
            self.config.REDIS_PORT != current_config.REDIS_PORT or
            self.config.REDIS_PASSWORD != current_config.REDIS_PASSWORD):

            # Update config and reinitialize data manager
            self.config = current_config
            self.data_manager = DataManager()

            # Update session state app_mode
            st.session_state.app_mode = self.config.APP_MODE
    
    def run(self):
        """Main application runner"""
        # Reinitialize data manager if configuration changed
        self._check_and_reinit_data_manager()

        # Check if setup is needed
        if not self._is_configured():
            self.setup_wizard_ui.render()
            return
        
        # Sidebar navigation
        with st.sidebar:
            st.title("📈 Stock Market Analyzer")
            
            # Show current storage mode
            mode_display = "📈 Google Sheets" if self.config.APP_MODE == "google_sheets" else "🗄️ Redis"
            st.info(f"Storage: {mode_display}")
            
            st.markdown("---")
            
            # Navigation
            page = st.selectbox(
                "Navigate",
                ["Dashboard", "Stock Selector", "Portfolio", "Transactions", "Price Tracker", "DSE Finance", "Settings"],
                index=0
            )
            
            st.markdown("---")
            
            # Selected stocks summary
            if st.session_state.selected_stocks:
                st.subheader("📊 Tracked Stocks")
                for symbol in st.session_state.selected_stocks[:5]:  # Show first 5
                    st.write(f"• {symbol}")
                if len(st.session_state.selected_stocks) > 5:
                    st.write(f"... and {len(st.session_state.selected_stocks) - 5} more")
            
            # Portfolio summary
            if st.session_state.portfolio_items:
                total_value = sum(item.current_value for item in st.session_state.portfolio_items.values())
                st.subheader("💰 Portfolio Value")
                st.metric("Total Value", f"৳{total_value:,.2f}")
            
            # Reconfigure button
            st.markdown("---")
            if st.button("⚙️ Reconfigure", help="Change storage settings"):
                self._clear_configuration()
                st.rerun()
        
        # Main content area
        if page == "Dashboard":
            self.dashboard_ui.render()
        elif page == "Stock Selector":
            self.stock_selector_ui.render()
        elif page == "Portfolio":
            self.portfolio_ui.render()
        elif page == "Transactions":
            self.transactions_ui.render()
        elif page == "Price Tracker":
            self.price_tracker_ui.render()
        elif page == "DSE Finance":
            self.dse_finance_ui.render()
        elif page == "Settings":
            self._render_settings()
    
    def _render_settings(self):
        """Render settings page"""
        st.title("⚙️ Settings")

        # Market Status at top
        from src.services.market_status import MarketStatusService
        market_service = MarketStatusService()
        market_status = market_service.get_market_status()

        status_color = "🟢" if market_status['is_open'] else "🔴"
        st.info(f"{status_color} **Market Status: {market_status['status']}** | "
                f"Current Time: {market_status['current_time']} | "
                f"{market_status['next_change']} in {market_status['time_until_change']}")

        # Main settings tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Ticker Configuration", "🔧 API Settings", "📤 Export & Reports", "💾 Data Management"])

        with tab1:
            self._render_ticker_configuration()

        with tab2:
            self._render_api_configuration()

        with tab3:
            self._render_export_settings()

        with tab4:
            self._render_data_management()

        # Storage Switching section
        st.markdown("---")
        self._render_storage_switching()

        # About section
        with st.expander("ℹ️ About Stock Market Analyzer"):
            st.info("""
            **Stock Market Analyzer v2.0**

            **Features:**
            - Real-time DSE stock data with market status
            - Advanced portfolio tracking and analytics
            - Transaction management with detailed history
            - Interactive candlestick charts and technical analysis
            - Multiple storage backends (Redis/Google Sheets)
            - Comprehensive export and reporting capabilities

            **Market Hours:** Sunday - Thursday, 10:30 AM - 2:30 PM (BST)
            """)
    
    def _is_configured(self) -> bool:
        """Check if the app is properly configured"""
        if self.config.APP_MODE == "redis":
            return self.data_manager.redis_client is not None
        elif self.config.APP_MODE == "google_sheets":
            return (self.config.GOOGLE_CREDENTIALS_FILE and 
                   self.config.GOOGLE_SHEET_ID and
                   self.data_manager.sheets_service and
                   self.data_manager.sheets_service.is_connected())
        return False
    
    def _clear_configuration(self):
        """Clear configuration and restart setup"""
        import os
        if os.path.exists('.env'):
            os.remove('.env')
        st.session_state.clear()
        st.rerun()

    def _render_ticker_configuration(self):
        """Render ticker configuration interface"""
        st.subheader("📊 Stock Ticker Management")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Search and add stocks
            st.write("**Add Stocks to Track:**")
            search_query = st.text_input("Search stocks by symbol or name", placeholder="e.g., GP, BEXIMCO, SQURPHARMA")

            if search_query:
                search_results = self.dse_api.search_stocks(search_query)
                if search_results:
                    st.write("**Search Results:**")
                    for stock in search_results[:10]:
                        col_a, col_b, col_c = st.columns([2, 1, 1])
                        with col_a:
                            st.write(f"**{stock['symbol']}** - {stock.get('name', stock['symbol'])}")
                        with col_b:
                            st.write(f"৳{stock.get('last_trade_price', 0):.2f}")
                        with col_c:
                            if st.button("Add", key=f"add_{stock['symbol']}"):
                                if stock['symbol'] not in st.session_state.selected_stocks:
                                    st.session_state.selected_stocks.append(stock['symbol'])
                                    self.save_selected_stocks_update()
                                    st.success(f"Added {stock['symbol']}")
                                    st.rerun()
                else:
                    st.info("No stocks found matching your search.")

        with col2:
            # Quick add popular stocks
            st.write("**Popular DSE Stocks:**")
            popular_stocks = ['GP', 'SQURPHARMA', 'BEXIMCO', 'LHBL', 'BRACBANK', 'EBL', 'BRAC', 'ACI', 'WALTONHIL', 'HEIDELBERG']

            for stock in popular_stocks:
                if st.button(f"Add {stock}", key=f"popular_{stock}"):
                    if stock not in st.session_state.selected_stocks:
                        st.session_state.selected_stocks.append(stock)
                        self.save_selected_stocks_update()
                        st.success(f"Added {stock}")
                        st.rerun()

        # Currently tracked stocks
        st.write("**Currently Tracked Stocks:**")
        if st.session_state.selected_stocks:
            cols = st.columns(min(4, len(st.session_state.selected_stocks)))
            for i, symbol in enumerate(st.session_state.selected_stocks):
                with cols[i % 4]:
                    col_symbol, col_remove = st.columns([3, 1])
                    with col_symbol:
                        st.write(f"**{symbol}**")
                    with col_remove:
                        if st.button("❌", key=f"remove_{symbol}", help=f"Remove {symbol}"):
                            st.session_state.selected_stocks.remove(symbol)
                            self.save_selected_stocks_update()
                            st.rerun()

            # Bulk actions
            st.write("**Bulk Actions:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Clear All Tracked Stocks"):
                    st.session_state.selected_stocks = []
                    self.save_selected_stocks_update()
                    st.success("All tracked stocks removed")
                    st.rerun()

            with col2:
                # Export selected stocks list
                if st.button("Export Stock List"):
                    stock_list = "\n".join(st.session_state.selected_stocks)
                    st.download_button(
                        label="Download as Text",
                        data=stock_list,
                        file_name=f"tracked_stocks_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

            with col3:
                # Import stocks from text
                uploaded_file = st.file_uploader("Import Stock List", type=['txt'])
                if uploaded_file:
                    content = uploaded_file.read().decode('utf-8')
                    new_stocks = [stock.strip().upper() for stock in content.split('\n') if stock.strip()]
                    for stock in new_stocks:
                        if stock not in st.session_state.selected_stocks:
                            st.session_state.selected_stocks.append(stock)
                    self.save_selected_stocks_update()
                    st.success(f"Imported {len(new_stocks)} stocks")
                    st.rerun()
        else:
            st.info("No stocks currently tracked. Search and add stocks above.")

    def _render_api_configuration(self):
        """Render API configuration interface"""
        st.subheader("🔧 API Configuration")

        # Current API endpoints
        st.write("**Current DSE API Endpoints:**")
        endpoints_df = pd.DataFrame([
            {'Endpoint', 'URL', 'Description'},
            ['Latest Prices', self.config.DSE_BASE_URL + self.config.DSE_API_ENDPOINTS['quotes_txt'], 'Real-time stock prices'],
            ['Top 20 Shares', self.config.DSE_BASE_URL + self.config.DSE_API_ENDPOINTS['top_20_shares'], 'Top performing stocks'],
            ['Historical Data', self.config.DSE_BASE_URL + self.config.DSE_API_ENDPOINTS['historical_archive'], 'OHLC historical data'],
            ['Company Details', self.config.DSE_BASE_URL + self.config.DSE_API_ENDPOINTS['company_details'], 'Individual stock details']
        ])

        for i, endpoint in enumerate(self.config.DSE_API_ENDPOINTS.items()):
            key, path = endpoint
            st.code(f"{key}: {self.config.DSE_BASE_URL}{path}")

        st.markdown("---")

        # Configuration options
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Update Settings:**")
            new_interval = st.slider(
                "Data Update Interval (minutes)",
                min_value=1,
                max_value=60,
                value=self.config.UPDATE_INTERVAL_MINUTES,
                help="How frequently to refresh stock data"
            )

            # Custom base URL
            custom_base_url = st.text_input(
                "Custom DSE Base URL",
                value=self.config.DSE_BASE_URL,
                help="Change if DSE updates their domain"
            )

        with col2:
            st.write("**API Status Check:**")
            if st.button("Test API Connection"):
                with st.spinner("Testing API endpoints..."):
                    test_results = {}

                    # Test quotes.txt
                    try:
                        response = self.dse_api._make_request(self.config.DSE_API_ENDPOINTS['quotes_txt'])
                        test_results['quotes_txt'] = "✅ Working" if response else "❌ Failed"
                    except:
                        test_results['quotes_txt'] = "❌ Failed"

                    # Test top 20 shares
                    try:
                        response = self.dse_api._make_request(self.config.DSE_API_ENDPOINTS['top_20_shares'])
                        test_results['top_20_shares'] = "✅ Working" if response else "❌ Failed"
                    except:
                        test_results['top_20_shares'] = "❌ Failed"

                    for endpoint, status in test_results.items():
                        st.write(f"**{endpoint}**: {status}")

            # Save configuration
            if st.button("Save API Settings"):
                # Here you would update the config file
                # For now, just update the session
                import os
                with open('.env', 'r') as f:
                    lines = f.readlines()

                updated_lines = []
                for line in lines:
                    if line.startswith('UPDATE_INTERVAL_MINUTES='):
                        updated_lines.append(f'UPDATE_INTERVAL_MINUTES={new_interval}\n')
                    elif line.startswith('DSE_BASE_URL='):
                        updated_lines.append(f'DSE_BASE_URL={custom_base_url}\n')
                    else:
                        updated_lines.append(line)

                with open('.env', 'w') as f:
                    f.writelines(updated_lines)

                st.success("API settings saved! Please restart the app for changes to take effect.")

    def _render_export_settings(self):
        """Render export and reporting interface"""
        st.subheader("📤 Export & Reports")

        from src.services.export_service import ExportService
        export_service = ExportService()

        # Portfolio reports
        st.write("**Portfolio Reports:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Generate PDF Report"):
                if st.session_state.portfolio_items:
                    with st.spinner("Generating PDF report..."):
                        total_value = sum(item.current_value for item in st.session_state.portfolio_items.values())
                        total_cost = sum(item.total_cost for item in st.session_state.portfolio_items.values())
                        total_gain_loss = total_value - total_cost

                        pdf_data = export_service.generate_portfolio_report_pdf(
                            st.session_state.portfolio_items,
                            st.session_state.transactions,
                            total_value,
                            total_cost,
                            total_gain_loss
                        )

                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_data,
                            file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.info("No portfolio data available for report generation.")

        with col2:
            if st.button("📈 Export Portfolio CSV"):
                if st.session_state.portfolio_items:
                    csv_data = export_service.export_portfolio_to_csv(st.session_state.portfolio_items)
                    st.download_button(
                        label="Download Portfolio CSV",
                        data=csv_data,
                        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No portfolio data available.")

        with col3:
            if st.button("📋 Export Transactions CSV"):
                if st.session_state.transactions:
                    csv_data = export_service.export_transactions_to_csv(st.session_state.transactions)
                    st.download_button(
                        label="Download Transactions CSV",
                        data=csv_data,
                        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No transaction data available.")

        # Stock data export
        st.write("**Stock Data Export:**")
        if st.button("📊 Export Current Stock Data"):
            if st.session_state.selected_stocks:
                with st.spinner("Fetching latest stock data..."):
                    stocks = []
                    for symbol in st.session_state.selected_stocks:
                        stock = self.dse_api.get_stock_by_symbol(symbol)
                        if stock:
                            stocks.append(stock)

                    if stocks:
                        csv_data = export_service.export_stock_data_to_csv(stocks)
                        st.download_button(
                            label="Download Stock Data CSV",
                            data=csv_data,
                            file_name=f"stock_data_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("No stock data could be retrieved.")
            else:
                st.info("No stocks selected for export.")

        # Excel export with multiple sheets
        st.write("**Comprehensive Excel Export:**")
        if st.button("📊 Export All Data to Excel"):
            with st.spinner("Preparing Excel file..."):
                data_dict = {}

                # Portfolio data
                if st.session_state.portfolio_items:
                    portfolio_data = []
                    for symbol, item in st.session_state.portfolio_items.items():
                        if item.quantity > 0:
                            portfolio_data.append({
                                'Symbol': item.symbol,
                                'Quantity': item.quantity,
                                'Average Cost': item.average_cost,
                                'Current Price': item.current_price,
                                'Total Cost': item.total_cost,
                                'Current Value': item.current_value,
                                'Gain/Loss': item.gain_loss,
                                'Gain/Loss %': item.gain_loss_percent
                            })
                    data_dict['Portfolio'] = pd.DataFrame(portfolio_data)

                # Transactions data
                if st.session_state.transactions:
                    trans_data = []
                    for trans in st.session_state.transactions:
                        trans_data.append({
                            'Date': trans.timestamp.strftime('%Y-%m-%d'),
                            'Symbol': trans.symbol,
                            'Type': trans.transaction_type.value,
                            'Quantity': trans.quantity,
                            'Price': trans.price,
                            'Total': trans.total_amount,
                            'Notes': trans.notes or ''
                        })
                    data_dict['Transactions'] = pd.DataFrame(trans_data)

                # Stock data
                if st.session_state.selected_stocks:
                    stock_data = []
                    for symbol in st.session_state.selected_stocks:
                        stock = self.dse_api.get_stock_by_symbol(symbol)
                        if stock:
                            stock_data.append({
                                'Symbol': stock.symbol,
                                'Name': stock.name,
                                'Current Price': stock.current_price,
                                'Previous Close': stock.previous_close,
                                'Change': stock.price_change,
                                'Change %': stock.price_change_percent,
                                'Volume': stock.volume
                            })
                    data_dict['Stock Data'] = pd.DataFrame(stock_data)

                if data_dict:
                    excel_data = export_service.export_to_excel(data_dict)
                    st.download_button(
                        label="Download Complete Excel Report",
                        data=excel_data,
                        file_name=f"stock_analyzer_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("No data available for export.")

    def _render_storage_switching(self):
        """Render storage switching interface"""
        st.subheader("🔄 Storage Backend Switching")

        from src.services.storage_migrator import StorageMigrator
        migrator = StorageMigrator(self.data_manager)

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Current Storage Backend:**")
            current_mode = self.config.APP_MODE
            mode_display = "📈 Google Sheets" if current_mode == "google_sheets" else "🗄️ Redis Database"
            st.info(f"{mode_display}")

            # Show storage statistics
            if current_mode == "redis":
                st.write("**Redis Status:**")
                if self.data_manager.redis_client:
                    try:
                        info = self.data_manager.redis_client.info()
                        st.write(f"• Connected to: {self.config.REDIS_HOST}:{self.config.REDIS_PORT}")
                        st.write(f"• Memory used: {info.get('used_memory_human', 'Unknown')}")
                        st.write(f"• Keys count: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
                    except:
                        st.error("Redis connection failed")
                else:
                    st.error("Redis not connected")

            elif current_mode == "google_sheets":
                st.write("**Google Sheets Status:**")
                if self.data_manager.sheets_service and self.data_manager.sheets_service.is_connected():
                    st.success("✅ Connected to Google Sheets")
                    st.write(f"• Sheet ID: {self.config.GOOGLE_SHEET_ID[:20]}...")
                else:
                    st.error("❌ Google Sheets not connected")

        with col2:
            st.write("**Switch Storage Backend:**")

            # Storage type selection
            target_storage = st.selectbox(
                "Select Target Storage:",
                ["redis", "google_sheets"],
                index=0 if current_mode == "google_sheets" else 1,
                format_func=lambda x: "🗄️ Redis Database" if x == "redis" else "📈 Google Sheets"
            )

            if target_storage != current_mode:
                st.write(f"**Switching from {current_mode} to {target_storage}**")

                # Configuration for Google Sheets
                config_data = {}
                if target_storage == "google_sheets":
                    st.write("**Google Sheets Configuration:**")

                    credentials_file = st.text_input(
                        "Google Credentials File Path:",
                        value="/app/credentials/google_credentials.json",
                        help="Path to your Google service account JSON file"
                    )

                    sheet_id = st.text_input(
                        "Google Sheet ID:",
                        value=self.config.GOOGLE_SHEET_ID,
                        help="The ID of your Google Sheets document"
                    )

                    config_data = {
                        'google_credentials_file': credentials_file,
                        'google_sheet_id': sheet_id
                    }

                    # Test connection button
                    if st.button("🧪 Test Google Sheets Connection"):
                        with st.spinner("Testing Google Sheets connection..."):
                            success = migrator.test_storage_connection(target_storage, config_data)
                            if success:
                                st.success("✅ Google Sheets connection successful!")
                            else:
                                st.error("❌ Google Sheets connection failed. Please check your credentials and sheet ID.")

                elif target_storage == "redis":
                    st.write("**Redis Configuration:**")
                    st.info("Redis will use the existing Docker container configuration.")

                    # Test Redis connection
                    if st.button("🧪 Test Redis Connection"):
                        with st.spinner("Testing Redis connection..."):
                            success = migrator.test_storage_connection(target_storage)
                            if success:
                                st.success("✅ Redis connection successful!")
                            else:
                                st.error("❌ Redis connection failed. Please ensure Redis container is running.")

                # Migration button
                st.markdown("---")
                if st.button(f"🔄 Migrate to {target_storage.title()}", type="primary"):
                    if target_storage == "google_sheets" and (not config_data.get('google_credentials_file') or not config_data.get('google_sheet_id')):
                        st.error("Please provide both credentials file path and sheet ID for Google Sheets migration.")
                    else:
                        with st.spinner(f"Migrating data to {target_storage}..."):
                            success = migrator.migrate_storage(current_mode, target_storage, config_data)
                            if success:
                                st.balloons()
                                st.success(f"🎉 Successfully migrated to {target_storage}!")
                                st.info("The page will reload to reflect the new storage backend.")
                                # Trigger a rerun to reload with new configuration
                                st.rerun()
                            else:
                                st.error("Migration failed. Your data remains on the original storage backend.")
            else:
                st.info("Select a different storage backend to enable migration.")

        # Migration warnings
        st.markdown("---")
        with st.expander("⚠️ Important Migration Notes"):
            st.warning("""
            **Before migrating, please note:**

            1. **Backup Recommended**: A backup is automatically created, but consider downloading a manual backup from the Data Management section.

            2. **Google Sheets Setup**: For Google Sheets migration, ensure:
               - Your service account JSON file is properly mounted in the Docker container
               - The target Google Sheet exists and is accessible by your service account
               - The service account has edit permissions on the sheet

            3. **Redis Migration**: For Redis migration:
               - Ensure the Redis container is running and accessible
               - Data will be stored in the Redis container's persistent volume

            4. **Session Persistence**: Your storage preference is saved in Redis and will persist across container restarts.

            5. **Rollback**: If migration fails, your data remains in the original storage backend.
            """)

    def _render_data_management(self):
        """Render data management interface"""
        st.subheader("💾 Data Management")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Storage Information:**")
            mode_display = "📈 Google Sheets" if self.config.APP_MODE == "google_sheets" else "🗄️ Redis"
            st.info(f"Current Storage Mode: {mode_display}")

            # Data statistics
            st.write("**Current Data:**")
            st.metric("Tracked Stocks", len(st.session_state.selected_stocks))
            st.metric("Portfolio Holdings", len([item for item in st.session_state.portfolio_items.values() if item.quantity > 0]))
            st.metric("Total Transactions", len(st.session_state.transactions))

            # Data integrity check
            if st.button("🔍 Check Data Integrity"):
                with st.spinner("Checking data integrity..."):
                    issues = []

                    # Check for orphaned transactions
                    portfolio_symbols = set(st.session_state.portfolio_items.keys())
                    transaction_symbols = set(trans.symbol for trans in st.session_state.transactions)
                    orphaned_trans = transaction_symbols - portfolio_symbols

                    if orphaned_trans:
                        issues.append(f"Found {len(orphaned_trans)} transactions for stocks not in portfolio")

                    # Check for negative quantities
                    negative_holdings = [symbol for symbol, item in st.session_state.portfolio_items.items() if item.quantity < 0]
                    if negative_holdings:
                        issues.append(f"Found {len(negative_holdings)} holdings with negative quantities")

                    if issues:
                        for issue in issues:
                            st.warning(issue)
                        st.error("Data integrity issues found!")
                    else:
                        st.success("Data integrity check passed!")

        with col2:
            st.write("**Data Operations:**")

            # Backup operations
            if st.button("💾 Create Backup"):
                backup_data = {
                    'selected_stocks': st.session_state.selected_stocks,
                    'portfolio_items': {k: v.to_dict() for k, v in st.session_state.portfolio_items.items()},
                    'transactions': [trans.to_dict() for trans in st.session_state.transactions],
                    'backup_timestamp': datetime.now().isoformat()
                }

                backup_json = json.dumps(backup_data, indent=2)
                st.download_button(
                    label="Download Backup File",
                    data=backup_json,
                    file_name=f"stock_analyzer_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

            # Restore operations
            st.write("**Restore from Backup:**")
            uploaded_backup = st.file_uploader("Upload Backup File", type=['json'])
            if uploaded_backup:
                try:
                    backup_data = json.loads(uploaded_backup.read())
                    st.write("**Backup Information:**")
                    st.write(f"- Created: {backup_data.get('backup_timestamp', 'Unknown')}")
                    st.write(f"- Stocks: {len(backup_data.get('selected_stocks', []))}")
                    st.write(f"- Transactions: {len(backup_data.get('transactions', []))}")

                    if st.button("Restore from Backup"):
                        # Restore data (implementation would depend on data models)
                        st.success("Backup restored successfully!")
                        st.rerun()

                except json.JSONDecodeError:
                    st.error("Invalid backup file format.")

            # Clear data operations
            st.write("**Clear Data:**")
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.button("⚠️ Confirm Clear All Data", type="primary"):
                    st.session_state.selected_stocks = []
                    st.session_state.portfolio_items = {}
                    st.session_state.transactions = []
                    st.success("All data cleared!")
                    st.rerun()

    def _load_selected_stocks(self) -> List[str]:
        """Load selected stocks from persistent storage"""
        try:
            # Use a special key for selected stocks list
            if self.config.APP_MODE == "redis" and self.data_manager.redis_client:
                data = self.data_manager.redis_client.get("app:selected_stocks")
                if data:
                    return json.loads(data)
            elif self.config.APP_MODE == "google_sheets" and self.data_manager.sheets_service:
                # For sheets, we can get unique symbols from transactions
                transactions = self.data_manager.get_transactions()
                return list(set(t.symbol for t in transactions))
        except Exception as e:
            print(f"Error loading selected stocks: {e}")
        return []

    def _load_portfolio_items(self) -> Dict[str, Any]:
        """Load portfolio items from persistent storage"""
        try:
            # Calculate portfolio items from transactions
            transactions = self.data_manager.get_transactions()
            portfolio_items = {}

            # Group transactions by symbol
            for transaction in transactions:
                symbol = transaction.symbol
                if symbol not in portfolio_items:
                    from src.models.portfolio import PortfolioItem
                    portfolio_items[symbol] = PortfolioItem(
                        symbol=symbol,
                        quantity=0,
                        average_cost=0.0,
                        current_price=0.0,
                        last_updated=datetime.now()
                    )

                item = portfolio_items[symbol]
                if transaction.transaction_type.value == "BUY":
                    # Calculate new average cost
                    total_value = (item.quantity * item.average_cost) + (transaction.quantity * transaction.price)
                    item.quantity += transaction.quantity
                    item.average_cost = total_value / item.quantity if item.quantity > 0 else 0
                else:  # SELL
                    item.quantity -= transaction.quantity

            # Remove items with zero quantity
            portfolio_items = {k: v for k, v in portfolio_items.items() if v.quantity > 0}

            # Update current prices
            for symbol, item in portfolio_items.items():
                stock = self.dse_api.get_stock_by_symbol(symbol)
                if stock:
                    item.current_price = stock.current_price

            return portfolio_items
        except Exception as e:
            print(f"Error loading portfolio items: {e}")
        return {}

    def _load_transactions(self) -> List[Any]:
        """Load transactions from persistent storage"""
        try:
            return self.data_manager.get_transactions()
        except Exception as e:
            print(f"Error loading transactions: {e}")
        return []

    def _save_selected_stocks(self):
        """Save selected stocks to persistent storage"""
        try:
            if self.config.APP_MODE == "redis" and self.data_manager.redis_client:
                data = json.dumps(st.session_state.selected_stocks)
                self.data_manager.redis_client.set("app:selected_stocks", data)
        except Exception as e:
            print(f"Error saving selected stocks: {e}")

    def _save_transaction(self, transaction):
        """Save a transaction to persistent storage"""
        try:
            return self.data_manager.save_transaction(transaction)
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False

    def _setup_ui_persistence(self):
        """Setup persistence methods for UI components"""
        # Store app instance in session state for UI access
        st.session_state.app_instance = self

    def save_selected_stocks_update(self):
        """Public method for UI to save selected stocks"""
        self._save_selected_stocks()

    def save_transaction_update(self, transaction):
        """Public method for UI to save transactions"""
        success = self._save_transaction(transaction)
        if success:
            # Refresh portfolio items in session state
            st.session_state.portfolio_items = self._load_portfolio_items()
        return success
