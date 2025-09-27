"""
DSE Finance UI Component
Clean and simple interface for DSE Finance functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go

from src.services.dse_finance import DSEFinanceService


class DSEFinanceUI:
    """
    UI Component for DSE Finance functionality
    Provides GOOGLEFINANCE-like interface for Dhaka Stock Exchange
    """

    def __init__(self):
        self.dse_finance = DSEFinanceService()

    def render(self):
        """Main render method for DSE Finance UI"""
        st.title("📊 DSE Finance - Market Data Tool")
        st.markdown("*Get real-time and historical data from Dhaka Stock Exchange*")

        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Quick Lookup",
            "📈 Historical Data",
            "📊 Market Overview",
            "📥 Bulk Export"
        ])

        with tab1:
            self._render_quick_lookup()

        with tab2:
            self._render_historical_data()

        with tab3:
            self._render_market_overview()

        with tab4:
            self._render_bulk_export()

    def _render_quick_lookup(self):
        """Render quick stock lookup interface"""
        st.subheader("🔍 Quick Stock Lookup")

        # Initialize search_results to avoid UnboundLocalError
        search_results = []

        col1, col2 = st.columns([2, 1])

        with col1:
            # Stock search
            search_query = st.text_input(
                "Search for stocks",
                placeholder="Enter stock symbol (e.g., GP, SQURPHARMA, BEXIMCO)",
                help="Start typing to search for DSE stocks"
            )

            if search_query:
                with st.spinner("Searching stocks..."):
                    search_results = self.dse_finance.search_stocks(search_query)

                if search_results:
                    st.write("**Search Results:**")

                    # Display search results in a nice format
                    for stock in search_results[:5]:
                        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])

                        with col_a:
                            st.write(f"**{stock['symbol']}**")

                        with col_b:
                            st.write(f"৳{stock['price']:.2f}")

                        with col_c:
                            change_color = "green" if stock['change'] >= 0 else "red"
                            st.markdown(f"<span style='color: {change_color}'>{stock['change']:+.2f}</span>",
                                      unsafe_allow_html=True)

                        with col_d:
                            change_color = "green" if stock['change_percent'] >= 0 else "red"
                            st.markdown(f"<span style='color: {change_color}'>{stock['change_percent']:+.2f}%</span>",
                                      unsafe_allow_html=True)

        with col2:
            st.write("**Popular Stocks:**")
            popular_stocks = ['SQURPHARMA', 'DHAKABANK', 'ISLAMIBANK', 'PRIMEBANK', 'PUBALIBANK', 'TECHNODRUG']

            for stock in popular_stocks:
                if st.button(f"📊 {stock}", key=f"popular_{stock}"):
                    st.session_state.selected_stock_lookup = stock

        # Stock Details Section
        selected_stock = st.session_state.get('selected_stock_lookup', '')

        if not selected_stock and search_results:
            selected_stock = st.selectbox(
                "Select a stock for detailed information:",
                options=[stock['symbol'] for stock in search_results],
                index=0
            )

        if selected_stock:
            st.markdown("---")
            self._display_stock_details(selected_stock)

    def _display_stock_details(self, symbol: str):
        """Display detailed stock information"""
        st.subheader(f"📈 {symbol} - Detailed Information")

        # Get stock data
        with st.spinner("Fetching stock data..."):
            stock_data = self.dse_finance.dsefinance(symbol, 'all')

        if not stock_data:
            st.error(f"No data found for {symbol}")
            return

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Current Price",
                value=f"৳{stock_data['price']:.2f}",
                delta=f"{stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)"
            )

        with col2:
            st.metric(
                label="High",
                value=f"৳{stock_data['high']:.2f}"
            )

        with col3:
            st.metric(
                label="Low",
                value=f"৳{stock_data['low']:.2f}"
            )

        with col4:
            st.metric(
                label="Volume",
                value=f"{stock_data['volume']:,}"
            )

        # Additional details
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Trading Information:**")
            st.write(f"• Previous Close: ৳{stock_data['previous_close']:.2f}")
            st.write(f"• Total Trades: {stock_data['trades']:,}")
            st.write(f"• Value (Million): ৳{stock_data['value_mn']:.2f}")

        with col2:
            st.write("**Market Data:**")
            st.write(f"• Last Updated: {stock_data['timestamp']}")

            # DSEFINANCE examples
            st.write("**API Examples:**")
            st.code(f"DSEFINANCE('{symbol}', 'price')")
            st.code(f"DSEFINANCE('{symbol}', 'volume')")
            st.code(f"DSEFINANCE('{symbol}', 'change')")

    def _render_historical_data(self):
        """Render historical data interface"""
        st.subheader("📈 Historical Data")

        col1, col2 = st.columns([1, 1])

        with col1:
            symbol = st.text_input(
                "Stock Symbol",
                value="GP",
                help="Enter DSE stock symbol"
            ).upper()

        with col2:
            period = st.selectbox(
                "Select Period",
                options=['1 Week', '1 Month', '3 Months', '6 Months', '1 Year', 'Custom'],
                index=2
            )

        # Date selection
        if period == 'Custom':
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=90)
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now()
                )
        else:
            # Calculate dates based on period
            end_date = datetime.now().date()
            if period == '1 Week':
                start_date = end_date - timedelta(days=7)
            elif period == '1 Month':
                start_date = end_date - timedelta(days=30)
            elif period == '3 Months':
                start_date = end_date - timedelta(days=90)
            elif period == '6 Months':
                start_date = end_date - timedelta(days=180)
            elif period == '1 Year':
                start_date = end_date - timedelta(days=365)

        # Fetch and display historical data
        if st.button("📊 Get Historical Data", type="primary"):
            with st.spinner("Fetching historical data..."):
                historical_data = self.dse_finance.dsefinance(
                    symbol,
                    'history',
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )

            if historical_data is not None and not historical_data.empty:
                # Display chart
                st.write(f"**Historical Data for {symbol}**")

                # Create candlestick chart
                fig = go.Figure(data=go.Candlestick(
                    x=historical_data['Date'],
                    open=historical_data['Open'],
                    high=historical_data['High'],
                    low=historical_data['Low'],
                    close=historical_data['Close'],
                    name=symbol
                ))

                fig.update_layout(
                    title=f"{symbol} - Historical Price Data",
                    yaxis_title="Price (৳)",
                    xaxis_title="Date",
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display data table
                st.write("**Data Table:**")
                st.dataframe(historical_data, use_container_width=True)

                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = self.dse_finance.export_to_csv(historical_data)
                    st.download_button(
                        "📥 Download CSV",
                        csv_data,
                        f"{symbol}_historical_{start_date}_to_{end_date}.csv",
                        "text/csv"
                    )

                with col2:
                    json_data = self.dse_finance.export_to_json(historical_data)
                    st.download_button(
                        "📥 Download JSON",
                        json_data,
                        f"{symbol}_historical_{start_date}_to_{end_date}.json",
                        "application/json"
                    )

                # API example
                st.write("**API Example:**")
                st.code(f"DSEFINANCE('{symbol}', 'history', '{start_date}', '{end_date}')")

            else:
                st.error(f"No historical data found for {symbol}")

    def _render_market_overview(self):
        """Render market overview interface"""
        st.subheader("📊 Market Overview")

        # Get market summary
        with st.spinner("Loading market data..."):
            market_summary = self.dse_finance.get_market_summary()

        if market_summary:
            # Market status
            status_color = "🟢" if market_summary['market_status'] == 'Open' else "🔴"
            st.info(f"{status_color} **Market Status: {market_summary['market_status']}**")

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Stocks",
                    value=market_summary['total_stocks']
                )

            with col2:
                st.metric(
                    "Advancing",
                    value=market_summary['advancing'],
                    delta=None
                )

            with col3:
                st.metric(
                    "Declining",
                    value=market_summary['declining']
                )

            with col4:
                st.metric(
                    "Unchanged",
                    value=market_summary['unchanged']
                )

            # Trading summary
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Total Volume",
                    value=f"{market_summary['total_volume']:,}"
                )

            with col2:
                st.metric(
                    "Total Value (Million)",
                    value=f"৳{market_summary['total_value_mn']:.2f}"
                )

            # Market composition chart
            fig = px.pie(
                values=[market_summary['advancing'], market_summary['declining'], market_summary['unchanged']],
                names=['Advancing', 'Declining', 'Unchanged'],
                title="Market Composition",
                color_discrete_map={
                    'Advancing': '#00CC96',
                    'Declining': '#EF553B',
                    'Unchanged': '#636EFA'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        # Top performers section
        st.markdown("---")
        st.write("**Top Performing Stocks:**")

        # Get some sample top performers
        with st.spinner("Loading top performers..."):
            all_stocks = self.dse_finance.search_stocks("", limit=100)

        if all_stocks:
            # Sort by change percentage
            top_gainers = sorted(all_stocks, key=lambda x: x['change_percent'], reverse=True)[:10]
            top_losers = sorted(all_stocks, key=lambda x: x['change_percent'])[:10]

            col1, col2 = st.columns(2)

            with col1:
                st.write("**📈 Top Gainers:**")
                for stock in top_gainers:
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        st.write(stock['symbol'])
                    with col_b:
                        st.write(f"৳{stock['price']:.2f}")
                    with col_c:
                        st.markdown(f"<span style='color: green'>+{stock['change_percent']:.2f}%</span>",
                                  unsafe_allow_html=True)

            with col2:
                st.write("**📉 Top Losers:**")
                for stock in top_losers:
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        st.write(stock['symbol'])
                    with col_b:
                        st.write(f"৳{stock['price']:.2f}")
                    with col_c:
                        st.markdown(f"<span style='color: red'>{stock['change_percent']:.2f}%</span>",
                                  unsafe_allow_html=True)

    def _render_bulk_export(self):
        """Render bulk export interface"""
        st.subheader("📥 Bulk Data Export")

        # Stock selection
        col1, col2 = st.columns([2, 1])

        with col1:
            export_option = st.selectbox(
                "Select Export Type",
                options=[
                    "Multiple Stocks - Current Data",
                    "Single Stock - Historical Data",
                    "Market Summary",
                    "All Stocks - Current Data"
                ]
            )

        with col2:
            export_format = st.selectbox(
                "Export Format",
                options=["CSV", "JSON"],
                index=0
            )

        if export_option == "Multiple Stocks - Current Data":
            symbols_input = st.text_area(
                "Enter stock symbols (one per line or comma-separated)",
                value="GP\nSQURPHARMA\nBEXIMCO\nLHBL\nBRACBANK",
                help="Enter stock symbols separated by new lines or commas"
            )

            if st.button("📊 Get Multiple Stocks Data", type="primary"):
                # Parse symbols
                symbols = []
                for line in symbols_input.replace(',', '\n').split('\n'):
                    symbol = line.strip().upper()
                    if symbol:
                        symbols.append(symbol)

                if symbols:
                    with st.spinner(f"Fetching data for {len(symbols)} stocks..."):
                        bulk_data = self.dse_finance.get_multiple_stocks(symbols, 'price')

                    if not bulk_data.empty:
                        st.write(f"**Data for {len(bulk_data)} stocks:**")
                        st.dataframe(bulk_data, use_container_width=True)

                        # Export
                        if export_format == "CSV":
                            export_data = self.dse_finance.export_to_csv(bulk_data)
                            filename = f"dse_multiple_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                        else:
                            export_data = self.dse_finance.export_to_json(bulk_data)
                            filename = f"dse_multiple_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

                        st.download_button(
                            f"📥 Download {export_format}",
                            export_data,
                            filename,
                            "text/csv" if export_format == "CSV" else "application/json"
                        )

                        # API examples
                        st.write("**API Examples:**")
                        for symbol in symbols[:3]:  # Show first 3
                            st.code(f"DSEFINANCE('{symbol}', 'price')")

        elif export_option == "Market Summary":
            if st.button("📊 Get Market Summary", type="primary"):
                with st.spinner("Fetching market summary..."):
                    market_data = self.dse_finance.get_market_summary()

                if market_data:
                    st.json(market_data)

                    # Export
                    if export_format == "CSV":
                        export_data = self.dse_finance.export_to_csv(market_data)
                        filename = f"dse_market_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                    else:
                        export_data = self.dse_finance.export_to_json(market_data)
                        filename = f"dse_market_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

                    st.download_button(
                        f"📥 Download {export_format}",
                        export_data,
                        filename,
                        "text/csv" if export_format == "CSV" else "application/json"
                    )

        # Help section
        st.markdown("---")
        with st.expander("ℹ️ DSE Finance API Reference"):
            st.write("""
            **Available Functions:**

            **Current Data:**
            - `DSEFINANCE('GP', 'price')` - Get current price and basic info
            - `DSEFINANCE('GP', 'volume')` - Get volume data
            - `DSEFINANCE('GP', 'change')` - Get price change data
            - `DSEFINANCE('GP', 'all')` - Get all available data

            **Historical Data:**
            - `DSEFINANCE('GP', 'history', '2024-01-01', '2024-12-31')` - Get historical data

            **Data Fields:**
            - **price**: Current price, high, low, previous close
            - **volume**: Trading volume, value, number of trades
            - **change**: Price change, percentage change
            - **all**: Complete dataset for the stock

            **Date Format:** YYYY-MM-DD (e.g., 2024-01-01)

            **Supported Stocks:** All DSE listed companies
            """)

            st.write("**Example Usage in Excel/Google Sheets:**")
            st.code("""
=DSEFINANCE("GP", "price")
=DSEFINANCE("SQURPHARMA", "volume")
=DSEFINANCE("BEXIMCO", "history", "2024-01-01", "2024-12-31")
            """)