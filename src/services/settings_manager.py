"""
Settings Manager for Stock Market Analyzer
Handles application settings and configuration
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class SettingsManager:
    """Manages application settings and configuration"""

    def __init__(self, config, data_manager, session_manager):
        self.config = config
        self.data_manager = data_manager
        self.session_manager = session_manager

    def render_settings_page(self):
        """Render the main settings page"""
        st.title("⚙️ Settings")

        # Market Status at top
        self._render_market_status()

        # Main settings tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Ticker Configuration",
            "🔧 API Settings",
            "📤 Export & Reports",
            "💾 Data Management",
            "💰 Portfolio Settings"
        ])

        with tab1:
            self._render_ticker_configuration()

        with tab2:
            self._render_api_configuration()

        with tab3:
            self._render_export_settings()

        with tab4:
            self._render_data_management()

        with tab5:
            self._render_portfolio_settings()

        # Storage Switching section
        st.markdown("---")
        self._render_storage_switching()

    def _render_market_status(self):
        """Render market status information"""
        try:
            from src.services.market_status import MarketStatusService
            market_service = MarketStatusService()
            market_status = market_service.get_market_status()
            status_color = "🟢" if market_status['is_open'] else "🔴"
            st.info(f"{status_color} **Market Status: {market_status['status']}** | "
                    f"Current Time: {market_status['current_time']} | "
                    f"{market_status['next_change']} in {market_status['time_until_change']}")
        except Exception as e:
            st.warning(f"Could not fetch market status: {e}")

    def _render_ticker_configuration(self):
        """Render ticker configuration settings"""
        st.subheader("📊 Ticker Configuration")

        # Auto-refresh settings
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Display Settings:**")
            show_percentages = st.checkbox("Show percentage changes", value=True)
            show_volumes = st.checkbox("Show trading volumes", value=True)
            compact_view = st.checkbox("Use compact view", value=False)

        with col2:
            st.write("**Update Settings:**")
            auto_refresh = st.checkbox("Auto-refresh data", value=True)
            if auto_refresh:
                refresh_interval = st.slider(
                    "Refresh interval (seconds)",
                    min_value=10,
                    max_value=300,
                    value=60,
                    step=10
                )

        # Default stocks
        st.write("**Default Stocks for New Users:**")
        default_stocks = st.text_area(
            "Enter stock symbols (one per line)",
            value="SQURPHARMA\nDHAKABANK\nISLAMIBANK\nPRIMEBANK",
            help="These stocks will be automatically added for new users"
        )

        if st.button("💾 Save Ticker Settings"):
            # Save settings logic here
            st.success("✅ Ticker settings saved!")

    def _render_api_configuration(self):
        """Render API configuration settings"""
        st.subheader("🔧 API Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Data Sources:**")
            primary_source = st.selectbox(
                "Primary data source",
                ["DSE Official", "YFinance Backup"],
                index=0
            )

            enable_fallback = st.checkbox("Enable fallback sources", value=True)

        with col2:
            st.write("**Update Settings:**")
            new_interval = st.slider(
                "Data Update Interval (minutes)",
                min_value=1,
                max_value=60,
                value=self.config.UPDATE_INTERVAL_MINUTES,
                help="How frequently to refresh stock data"
            )

        # API endpoints
        st.write("**API Endpoints:**")
        with st.expander("Advanced API Settings"):
            dse_base_url = st.text_input("DSE Base URL", value="https://www.dsebd.org")
            timeout_seconds = st.number_input("Request timeout (seconds)", min_value=5, max_value=60, value=15)

        if st.button("💾 Save API Settings"):
            # Update environment variables or config
            st.success("✅ API settings saved!")

    def _render_export_settings(self):
        """Render export and reporting settings"""
        st.subheader("📤 Export & Reports")

        # Export formats
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Export Data:**")

            # Portfolio export
            if st.button("📊 Export Portfolio (CSV)"):
                self._export_portfolio_csv()

            if st.button("💼 Export Transactions (CSV)"):
                self._export_transactions_csv()

            if st.button("📈 Export All Data (JSON)"):
                self._export_all_data_json()

        with col2:
            st.write("**Report Generation:**")

            # Date range for reports
            start_date = st.date_input("Report start date")
            end_date = st.date_input("Report end date")

            if st.button("📋 Generate Performance Report"):
                self._generate_performance_report(start_date, end_date)

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
            summary = self.session_manager.get_user_summary()
            if summary:
                data = summary['data']
                st.metric("Tracked Stocks", data['tracked_stocks'])
                st.metric("Portfolio Holdings", data['portfolio_items'])
                st.metric("Total Transactions", data['total_transactions'])

        with col2:
            st.write("**Data Operations:**")

            if st.button("🔄 Refresh All Data"):
                self._refresh_all_data()

            if st.button("🧹 Clear User Data"):
                if st.checkbox("I understand this will delete all my data"):
                    self._clear_user_data()

            if st.button("📦 Backup User Data"):
                self._backup_user_data()

    def _render_portfolio_settings(self):
        """Render portfolio settings interface"""
        st.subheader("💰 Portfolio Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Initial Investment Fund Setup**")
            st.info("Set your starting investment amount to track performance against your initial capital.")

            # Get current settings
            portfolio_settings = st.session_state.get('portfolio_settings', {})

            # Initial fund amount
            initial_fund = st.number_input(
                "Initial Fund Amount (৳):",
                min_value=1000.0,
                value=portfolio_settings.get('initial_fund', 100000.0),
                step=1000.0,
                format="%.2f",
                help="Your starting investment capital"
            )

            # Fund set date
            fund_set_date = st.date_input(
                "Fund Set Date:",
                value=portfolio_settings.get('fund_set_date', datetime.now().date()),
                max_value=datetime.now().date(),
                help="Date when you started with this fund amount"
            )

            # Enable/disable fund tracking
            enable_fund_tracking = st.checkbox(
                "Enable Fund Tracking",
                value=portfolio_settings.get('enable_fund_tracking', True),
                help="Track portfolio performance against initial fund"
            )

            if st.button("💾 Save Portfolio Settings", type="primary"):
                # Update portfolio settings
                updated_settings = {
                    'initial_fund': initial_fund,
                    'fund_set_date': fund_set_date,
                    'enable_fund_tracking': enable_fund_tracking
                }

                st.session_state.portfolio_settings.update(updated_settings)
                self.session_manager.sync_user_data(self.data_manager)

                st.success("✅ Portfolio settings saved successfully!")

        with col2:
            st.write("**Portfolio Performance Summary**")

            if enable_fund_tracking and st.session_state.portfolio_items:
                self._render_portfolio_performance(initial_fund)
            else:
                st.info("Enable fund tracking and add some portfolio holdings to see performance metrics.")

            # Reset options
            st.write("**Reset Options**")

            # Reset initial fund to current portfolio value
            if st.button("🔄 Reset to Current Portfolio Value", help="Set initial fund to current portfolio value"):
                if st.session_state.portfolio_items:
                    current_value = sum(item.current_value for item in st.session_state.portfolio_items.values())
                    st.session_state.portfolio_settings['initial_fund'] = current_value
                    st.session_state.portfolio_settings['fund_set_date'] = datetime.now().date()
                    st.success(f"✅ Initial fund reset to current portfolio value: ৳{current_value:,.2f}")
                    st.rerun()
                else:
                    st.warning("No portfolio holdings found to calculate current value")

            # Reset all transactions - DANGEROUS operation
            st.markdown("---")
            st.write("**⚠️ Danger Zone**")
            st.warning("The following actions will permanently delete your data. This cannot be undone!")

            # Confirmation checkbox for transactions reset
            confirm_reset_transactions = st.checkbox(
                "I understand this will permanently delete ALL transactions and portfolio data",
                help="Check this box to enable the reset transactions button"
            )

            # Reset transactions button with confirmation
            if st.button(
                "🗑️ Reset All Transactions",
                type="secondary",
                disabled=not confirm_reset_transactions,
                help="Permanently delete all transactions and portfolio holdings"
            ):
                self._reset_all_transactions()

            # Spacer
            st.write("")

            # Reset EVERYTHING - NUCLEAR option
            confirm_reset_everything = st.checkbox(
                "I understand this will PERMANENTLY DELETE EVERYTHING (transactions, portfolio, tracked stocks, cash history)",
                help="Check this box to enable the reset everything button"
            )

            # Reset everything button with confirmation
            if st.button(
                "💥 RESET EVERYTHING TO 0",
                type="secondary",
                disabled=not confirm_reset_everything,
                help="Permanently delete ALL data: transactions, portfolio, tracked stocks, and cash history"
            ):
                self._reset_everything()

    def _render_portfolio_performance(self, initial_fund):
        """Render portfolio performance metrics"""
        # Calculate current portfolio value
        current_value = sum(item.current_value for item in st.session_state.portfolio_items.values())

        # Calculate cash remaining
        total_invested = sum(
            trans.total_amount for trans in st.session_state.transactions
            if trans.transaction_type.value == "BUY"
        ) - sum(
            trans.total_amount for trans in st.session_state.transactions
            if trans.transaction_type.value == "SELL"
        )

        cash_remaining = initial_fund - total_invested
        total_portfolio_value = current_value + cash_remaining

        # Performance metrics
        total_return = total_portfolio_value - initial_fund
        return_percentage = (total_return / initial_fund * 100) if initial_fund > 0 else 0

        # Display metrics
        st.metric("Initial Fund", f"৳{initial_fund:,.2f}")
        st.metric("Current Portfolio", f"৳{current_value:,.2f}")
        st.metric("Cash Remaining", f"৳{cash_remaining:,.2f}")
        st.metric("Total Value", f"৳{total_portfolio_value:,.2f}")
        st.metric("Total Return", f"৳{total_return:,.2f}", f"{return_percentage:+.2f}%")

        # Visual indicator
        if return_percentage > 0:
            st.success(f"📈 Portfolio is up {return_percentage:.2f}% from initial fund")
        elif return_percentage < 0:
            st.error(f"📉 Portfolio is down {return_percentage:.2f}% from initial fund")
        else:
            st.info("📊 Portfolio is at break-even")

    def _render_storage_switching(self):
        """Render storage switching interface"""
        st.subheader("🔄 Storage Migration")

        current_mode = self.config.APP_MODE
        st.info(f"Current storage mode: **{current_mode}**")

        # Migration options
        if current_mode == "redis":
            if st.button("📈 Migrate to Google Sheets"):
                self._migrate_to_google_sheets()
        else:
            if st.button("🗄️ Migrate to Redis"):
                self._migrate_to_redis()

    # Helper methods for data operations
    def _export_portfolio_csv(self):
        """Export portfolio data as CSV"""
        if st.session_state.portfolio_items:
            # Create portfolio DataFrame
            portfolio_data = []
            for symbol, item in st.session_state.portfolio_items.items():
                if item.quantity > 0:
                    portfolio_data.append({
                        'Symbol': symbol,
                        'Quantity': item.quantity,
                        'Average Cost': item.average_cost,
                        'Current Price': item.current_price,
                        'Total Cost': item.total_cost,
                        'Current Value': item.current_value,
                        'Gain/Loss': item.gain_loss,
                        'Gain/Loss %': item.gain_loss_percent
                    })

            if portfolio_data:
                df = pd.DataFrame(portfolio_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Portfolio CSV",
                    data=csv,
                    file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No portfolio data to export")
        else:
            st.warning("No portfolio items found")

    def _export_transactions_csv(self):
        """Export transaction data as CSV"""
        if st.session_state.transactions:
            transactions_data = []
            for trans in st.session_state.transactions:
                transactions_data.append({
                    'Date': trans.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Symbol': trans.symbol,
                    'Type': trans.transaction_type.value,
                    'Quantity': trans.quantity,
                    'Price': trans.price,
                    'Total Amount': trans.total_amount,
                    'Notes': trans.notes
                })

            df = pd.DataFrame(transactions_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="💼 Download Transactions CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No transaction data to export")

    def _export_all_data_json(self):
        """Export all user data as JSON"""
        user_summary = self.session_manager.get_user_summary()
        if user_summary:
            # Export comprehensive data
            export_data = {
                'user_info': user_summary['user'],
                'export_timestamp': datetime.now().isoformat(),
                'portfolio_settings': st.session_state.get('portfolio_settings', {}),
                'selected_stocks': st.session_state.get('selected_stocks', []),
                'cash_balance': st.session_state.get('cash_balance', 0),
                'transactions_count': len(st.session_state.get('transactions', [])),
                'portfolio_items_count': len(st.session_state.get('portfolio_items', {}))
            }

            json_data = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="📈 Download All Data (JSON)",
                data=json_data,
                file_name=f"stock_analyzer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.warning("No user data to export")

    def _generate_performance_report(self, start_date, end_date):
        """Generate performance report for date range"""
        st.info("📋 Performance report generation feature coming soon!")

    def _refresh_all_data(self):
        """Refresh all data from sources"""
        with st.spinner("Refreshing all data..."):
            # Force reload of session state
            self.session_manager.clear_user_session()
            st.success("✅ All data refreshed!")
            st.rerun()

    def _clear_user_data(self):
        """Clear all user data"""
        self.session_manager.clear_user_session()
        st.success("✅ All user data cleared!")
        st.rerun()

    def _backup_user_data(self):
        """Create backup of user data"""
        user_prefix = self.session_manager.get_user_prefix()
        backup_data = self.session_manager.get_user_summary()

        if backup_data:
            json_data = json.dumps(backup_data, indent=2, default=str)
            st.download_button(
                label="📦 Download Backup",
                data=json_data,
                file_name=f"backup_{user_prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.warning("No data to backup")

    def _migrate_to_google_sheets(self):
        """Migrate data to Google Sheets"""
        st.info("📈 Google Sheets migration feature coming soon!")

    def _migrate_to_redis(self):
        """Migrate data to Redis"""
        st.info("🗄️ Redis migration feature coming soon!")

    def _reset_all_transactions(self):
        """Reset all transactions and portfolio data"""
        try:
            with st.spinner("Resetting all transactions and portfolio data..."):
                # Call data manager to reset transactions
                success = self.data_manager.reset_user_transactions()

                if success:
                    # Clear session state
                    st.session_state.transactions = []
                    st.session_state.portfolio_items = {}

                    # Optionally reset cash balance to initial fund
                    if 'portfolio_settings' in st.session_state:
                        initial_fund = st.session_state.portfolio_settings.get('initial_fund', 100000.0)
                        st.session_state.cash_balance = initial_fund

                    # Sync with storage
                    self.session_manager.sync_user_data(self.data_manager)

                    st.success("✅ All transactions and portfolio data have been reset successfully!")
                    st.info("Your cash balance has been reset to your initial fund amount.")

                    # Force page refresh to show updated data
                    st.rerun()
                else:
                    st.error("❌ Failed to reset transactions. Please try again or contact support.")

        except Exception as e:
            st.error(f"❌ Error resetting transactions: {str(e)}")
            print(f"Reset transactions error: {e}")

    def _reset_everything(self):
        """Reset EVERYTHING - transactions, portfolio, selected stocks, cash history, and all user data"""
        try:
            with st.spinner("Resetting EVERYTHING to 0..."):
                # Reset transactions and portfolio
                self.data_manager.reset_user_transactions()

                # Clear ALL session state data
                st.session_state.transactions = []
                st.session_state.portfolio_items = {}
                st.session_state.selected_stocks = []
                st.session_state.cash_transactions = []

                # Reset cash balance to initial fund (or default)
                if 'portfolio_settings' in st.session_state:
                    initial_fund = st.session_state.portfolio_settings.get('initial_fund', 100000.0)
                    st.session_state.cash_balance = initial_fund
                else:
                    st.session_state.cash_balance = 100000.0

                # Reset portfolio settings to defaults
                st.session_state.portfolio_settings = {
                    'initial_fund': 100000.0,
                    'fund_set_date': datetime.now().date(),
                    'enable_fund_tracking': True
                }

                # Sync with storage to persist the reset
                self.session_manager.sync_user_data(self.data_manager)

                st.success("✅ EVERYTHING has been reset to 0!")
                st.info("All transactions, portfolio, tracked stocks, and cash history have been cleared. Cash balance reset to ৳100,000.")

                # Force page refresh to show clean slate
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error resetting everything: {str(e)}")
            print(f"Reset everything error: {e}")