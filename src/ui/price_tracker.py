import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from src.models.stock import Stock, StockPriceHistory
from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager
from src.ui.components.time_range_selector import create_time_range_selector

class PriceTrackerUI:
    def __init__(self, dse_api: DSEAPIService, data_manager: DataManager):
        self.dse_api = dse_api
        self.data_manager = data_manager
        self.time_range_selector = create_time_range_selector(default_range="1M")

    def render(self):
        """Render the Price Tracker page with pivot table equivalent functionality"""
        st.title("📊 Price Tracker & Analysis")

        if not st.session_state.selected_stocks:
            st.warning("⚠️ No stocks selected for tracking. Please go to 'Stock Selector' to add stocks.")
            return

        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Matrix", "📊 Comparison View", "📋 Data Table", "🔄 Historical Pivot"])

        with tab1:
            self._render_price_matrix()

        with tab2:
            self._render_comparison_view()

        with tab3:
            self._render_data_table()

        with tab4:
            self._render_historical_pivot()

    def _render_price_matrix(self):
        """Render a matrix view of stock prices similar to Excel pivot table"""
        st.subheader("📈 Real-time Price Matrix")

        # Time period selection
        col1, col2, col3 = st.columns(3)
        with col1:
            days = st.selectbox("Time Period", [1, 7, 30, 90], index=2)
        with col2:
            refresh_interval = st.selectbox("Auto Refresh", ["Off", "30s", "1m", "5m"], index=0)
        with col3:
            if st.button("🔄 Refresh Data"):
                st.rerun()

        # Get current prices for all selected stocks
        with st.spinner("Fetching latest prices..."):
            stock_data = []
            for symbol in st.session_state.selected_stocks:
                try:
                    # Get current stock data
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    if stock:
                        # Get historical data for trend calculation
                        historical = self.dse_api.get_stock_historical_data(symbol, min(days, 30))

                        # Calculate trend
                        trend = "→"
                        trend_pct = 0
                        if historical and len(historical) > 1:
                            old_price = historical[0].close_price
                            new_price = historical[-1].close_price
                            trend_pct = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
                            trend = "📈" if trend_pct > 0 else "📉" if trend_pct < 0 else "→"

                        stock_data.append({
                            'Symbol': symbol,
                            'Current Price': stock.current_price,
                            'Previous Close': stock.previous_close,
                            'Change': stock.price_change,
                            'Change %': stock.price_change_percent,
                            'Volume': stock.volume,
                            'High': stock.high or stock.current_price,
                            'Low': stock.low or stock.current_price,
                            'Trend': trend,
                            f'{days}d Change %': trend_pct
                        })
                except Exception as e:
                    st.error(f"Error fetching data for {symbol}: {e}")

        if stock_data:
            df = pd.DataFrame(stock_data)

            # Create a styled dataframe
            def style_dataframe(df):
                """Apply styling to the dataframe"""
                def color_change(val):
                    if isinstance(val, (int, float)):
                        color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
                        return f'color: {color}'
                    return ''

                def color_trend(val):
                    if val == "📈":
                        return 'color: green'
                    elif val == "📉":
                        return 'color: red'
                    return 'color: gray'

                styled = df.style.applymap(color_change, subset=['Change', 'Change %', f'{days}d Change %']) \
                              .applymap(color_trend, subset=['Trend']) \
                              .format({
                                  'Current Price': '৳{:.2f}',
                                  'Previous Close': '৳{:.2f}',
                                  'Change': '৳{:.2f}',
                                  'Change %': '{:+.2f}%',
                                  'Volume': '{:,}',
                                  'High': '৳{:.2f}',
                                  'Low': '৳{:.2f}',
                                  f'{days}d Change %': '{:+.2f}%'
                              })
                return styled

            # Display styled dataframe
            st.dataframe(style_dataframe(df), use_container_width=True)

            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                gainers = len(df[df['Change %'] > 0])
                gainers_pct = (gainers/len(df)*100) if len(df) > 0 else 0
                st.metric("Gainers", gainers, f"{gainers_pct:.1f}%")

            with col2:
                losers = len(df[df['Change %'] < 0])
                losers_pct = (losers/len(df)*100) if len(df) > 0 else 0
                st.metric("Losers", losers, f"{losers_pct:.1f}%")

            with col3:
                avg_change = df['Change %'].mean()
                st.metric("Avg Change", f"{avg_change:+.2f}%")

            with col4:
                total_volume = df['Volume'].sum()
                st.metric("Total Volume", f"{total_volume:,.0f}")

        else:
            st.error("No data available for selected stocks")

    def _render_comparison_view(self):
        """Render comparison charts for multiple stocks"""
        st.subheader("📊 Multi-Stock Comparison")

        # Stock selection for comparison
        comparison_stocks = st.multiselect(
            "Select stocks to compare (max 5):",
            options=st.session_state.selected_stocks,
            default=st.session_state.selected_stocks[:3],
            max_selections=5
        )

        if not comparison_stocks:
            st.info("Please select stocks to compare")
            return

        # Time period and normalization options
        # Configuration options
        col1, col2 = st.columns(2)
        with col1:
            normalize = st.checkbox("Normalize to 100", value=True, help="Start all stocks at 100 for comparison")
            chart_type = st.selectbox("Chart Type", ["Line", "Area", "Candlestick"])

        with col2:
            # Time range selector
            start_date, end_date = self.time_range_selector.render(
                key_prefix="price_comparison",
                show_custom=True,
                compact=True
            )

        # Calculate days from date range
        date_diff = end_date - start_date
        days = max(1, date_diff.days)

        # Fetch historical data for comparison
        comparison_data = {}
        for symbol in comparison_stocks:
            try:
                historical = self.dse_api.get_stock_historical_data(symbol, days)
                if historical:
                    comparison_data[symbol] = historical
            except Exception as e:
                st.warning(f"Could not fetch data for {symbol}: {e}")

        if comparison_data:
            # Create comparison chart
            fig = go.Figure()

            for symbol, data in comparison_data.items():
                dates = [item.date for item in data]
                prices = [item.close_price for item in data]

                if normalize and prices:
                    # Normalize to start at 100
                    base_price = prices[0]
                    prices = [(price / base_price) * 100 for price in prices]

                if chart_type == "Line":
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=prices,
                        mode='lines',
                        name=symbol,
                        line=dict(width=2)
                    ))
                elif chart_type == "Area":
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=prices,
                        mode='lines',
                        name=symbol,
                        fill='tonexty' if symbol != comparison_stocks[0] else None,
                        line=dict(width=2)
                    ))

            y_title = "Normalized Price (Base=100)" if normalize else "Price (৳)"
            fig.update_layout(
                title="Stock Price Comparison",
                xaxis_title="Date",
                yaxis_title=y_title,
                hovermode='x unified',
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Performance comparison table
            st.subheader("📋 Performance Summary")
            perf_data = []
            for symbol, data in comparison_data.items():
                if len(data) > 1:
                    start_price = data[0].close_price
                    end_price = data[-1].close_price
                    total_return = ((end_price - start_price) / start_price * 100) if start_price > 0 else 0

                    # Calculate volatility
                    prices = [item.close_price for item in data]
                    returns = [((prices[i] - prices[i-1]) / prices[i-1]) for i in range(1, len(prices))]
                    volatility = np.std(returns) * np.sqrt(252) * 100 if returns else 0

                    # Calculate max drawdown
                    peak = prices[0]
                    max_dd = 0
                    for price in prices:
                        if price > peak:
                            peak = price
                        drawdown = (peak - price) / peak * 100
                        if drawdown > max_dd:
                            max_dd = drawdown

                    perf_data.append({
                        'Symbol': symbol,
                        'Start Price': f"৳{start_price:.2f}",
                        'End Price': f"৳{end_price:.2f}",
                        'Total Return': f"{total_return:+.2f}%",
                        'Volatility': f"{volatility:.2f}%",
                        'Max Drawdown': f"{max_dd:.2f}%"
                    })

            if perf_data:
                perf_df = pd.DataFrame(perf_data)
                st.dataframe(perf_df, use_container_width=True)

    def _render_data_table(self):
        """Render detailed data table with filtering and sorting"""
        st.subheader("📋 Detailed Stock Data Table")

        # Data refresh
        if st.button("🔄 Refresh All Data"):
            with st.spinner("Fetching latest data for all stocks..."):
                st.rerun()

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            min_price = st.number_input("Min Price Filter (৳)", min_value=0.0, value=0.0)
        with col2:
            min_volume = st.number_input("Min Volume Filter", min_value=0, value=0)
        with col3:
            sort_by = st.selectbox("Sort By", ["Symbol", "Current Price", "Change %", "Volume"])

        # Fetch detailed data
        detailed_data = []
        for symbol in st.session_state.selected_stocks:
            try:
                stock = self.dse_api.get_stock_by_symbol(symbol)
                if stock and stock.current_price >= min_price and stock.volume >= min_volume:
                    # Calculate additional metrics
                    portfolio_item = st.session_state.portfolio_items.get(symbol)
                    position_value = 0
                    gain_loss = 0
                    if portfolio_item and portfolio_item.quantity > 0:
                        position_value = portfolio_item.current_value
                        gain_loss = portfolio_item.gain_loss

                    detailed_data.append({
                        'Symbol': symbol,
                        'Name': stock.name,
                        'Current Price': stock.current_price,
                        'Previous Close': stock.previous_close,
                        'Change': stock.price_change,
                        'Change %': stock.price_change_percent,
                        'Volume': stock.volume,
                        'High': stock.high or stock.current_price,
                        'Low': stock.low or stock.current_price,
                        'Position Value': position_value,
                        'P&L': gain_loss,
                        'Last Updated': stock.last_updated.strftime('%H:%M:%S') if stock.last_updated else 'N/A'
                    })
            except Exception as e:
                st.error(f"Error fetching data for {symbol}: {e}")

        if detailed_data:
            df = pd.DataFrame(detailed_data)

            # Sort data
            if sort_by in df.columns:
                ascending = sort_by == "Symbol"  # Sort symbols alphabetically
                df = df.sort_values(sort_by, ascending=ascending)

            # Display with formatting
            st.dataframe(
                df.style.format({
                    'Current Price': '৳{:.2f}',
                    'Previous Close': '৳{:.2f}',
                    'Change': '৳{:.2f}',
                    'Change %': '{:+.2f}%',
                    'Volume': '{:,}',
                    'High': '৳{:.2f}',
                    'Low': '৳{:.2f}',
                    'Position Value': '৳{:.2f}',
                    'P&L': '৳{:.2f}'
                }),
                use_container_width=True
            )

            # Export functionality
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )

            with col2:
                if st.button("Copy to Clipboard"):
                    st.info("Data copied to clipboard (feature would be implemented)")

    def _render_historical_pivot(self):
        """Render historical pivot table view"""
        st.subheader("🔄 Historical Data Pivot Analysis")

        # Configuration
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_symbols = st.multiselect(
                "Select stocks for pivot analysis:",
                options=st.session_state.selected_stocks,
                default=st.session_state.selected_stocks[:5]
            )
        with col2:
            days = st.selectbox("Historical Period", [7, 14, 30, 60, 90], index=2)
        with col3:
            data_field = st.selectbox("Data Field", ["Close Price", "Volume", "High", "Low"])

        if not selected_symbols:
            st.info("Please select stocks for pivot analysis")
            return

        # Fetch historical data
        pivot_data = []
        with st.spinner("Fetching historical data..."):
            for symbol in selected_symbols:
                try:
                    historical = self.dse_api.get_stock_historical_data(symbol, days)
                    for item in historical:
                        value = item.close_price
                        if data_field == "Volume":
                            value = item.volume
                        elif data_field == "High":
                            value = item.high
                        elif data_field == "Low":
                            value = item.low

                        pivot_data.append({
                            'Date': item.date.strftime('%Y-%m-%d'),
                            'Symbol': symbol,
                            'Value': value
                        })
                except Exception as e:
                    st.warning(f"Could not fetch historical data for {symbol}: {e}")

        if pivot_data:
            # Create pivot table
            df = pd.DataFrame(pivot_data)
            pivot_table = df.pivot(index='Date', columns='Symbol', values='Value')
            pivot_table = pivot_table.fillna(0)

            # Display pivot table
            st.subheader(f"Pivot Table - {data_field}")

            # Format based on data type
            if data_field == "Volume":
                formatted_pivot = pivot_table.style.format('{:,.0f}')
            else:
                formatted_pivot = pivot_table.style.format('৳{:.2f}')

            st.dataframe(formatted_pivot, use_container_width=True)

            # Create heatmap
            st.subheader("Data Heatmap")
            fig = px.imshow(
                pivot_table.T,  # Transpose for better view
                labels=dict(x="Date", y="Symbol", color=data_field),
                aspect="auto",
                title=f"{data_field} Heatmap"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Statistics
            st.subheader("Summary Statistics")
            stats = pivot_table.describe()
            st.dataframe(stats.style.format('{:.2f}'), use_container_width=True)

            # Export pivot table
            if st.button("Export Pivot Table"):
                csv = pivot_table.to_csv()
                st.download_button(
                    label="Download Pivot CSV",
                    data=csv,
                    file_name=f"pivot_{data_field.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )