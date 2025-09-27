"""
Session State Manager for Stock Market Analyzer
Handles user-specific session state management
"""

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime
from src.models.portfolio import PortfolioItem, Transaction


class SessionManager:
    """Manages user-specific session state variables"""

    def __init__(self, auth_service):
        self.auth_service = auth_service

    def get_user_prefix(self) -> str:
        """Get session prefix for current user"""
        return self.auth_service.get_user_session_prefix()

    def initialize_user_session(self, data_loader):
        """Initialize user-specific session state variables"""
        user_prefix = self.get_user_prefix()

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
            st.session_state[keys['selected_stocks']] = data_loader.load_selected_stocks()

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

    def sync_user_data(self):
        """Sync user data with aliased session state variables"""
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

    def clear_user_session(self):
        """Clear user-specific session data (for logout)"""
        user_prefix = self.get_user_prefix()

        # Find and remove all user-specific keys
        keys_to_remove = [
            key for key in st.session_state.keys()
            if key.startswith(user_prefix)
        ]

        for key in keys_to_remove:
            del st.session_state[key]

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