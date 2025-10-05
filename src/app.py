"""
Stock Market Analyzer - Main Application (Modular Version)
Clean, modular architecture with separated concerns
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core services
from config import Config
from src.services.dse_api import DSEAPIService
from src.services.auth_service import AuthService
from src.services.session_manager import SessionManager
from src.services.data_loader import DataLoader
from src.services.data_manager import DataManager
from src.services.settings_manager import SettingsManager

# UI components
from src.ui.landing_page import LandingPageUI
from src.ui.profile import ProfileUI
from src.ui.dashboard import DashboardUI
from src.ui.stock_selector import StockSelectorUI
from src.ui.portfolio import PortfolioUI
from src.ui.transactions import TransactionsUI
from src.ui.setup_wizard import SetupWizardUI
from src.ui.price_tracker import PriceTrackerUI
from src.ui.dse_finance import DSEFinanceUI


class StockMarketApp:
    """
    Main application class - Now clean and modular!

    Responsibilities:
    - Application initialization
    - Service coordination
    - Page routing
    - Main UI layout
    """

    def __init__(self):
        """Initialize the application with all required services"""
        # Core configuration
        self.config = Config()

        # Initialize services
        self._initialize_services()

        # Initialize UI components
        self._initialize_ui_components()

    def _initialize_services(self):
        """Initialize all application services"""
        # Authentication service (must be first)
        self.auth_service = AuthService()

        # Data services
        self.dse_api = DSEAPIService()
        self.data_manager = DataManager()
        self.data_loader = DataLoader(self.config, self.data_manager, self.dse_api)

        # Session management (with data_manager for token storage)
        self.session_manager = SessionManager(self.auth_service, self.data_manager)

        # Settings management
        self.settings_manager = SettingsManager(self.config, self.data_manager, self.session_manager)

    def _initialize_ui_components(self):
        """Initialize all UI components"""
        self.landing_page_ui = LandingPageUI(self.auth_service)
        self.profile_ui = ProfileUI(self.auth_service)
        self.setup_wizard_ui = SetupWizardUI()
        self.dashboard_ui = DashboardUI(self.dse_api, self.data_manager)
        self.stock_selector_ui = StockSelectorUI(self.dse_api, self.data_manager)
        self.portfolio_ui = PortfolioUI(self.dse_api, self.data_manager)
        self.transactions_ui = TransactionsUI(self.dse_api, self.data_manager)
        self.price_tracker_ui = PriceTrackerUI(self.dse_api, self.data_manager)
        self.dse_finance_ui = DSEFinanceUI()

    def run(self):
        """Main application runner"""
        # Handle authentication first
        if not self._handle_authentication():
            return

        # Check configuration
        if not self._is_configured():
            self.setup_wizard_ui.render()
            return

        # Initialize global session state
        self.session_manager.initialize_global_session(self.config)

        # Render main application
        self._render_main_app()

    def _handle_authentication(self):
        """Handle user authentication"""
        name, authentication_status, username = self.auth_service.login()

        if authentication_status == False:
            st.error('❌ Username/password is incorrect')
            self.landing_page_ui.render()
            return False
        elif authentication_status == None:
            # Show landing page for non-authenticated users
            self.landing_page_ui.render()
            self.auth_service.render_registration_form()
            return False
        elif authentication_status:
            # User authenticated - initialize their session
            self.session_manager.initialize_user_session(self.data_loader)
            return True

        return False

    def _show_demo_credentials(self):
        """Show demo credentials for easy access"""
        st.info("🚀 **Demo Credentials** - Try these accounts:")

        demo_creds = self.auth_service.get_demo_credentials()

        cols = st.columns(2)
        for i, (name, creds) in enumerate(demo_creds.items()):
            with cols[i % 2]:
                st.markdown(f"""
                **{name}:**
                - Username: `{creds['username']}`
                - Password: `{creds['password']}`
                """)

        st.markdown("---")
        st.markdown("💡 **Each user gets their own separate portfolio and transactions!**")

    def _is_configured(self):
        """Check if the application is properly configured"""
        return self.data_loader.is_configured()

    def _render_main_app(self):
        """Render the main application interface"""
        # Top bar with user info
        self._render_top_bar()

        # Sidebar with navigation
        self._render_sidebar()

        # Main content area
        page = st.session_state.get('current_page', 'Dashboard')
        self._render_page_content(page)

    def _render_top_bar(self):
        """Render beautiful top bar with user info"""
        # Get user info
        username = st.session_state.get('username', 'User')
        name = st.session_state.get('name', 'User')

        # Try to get actual name from config
        try:
            import yaml
            from pathlib import Path
            config_path = Path("config/auth_config.yaml")
            with open(config_path) as file:
                config = yaml.load(file, yaml.SafeLoader)
            user_data = config['credentials']['usernames'].get(username, {})
            name = user_data.get('name', name)
        except:
            pass

        # Create top bar with custom CSS
        st.markdown("""
        <style>
        .top-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)

        # Top bar layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("# 📈 Stock Market Analyzer")

        with col2:
            st.markdown(f"### 👤 Welcome, {name}")

        st.markdown("---")

    def _render_sidebar(self):
        """Render the application sidebar"""
        with st.sidebar:
            st.title("🧭 Navigation")

            # Navigation
            page = st.selectbox(
                "Go to:",
                ["Dashboard", "Profile", "Stock Selector", "Portfolio", "Transactions", "Price Tracker", "DSE Finance", "Settings"],
                index=0,
                key="current_page",
                label_visibility="collapsed"
            )

            st.markdown("---")

            # Logout button
            if st.button("🚪 Logout", key="logout_btn", use_container_width=True, type="primary"):
                self.auth_service.logout()

            st.markdown("---")

            # User summary
            self._render_user_summary()

            st.markdown("---")

            # Quick stats
            self._render_quick_stats()

    def _render_user_summary(self):
        """Render user summary in sidebar"""
        summary = self.session_manager.get_user_summary()

        if summary and summary.get('data'):
            user_info = summary['user']
            data = summary['data']

            st.subheader(f"👤 {user_info['name']}")

            # Quick metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Cash", f"৳{data['cash_balance']:,.0f}")
                st.metric("📊 Stocks", data['tracked_stocks'])
            with col2:
                st.metric("📈 Value", f"৳{data['portfolio_value']:,.0f}")
                st.metric("💼 Holdings", data['portfolio_items'])

    def _render_quick_stats(self):
        """Render quick statistics"""
        if st.session_state.get('selected_stocks'):
            st.subheader("📊 Tracked Stocks")
            for symbol in st.session_state.selected_stocks[:5]:
                st.write(f"• {symbol}")
            if len(st.session_state.selected_stocks) > 5:
                st.write(f"... and {len(st.session_state.selected_stocks) - 5} more")

    def _render_page_content(self, page: str):
        """Render the main page content based on selection"""
        try:
            if page == "Dashboard":
                self.dashboard_ui.render()
            elif page == "Profile":
                self.profile_ui.render()
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
                self.settings_manager.render_settings_page()
            else:
                st.error(f"Unknown page: {page}")

            # Auto-sync user data after page rendering to ensure persistence
            try:
                self.session_manager.sync_user_data(self.data_manager)
            except Exception as sync_error:
                print(f"Auto-sync error: {sync_error}")

        except Exception as e:
            st.error(f"Error rendering {page}: {e}")
            st.exception(e)

    def get_app_info(self):
        """Get application information"""
        return {
            'version': '2.0.0',
            'architecture': 'Modular',
            'components': {
                'services': [
                    'AuthService', 'SessionManager', 'DataLoader',
                    'DataManager', 'SettingsManager', 'DSEAPIService'
                ],
                'ui_components': [
                    'DashboardUI', 'StockSelectorUI', 'PortfolioUI',
                    'TransactionsUI', 'PriceTrackerUI', 'DSEFinanceUI'
                ]
            },
            'features': [
                'Multi-user authentication',
                'User-specific data isolation',
                'Modular architecture',
                'Clean separation of concerns',
                'Comprehensive settings management'
            ]
        }


# For backward compatibility
class StockMarketAppLegacy:
    """Legacy app class - redirects to modular version"""

    def __init__(self):
        st.warning("⚠️ Using legacy app class. Consider upgrading to StockMarketApp.")
        self.app = StockMarketApp()

    def run(self):
        return self.app.run()


def main():
    """Main function for standalone execution"""
    app = StockMarketApp()
    app.run()


if __name__ == "__main__":
    main()