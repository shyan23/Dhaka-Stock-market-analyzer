"""
Data Loader Service for Stock Market Analyzer
Handles loading and saving of user data
"""

import json
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from src.models.portfolio import PortfolioItem, Transaction, TransactionType


class DataLoader:
    """Handles data loading and saving operations"""

    def __init__(self, config, data_manager, dse_api):
        self.config = config
        self.data_manager = data_manager
        self.dse_api = dse_api

    def load_selected_stocks(self) -> List[str]:
        """Load selected stocks from persistent storage"""
        try:
            return self.data_manager.get_selected_stocks()
        except Exception as e:
            print(f"Error loading selected stocks: {e}")
        return []

    def load_portfolio_items(self) -> Dict[str, PortfolioItem]:
        """Load portfolio items from persistent storage"""
        try:
            portfolio_items = self.data_manager.get_portfolio_items()

            # Update current prices for each portfolio item
            for symbol, item in portfolio_items.items():
                stock = self.dse_api.get_stock_by_symbol(symbol)
                if stock:
                    item.current_price = stock.current_price

            return portfolio_items
        except Exception as e:
            print(f"Error loading portfolio items: {e}")
        return {}

    def load_transactions(self) -> List[Transaction]:
        """Load transactions from persistent storage"""
        try:
            return self.data_manager.get_transactions()
        except Exception as e:
            print(f"Error loading transactions: {e}")
        return []

    def load_portfolio_settings(self) -> Dict[str, Any]:
        """Load portfolio settings from persistent storage"""
        try:
            if self.config.APP_MODE == "redis" and self.data_manager.redis_client:
                settings_data = self.data_manager.redis_client.get("app:portfolio_settings")
                if settings_data:
                    settings = json.loads(settings_data)
                    # Convert string dates back to date objects
                    if 'fund_set_date' in settings and isinstance(settings['fund_set_date'], str):
                        settings['fund_set_date'] = datetime.strptime(settings['fund_set_date'], '%Y-%m-%d').date()
                    return settings
        except Exception as e:
            print(f"Error loading portfolio settings: {e}")

        # Return default settings
        return {
            'initial_fund': 100000.0,  # Default ৳1,00,000
            'fund_set_date': datetime.now().date(),
            'enable_fund_tracking': True
        }

    def save_selected_stocks(self, stocks: List[str]):
        """Save selected stocks to persistent storage"""
        try:
            if self.config.APP_MODE == "redis" and self.data_manager.redis_client:
                data = json.dumps(stocks)
                self.data_manager.redis_client.set("app:selected_stocks", data)
        except Exception as e:
            print(f"Error saving selected stocks: {e}")

    def save_transaction(self, transaction: Transaction) -> bool:
        """Save a transaction to persistent storage"""
        try:
            return self.data_manager.save_transaction(transaction)
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False

    def save_portfolio_settings(self, settings: Dict[str, Any]):
        """Save portfolio settings to persistent storage"""
        try:
            settings_data = json.dumps(settings, default=str)
            if self.config.APP_MODE == "redis" and self.data_manager.redis_client:
                self.data_manager.redis_client.set("app:portfolio_settings", settings_data)
            elif self.config.APP_MODE == "google_sheets":
                # Could save to Google Sheets if needed
                pass
        except Exception as e:
            print(f"Error saving portfolio settings: {e}")

    def load_installer_config(self) -> Dict[str, Any]:
        """Load configuration from installer if available"""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading installer config: {e}")
        return {}

    def get_storage_preference_from_redis(self) -> str:
        """Get storage preference from Redis if available"""
        try:
            import redis

            # Use a temporary config to connect to Redis
            redis_client = redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                password=self.config.REDIS_PASSWORD if self.config.REDIS_PASSWORD else None,
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

    def is_configured(self) -> bool:
        """Check if the application is properly configured"""
        # Check if we have a basic configuration
        if self.config.APP_MODE == "google_sheets":
            # Check if Google Sheets credentials are available
            return bool(self.config.GOOGLE_CREDENTIALS_FILE and self.config.GOOGLE_SHEET_ID)
        elif self.config.APP_MODE == "redis":
            # Redis configuration is usually simpler
            return True
        else:
            # Default configuration is always available
            return True

    def export_user_data(self, user_prefix: str) -> Dict[str, Any]:
        """Export all user data for backup or migration"""
        import streamlit as st

        user_data = {}

        # Export user-specific session data
        for key in st.session_state.keys():
            if key.startswith(user_prefix):
                user_data[key] = st.session_state[key]

        # Add metadata
        user_data['_metadata'] = {
            'export_date': datetime.now().isoformat(),
            'user_prefix': user_prefix,
            'app_version': '1.0.0'
        }

        return user_data

    def import_user_data(self, user_data: Dict[str, Any], user_prefix: str):
        """Import user data from backup"""
        import streamlit as st

        try:
            # Import user-specific data
            for key, value in user_data.items():
                if key.startswith(user_prefix) and key != '_metadata':
                    st.session_state[key] = value

            print(f"Successfully imported data for user prefix: {user_prefix}")
            return True

        except Exception as e:
            print(f"Error importing user data: {e}")
            return False