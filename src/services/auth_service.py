"""
Authentication Service for Stock Market Analyzer
Handles user authentication and password management
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from pathlib import Path
import bcrypt


class AuthService:
    """Authentication service for the Stock Market Analyzer"""

    def __init__(self):
        self.config_path = Path("config/auth_config.yaml")
        self.authenticator = None
        self._initialize_auth()

    def _initialize_auth(self):
        """Initialize the authenticator"""
        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(exist_ok=True)

        # Create default config if it doesn't exist
        if not self.config_path.exists():
            self._create_default_config()

        # Load configuration
        with open(self.config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)

        # Initialize authenticator
        self.authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config.get('preauthorized', {})
        )

    def _create_default_config(self):
        """Create a default authentication configuration"""
        # Generate hashed passwords
        demo_password = stauth.Hasher(['demo123']).generate()[0]
        admin_password = stauth.Hasher(['admin123']).generate()[0]
        john_password = stauth.Hasher(['john123']).generate()[0]
        jane_password = stauth.Hasher(['jane123']).generate()[0]

        config = {
            'credentials': {
                'usernames': {
                    'demo_user': {
                        'email': 'demo@example.com',
                        'name': 'Demo User',
                        'password': demo_password
                    },
                    'admin': {
                        'email': 'admin@example.com',
                        'name': 'Administrator',
                        'password': admin_password
                    },
                    'john_doe': {
                        'email': 'john@example.com',
                        'name': 'John Doe',
                        'password': john_password
                    },
                    'jane_smith': {
                        'email': 'jane@example.com',
                        'name': 'Jane Smith',
                        'password': jane_password
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'stock_market_analyzer_key_2024',
                'name': 'stock_market_analyzer_cookie'
            },
            'preauthorized': {
                'emails': ['admin@example.com']
            }
        }

        with open(self.config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

    def login(self):
        """Handle user login"""
        name, authentication_status, username = self.authenticator.login()
        return name, authentication_status, username

    def perform_logout_cleanup(self, session_manager=None, data_manager=None):
        """Perform cleanup operations during logout"""
        try:
            # Save user data to Redis before logout
            if session_manager and data_manager:
                print("Saving user data before logout...")
                session_manager.sync_user_data(data_manager)

            # Clear user session after logout
            if session_manager:
                print("Clearing user session...")
                session_manager.clear_user_session()

            print("Logout cleanup completed successfully")
            return True

        except Exception as e:
            print(f"Logout cleanup error: {e}")
            return False

    def register_user(self):
        """Handle new user registration"""
        try:
            result = self.authenticator.register_user(location='main', key='Register user')
            if result:
                email, username, name = result
                st.success(f'User **{name}** registered successfully! Please login with your credentials.')
                # Save updated config
                self._save_config()
                return True
        except Exception as e:
            st.error(f"Registration error: {e}")
            return False

    def reset_password(self, username):
        """Handle password reset"""
        try:
            if self.authenticator.reset_password(username, location='main', key='Reset password'):
                st.success('Password modified successfully')
                # Save updated config
                self._save_config()
        except Exception as e:
            st.error(e)

    def update_user_details(self, username):
        """Handle updating user details"""
        try:
            result = self.authenticator.update_user_details(username, location='main', key='Update user details')
            if result:
                # Save updated config
                self._save_config()

                # Update session state with new name
                try:
                    import yaml
                    from pathlib import Path
                    config_path = Path("config/auth_config.yaml")
                    with open(config_path) as file:
                        config = yaml.load(file, yaml.SafeLoader)
                    user_data = config['credentials']['usernames'].get(username, {})
                    new_name = user_data.get('name')
                    if new_name:
                        st.session_state['name'] = new_name
                except:
                    pass

                st.success('Entries updated successfully! Refreshing...')
                st.rerun()
        except Exception as e:
            st.error(f"Update error: {e}")

    def _save_config(self):
        """Save the current configuration back to file"""
        config = {
            'credentials': self.authenticator.credentials,
            'cookie': {
                'expiry_days': 30,
                'key': 'stock_market_analyzer_key_2024',
                'name': 'stock_market_analyzer_cookie'
            },
            'preauthorized': {
                'emails': ['admin@example.com']
            }
        }

        with open(self.config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

    def get_current_user(self):
        """Get the current authenticated user"""
        return st.session_state.get('name'), st.session_state.get('username')

    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get('authentication_status') == True

    def get_user_session_prefix(self):
        """Get session prefix for current user"""
        username = st.session_state.get('username')
        if username:
            return f"user_{username}_"
        return "anonymous_"

    def show_login_info(self, session_manager=None, data_manager=None):
        """Show current login information in sidebar"""
        if self.is_authenticated():
            # Get name from config file for accuracy
            username = st.session_state.get('username')
            name = st.session_state.get('name', 'User')

            # Try to get the actual name from config
            try:
                import yaml
                from pathlib import Path
                config_path = Path("config/auth_config.yaml")
                with open(config_path) as file:
                    config = yaml.load(file, yaml.SafeLoader)
                user_data = config['credentials']['usernames'].get(username, {})
                actual_name = user_data.get('name', name)
                name = actual_name
            except:
                pass  # Fallback to session state name

            st.sidebar.success(f'Welcome **{name}**!')

            # Logout button
            st.markdown("---")
            if st.sidebar.button('🚪 Logout', key='logout_button', help='Click to logout and save your data', use_container_width=True):
                try:
                    # Save data first
                    if session_manager and data_manager:
                        with st.spinner("💾 Saving your data..."):
                            session_manager.sync_user_data(data_manager)

                    # Clear user session data
                    if session_manager:
                        session_manager.clear_user_session()

                    # Clear all session state variables
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]

                    # Force rerun to show landing page
                    st.success("✅ Logged out successfully!")
                    st.rerun()

                except Exception as e:
                    st.sidebar.error(f"❌ Logout error: {str(e)}")
                    # Emergency logout - clear everything
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

            # User management options
            with st.sidebar.expander("👤 Account Settings"):
                username = st.session_state.get('username')

                if st.button('🔐 Reset Password'):
                    self.reset_password(username)

                if st.button('📝 Update Details'):
                    self.update_user_details(username)
        else:
            st.sidebar.info('Please login to access the application')

    def render_registration_form(self):
        """Render user registration form"""
        st.subheader("👤 Create New Account")

        with st.expander("Register New User"):
            self.register_user()

    def get_demo_credentials(self):
        """Get demo credentials for display"""
        return {
            "Demo User": {"username": "demo_user", "password": "demo123"},
            "John Doe": {"username": "john_doe", "password": "john123"},
            "Jane Smith": {"username": "jane_smith", "password": "jane123"},
            "Admin": {"username": "admin", "password": "admin123"}
        }