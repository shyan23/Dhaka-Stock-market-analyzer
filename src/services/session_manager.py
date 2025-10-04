"""
Session State Manager for Stock Market Analyzer
Handles user-specific session state management with token-based sessions
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.models.portfolio import PortfolioItem, Transaction
from src.services.session_token import SessionToken, SessionTokenManager


class SessionManager:
    """Manages user-specific session state variables with token-based sessions"""

    def __init__(self, auth_service, data_manager=None):
        self.auth_service = auth_service
        self.data_manager = data_manager
        self.token_manager = SessionTokenManager(data_manager)

    def get_current_token(self) -> Optional[SessionToken]:
        """Get current session token"""
        # Check if token exists in session state
        if 'session_token' in st.session_state:
            token = st.session_state.session_token
            if isinstance(token, SessionToken) and token.is_valid():
                return token

        # Try to get/create token for current user
        username = st.session_state.get('username')
        if username:
            token = self.token_manager.get_or_create_session(username)
            st.session_state.session_token = token
            return token

        return None

    def get_user_prefix(self) -> str:
        """Get session prefix for current user (now uses token)"""
        token = self.get_current_token()
        if token:
            # Use session ID instead of username for better security
            session_id = token.get_session_id()
            return f"session_{session_id}_"

        # Fallback to old username-based prefix
        return self.auth_service.get_user_session_prefix()

    def initialize_user_session(self, data_loader):
        """Initialize user-specific session state variables"""
        user_prefix = self.get_user_prefix()
        print(f"Initializing session for user prefix: {user_prefix}")

        # User-specific session state keys
        keys = {
            'selected_stocks': f'{user_prefix}selected_stocks',
            'portfolio_items': f'{user_prefix}portfolio_items',
            'transactions': f'{user_prefix}transactions',
            'portfolio_settings': f'{user_prefix}portfolio_settings',
            'cash_balance': f'{user_prefix}cash_balance',
            'cash_transactions': f'{user_prefix}cash_transactions'
        }

        # Initialize user-specific data
        if keys['selected_stocks'] not in st.session_state:
            loaded_stocks = data_loader.load_selected_stocks()
            st.session_state[keys['selected_stocks']] = loaded_stocks
            print(f"Loaded {len(loaded_stocks)} stocks from Redis for user")

        if keys['portfolio_items'] not in st.session_state:
            st.session_state[keys['portfolio_items']] = data_loader.load_portfolio_items()

        if keys['transactions'] not in st.session_state:
            st.session_state[keys['transactions']] = data_loader.load_transactions()

        if keys['portfolio_settings'] not in st.session_state:
            st.session_state[keys['portfolio_settings']] = data_loader.load_portfolio_settings()

        if keys['cash_balance'] not in st.session_state:
            st.session_state[keys['cash_balance']] = st.session_state[keys['portfolio_settings']].get('initial_fund', 100000.0)

        if keys['cash_transactions'] not in st.session_state:
            st.session_state[keys['cash_transactions']] = []

        # Set aliases for backward compatibility
        st.session_state.selected_stocks = st.session_state[keys['selected_stocks']]
        st.session_state.portfolio_items = st.session_state[keys['portfolio_items']]
        st.session_state.transactions = st.session_state[keys['transactions']]
        st.session_state.portfolio_settings = st.session_state[keys['portfolio_settings']]
        st.session_state.cash_balance = st.session_state[keys['cash_balance']]
        st.session_state.cash_transactions = st.session_state[keys['cash_transactions']]

        print(f"Session aliases set - selected_stocks: {len(st.session_state.selected_stocks)} items")

        # Mark data as loaded
        if f'{user_prefix}data_loaded' not in st.session_state:
            st.session_state[f'{user_prefix}data_loaded'] = True

    def initialize_global_session(self, config):
        """Initialize global (non-user-specific) session state"""
        if 'app_mode' not in st.session_state:
            st.session_state.app_mode = config.APP_MODE

        if 'last_update' not in st.session_state:
            st.session_state.last_update = None

    def get_user_data(self, key: str) -> Any:
        """Get user-specific data from session state"""
        user_prefix = self.get_user_prefix()
        full_key = f'{user_prefix}{key}'
        return st.session_state.get(full_key)

    def set_user_data(self, key: str, value: Any):
        """Set user-specific data in session state"""
        user_prefix = self.get_user_prefix()
        full_key = f'{user_prefix}{key}'
        st.session_state[full_key] = value

        # Update alias if it exists
        if hasattr(st.session_state, key):
            setattr(st.session_state, key, value)

    def sync_user_data(self, data_manager=None):
        """Sync user data with aliased session state variables and save to Redis"""
        user_prefix = self.get_user_prefix()

        # Update user-specific storage with current aliases
        user_keys = [
            'selected_stocks', 'portfolio_items', 'transactions',
            'portfolio_settings', 'cash_balance', 'cash_transactions'
        ]

        for key in user_keys:
            if hasattr(st.session_state, key):
                full_key = f'{user_prefix}{key}'
                st.session_state[full_key] = getattr(st.session_state, key)

        # If data_manager is provided, save to Redis
        if data_manager:
            try:
                if hasattr(st.session_state, 'selected_stocks'):
                    data_manager.save_user_selected_stocks(st.session_state.selected_stocks)
                if hasattr(st.session_state, 'portfolio_items'):
                    data_manager.save_user_portfolio_items(st.session_state.portfolio_items)
                if hasattr(st.session_state, 'transactions'):
                    data_manager.save_user_transactions(st.session_state.transactions)
                if hasattr(st.session_state, 'portfolio_settings'):
                    data_manager.save_user_portfolio_settings(st.session_state.portfolio_settings)
                if hasattr(st.session_state, 'cash_balance'):
                    data_manager.save_user_cash_balance(st.session_state.cash_balance)
            except Exception as e:
                print(f"Error syncing user data to Redis: {e}")

    def clear_user_session(self):
        """Clear user-specific session data (for logout) but preserve Redis data"""
        user_prefix = self.get_user_prefix()

        # Invalidate session token
        username = st.session_state.get('username')
        if username:
            self.token_manager.invalidate_session(username)

        # Clear session token from state
        if 'session_token' in st.session_state:
            del st.session_state['session_token']

        # Clear session state aliases (not the user-prefixed Redis keys)
        user_keys = [
            'selected_stocks', 'portfolio_items', 'transactions',
            'portfolio_settings', 'cash_balance', 'cash_transactions'
        ]

        for key in user_keys:
            if hasattr(st.session_state, key):
                delattr(st.session_state, key)

        # Also clear user-specific flags
        if f'{user_prefix}data_loaded' in st.session_state:
            del st.session_state[f'{user_prefix}data_loaded']

    def get_current_user_info(self) -> Dict[str, str]:
        """Get current user information"""
        name, username = self.auth_service.get_current_user()
        return {
            'name': name or 'Anonymous',
            'username': username or 'anonymous',
            'prefix': self.get_user_prefix()
        }

    def is_user_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.auth_service.is_authenticated()

    def get_user_summary(self) -> Dict[str, Any]:
        """Get summary of user's data"""
        if not self.is_user_authenticated():
            return {}

        user_info = self.get_current_user_info()

        # Add session token info
        token = self.get_current_token()
        if token:
            user_info['session_id'] = token.get_session_id()
            user_info['session_valid'] = token.is_valid()

        return {
            'user': user_info,
            'data': {
                'tracked_stocks': len(st.session_state.get('selected_stocks', [])),
                'portfolio_items': len([item for item in st.session_state.get('portfolio_items', {}).values() if item.quantity > 0]),
                'total_transactions': len(st.session_state.get('transactions', [])),
                'cash_balance': st.session_state.get('cash_balance', 0),
                'portfolio_value': sum(item.current_value for item in st.session_state.get('portfolio_items', {}).values() if item.quantity > 0)
            }
        }