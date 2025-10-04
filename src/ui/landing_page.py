"""
Landing Page for Stock Market Analyzer
Displays when user is not logged in
"""

import streamlit as st


class LandingPageUI:
    """Landing page UI for non-authenticated users"""

    def __init__(self, auth_service):
        self.auth_service = auth_service

    def render(self):
        """Render the landing page"""

        # Header
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #1f77b4; font-size: 3rem;">📈 Stock Market Analyzer</h1>
            <h3 style="color: #666; font-weight: 300;">Dhaka Stock Exchange Portfolio Management System</h3>
        </div>
        """, unsafe_allow_html=True)

        # Main content
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("---")

            # Features section
            st.markdown("""
            ### ✨ Key Features

            - 📊 **Real-time Stock Tracking** - Monitor DSE stocks with live price updates
            - 💼 **Portfolio Management** - Track your investments and performance
            - 💰 **Transaction Recording** - Keep detailed records of all your trades
            - 📈 **Professional Reports** - Generate comprehensive portfolio reports
            - 🔒 **Secure & Private** - Your data is protected with authentication
            - ☁️ **Cloud Sync** - Access your portfolio from anywhere

            ---

            ### 🚀 Get Started

            Please **login** to access your portfolio or **sign up** to create a new account.
            """)

            # Login section
            st.markdown("### 🔐 Login")

            # Demo credentials info
            with st.expander("📋 Demo Credentials (Click to view)"):
                demo_creds = self.auth_service.get_demo_credentials()
                st.markdown("**Available Demo Accounts:**")
                for name, creds in demo_creds.items():
                    st.markdown(f"- **{name}** - Username: `{creds['username']}` | Password: `{creds['password']}`")

            st.markdown("---")

            # Footer
            st.markdown("""
            <div style="text-align: center; color: #888; padding: 2rem 0; font-size: 0.9rem;">
                <p>🇧🇩 Designed for Dhaka Stock Exchange</p>
                <p>Powered by Streamlit | Real-time DSE Data</p>
            </div>
            """, unsafe_allow_html=True)
