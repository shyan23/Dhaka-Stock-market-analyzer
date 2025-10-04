"""
Reset Component for Stock Market Analyzer
Provides reusable reset functionality for transactions and portfolio data
"""

import streamlit as st
from typing import Optional


class ResetTransactionsComponent:
    """Reusable component for resetting transactions and portfolio data"""

    def __init__(self, data_manager, session_manager):
        self.data_manager = data_manager
        self.session_manager = session_manager

    def render(self,
               title: str = "Reset All Data",
               location: str = "page",
               compact: bool = False,
               button_key: Optional[str] = None):
        """
        Render the reset transactions component

        Args:
            title: Title for the reset section
            location: Where this component is being used ('page', 'sidebar', etc.)
            compact: Whether to use a compact layout
            button_key: Unique key for the button to avoid conflicts
        """
        if compact:
            self._render_compact_reset(title, button_key)
        else:
            self._render_full_reset(title, location, button_key)

    def _render_compact_reset(self, title: str, button_key: Optional[str]):
        """Render compact version for inline use"""
        with st.expander("🗑️ Reset All Data", expanded=False):
            st.warning("⚠️ This will permanently delete all transactions and portfolio holdings!")

            col1, col2 = st.columns(2)
            with col1:
                confirm_key = f"confirm_reset_{button_key}" if button_key else "confirm_reset_compact"
                confirm_reset = st.checkbox(
                    "I understand",
                    key=confirm_key,
                    help="Check to enable reset button"
                )

            with col2:
                reset_key = f"reset_btn_{button_key}" if button_key else "reset_btn_compact"
                if st.button(
                    "🗑️ Reset",
                    type="secondary",
                    disabled=not confirm_reset,
                    key=reset_key,
                    help="Permanently delete all data"
                ):
                    self._execute_reset()

    def _render_full_reset(self, title: str, location: str, button_key: Optional[str]):
        """Render full version with detailed warnings"""
        st.markdown("---")
        st.subheader(f"🗑️ {title}")

        # Warning section
        st.warning(
            "⚠️ **Warning**: This action will permanently delete ALL your transaction history "
            "and portfolio holdings. This cannot be undone!"
        )

        # Information about what gets reset
        with st.expander("ℹ️ What will be reset?", expanded=False):
            st.markdown("""
            **Will be deleted:**
            - ✅ All transaction records (buy/sell orders)
            - ✅ All portfolio holdings and positions
            - ✅ Current portfolio values and P&L data

            **Will be preserved:**
            - ❌ Your account settings and preferences
            - ❌ Your selected stocks watchlist
            - ❌ Portfolio settings (initial fund, dates)
            - ❌ Cash balance (will reset to initial fund amount)
            """)

        # Confirmation section
        col1, col2 = st.columns([3, 1])

        with col1:
            confirm_key = f"confirm_reset_{button_key}" if button_key else f"confirm_reset_{location}"
            confirm_reset = st.checkbox(
                "I understand this will permanently delete ALL transactions and portfolio data",
                key=confirm_key,
                help="You must check this box to enable the reset button"
            )

        with col2:
            reset_key = f"reset_all_btn_{button_key}" if button_key else f"reset_all_btn_{location}"
            if st.button(
                "🗑️ Reset All Data",
                type="secondary",
                disabled=not confirm_reset,
                key=reset_key,
                help="Permanently delete all transactions and portfolio data"
            ):
                self._execute_reset()

    def _execute_reset(self):
        """Execute the reset operation"""
        try:
            with st.spinner("Resetting all transactions and portfolio data..."):
                # Call data manager to reset transactions
                success = self.data_manager.reset_user_transactions()

                if success:
                    # Clear session state
                    st.session_state.transactions = []
                    st.session_state.portfolio_items = {}

                    # Reset cash balance to initial fund
                    if 'portfolio_settings' in st.session_state:
                        initial_fund = st.session_state.portfolio_settings.get('initial_fund', 100000.0)
                        st.session_state.cash_balance = initial_fund

                    # Sync with storage
                    if self.session_manager:
                        self.session_manager.sync_user_data(self.data_manager)

                    st.success("✅ All transactions and portfolio data have been reset successfully!")
                    st.info("💰 Your cash balance has been reset to your initial fund amount.")

                    # Small delay before rerun to show success message
                    import time
                    time.sleep(1)

                    # Force page refresh to show updated data
                    st.rerun()
                else:
                    st.error("❌ Failed to reset transactions. Please try again or contact support.")

        except Exception as e:
            st.error(f"❌ Error resetting transactions: {str(e)}")
            print(f"Reset transactions error: {e}")


def create_reset_component(data_manager, session_manager=None):
    """Factory function to create a reset component"""
    return ResetTransactionsComponent(data_manager, session_manager)