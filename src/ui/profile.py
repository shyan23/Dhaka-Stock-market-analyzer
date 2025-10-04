"""
User Profile Page
Displays user account information and settings
"""

import streamlit as st
import yaml
from pathlib import Path


class ProfileUI:
    """Profile page UI for displaying user information"""

    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.config_path = Path("config/auth_config.yaml")

    def _get_user_info(self, username):
        """Get user information from config"""
        try:
            with open(self.config_path) as file:
                config = yaml.load(file, yaml.SafeLoader)

            user_data = config['credentials']['usernames'].get(username, {})
            return user_data
        except Exception as e:
            st.error(f"Error loading user data: {e}")
            return {}

    def render(self):
        """Render the profile page"""
        st.title("👤 User Profile")

        # Get current user
        username = st.session_state.get('username')
        session_name = st.session_state.get('name')

        if not username:
            st.error("No user logged in")
            return

        # Get user info from config
        user_info = self._get_user_info(username)

        # Profile Header
        st.markdown("---")
        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 80px;">👤</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"### {user_info.get('name', session_name or 'User')}")
            st.markdown(f"**@{username}**")
            st.caption("Account Information")

        st.markdown("---")

        # Account Details Section
        st.subheader("📋 Account Details")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Personal Information")
            st.markdown(f"**Full Name:** {user_info.get('name', 'N/A')}")
            st.markdown(f"**Email:** {user_info.get('email', 'N/A')}")
            st.markdown(f"**Username:** {username}")

        with col2:
            st.markdown("#### Session Information")
            st.markdown(f"**Session Name:** {session_name or 'N/A'}")
            st.markdown(f"**Authentication Status:** ✅ Authenticated")

            # Show session token info if available
            if 'session_token' in st.session_state:
                from src.services.session_token import SessionToken
                token = st.session_state.session_token
                if isinstance(token, SessionToken):
                    st.markdown(f"**Session ID:** `{token.get_session_id()[:16]}...`")
                    st.markdown(f"**Token Valid:** {'✅ Yes' if token.is_valid() else '❌ No'}")
            else:
                st.markdown(f"**Session Type:** Legacy (username-based)")

        st.markdown("---")

        # Account Statistics
        st.subheader("📊 Account Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            tracked = len(st.session_state.get('selected_stocks', []))
            st.metric("Tracked Stocks", tracked)

        with col2:
            portfolio = len(st.session_state.get('portfolio_items', {}))
            st.metric("Portfolio Items", portfolio)

        with col3:
            transactions = len(st.session_state.get('transactions', []))
            st.metric("Total Transactions", transactions)

        with col4:
            cash = st.session_state.get('cash_balance', 0.0)
            st.metric("Cash Balance", f"৳{cash:,.0f}")

        st.markdown("---")

        # Debug Information (Expandable)
        with st.expander("🔍 Debug Information"):
            st.markdown("#### Session State Keys")
            auth_keys = {
                'username': st.session_state.get('username'),
                'name': st.session_state.get('name'),
                'authentication_status': st.session_state.get('authentication_status'),
            }
            st.json(auth_keys)

            st.markdown("#### Session Token Details")
            if 'session_token' in st.session_state:
                from src.services.session_token import SessionToken
                token = st.session_state.session_token
                if isinstance(token, SessionToken):
                    st.json(token.to_dict())
                else:
                    st.write("Session token exists but is not valid SessionToken object")
            else:
                st.write("No session token found (using legacy username-based sessions)")

            st.markdown("#### Full User Config")
            st.json(user_info)

            st.markdown("#### All Session Keys")
            st.write(list(st.session_state.keys()))

        st.markdown("---")

        # Account Management Actions
        st.subheader("⚙️ Account Management")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔐 Reset Password", use_container_width=True):
                st.info("Password reset form will appear below")
                self.auth_service.reset_password(username)

        with col2:
            if st.button("📝 Update Details", use_container_width=True):
                st.info("Update details form will appear below")
                self.auth_service.update_user_details(username)

        with col3:
            if st.button("🔄 Refresh Profile", use_container_width=True):
                st.rerun()

        st.markdown("---")

        # Footer
        st.caption("💡 Your profile information is stored securely in the application configuration.")
