import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import PortfolioItem, PortfolioSnapshot
from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager

class DashboardUI:
    def __init__(self, dse_api: DSEAPIService, data_manager: DataManager):
        self.dse_api = dse_api
        self.data_manager = data_manager
    
    def render(self):
        """Render the main dashboard"""
        st.title("📈 Portfolio Dashboard")

        # Market Status Bar
        self._render_market_status_bar()

        # Check if user has selected stocks
        if not st.session_state.selected_stocks:
            st.warning("⚠️ No stocks selected for tracking. Please go to 'Stock Selector' to add stocks.")
            return

        # Auto-refresh toggle
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader("Real-time Portfolio Overview")
        with col2:
            auto_refresh = st.checkbox("Auto Refresh", value=True)
        with col3:
            if st.button("🔄 Manual Refresh"):
                st.rerun()
        
        # Portfolio summary cards
        self._render_portfolio_summary()
        
        st.markdown("---")
        
        # Charts section
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Charts", "📈 Portfolio Performance", "🥧 Holdings Distribution", "📋 Stock Details"])
        
        with tab1:
            self._render_price_charts()
        
        with tab2:
            self._render_portfolio_performance()
        
        with tab3:
            self._render_holdings_distribution()
        
        with tab4:
            self._render_stock_details()
        
        # Auto-refresh functionality
        if auto_refresh:
            import time
            time.sleep(30)  # Refresh every 30 seconds
            st.rerun()
    
    def _render_portfolio_summary(self):
        """Render portfolio summary cards"""
        try:
            # Get current stock data
            stocks_data = []
            total_portfolio_value = 0
            total_change = 0
            
            for symbol in st.session_state.selected_stocks:
                stock = self.dse_api.get_stock_by_symbol(symbol)
                if stock:
                    # Get portfolio quantity (if any)
                    quantity = st.session_state.portfolio_items.get(symbol, PortfolioItem(
                        symbol=symbol,
                        quantity=0,
                        average_cost=0,
                        current_price=stock.current_price,
                        last_updated=datetime.now()
                    )).quantity
                    
                    current_value = quantity * stock.current_price
                    total_portfolio_value += current_value
                    
                    # Calculate change from previous close
                    change_value = quantity * stock.price_change
                    total_change += change_value
                    
                    stocks_data.append({
                        'symbol': symbol,
                        'name': stock.name,
                        'current_price': stock.current_price,
                        'change': stock.price_change,
                        'change_percent': stock.price_change_percent,
                        'quantity': quantity,
                        'value': current_value
                    })
            
            # Display summary cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Portfolio Value",
                    f"৳{total_portfolio_value:,.2f}",
                    delta=f"৳{total_change:+,.2f}"
                )
            
            with col2:
                total_change_percent = (total_change / (total_portfolio_value - total_change) * 100) if (total_portfolio_value - total_change) > 0 else 0
                st.metric(
                    "Daily Change",
                    f"{total_change_percent:+.2f}%",
                    delta=f"৳{total_change:+,.2f}"
                )
            
            with col3:
                active_stocks = len([s for s in stocks_data if s['quantity'] > 0])
                st.metric(
                    "Active Holdings",
                    active_stocks,
                    delta=f"{len(st.session_state.selected_stocks)} tracked"
                )
            
            with col4:
                if stocks_data:
                    avg_change = np.mean([s['change_percent'] for s in stocks_data])
                    st.metric(
                        "Avg Stock Change",
                        f"{avg_change:+.2f}%",
                        delta="Market Average"
                    )
        
        except Exception as e:
            st.error(f"Error loading portfolio summary: {e}")
    
    def _render_price_charts(self):
        """Render price movement charts"""
        st.subheader("📊 Stock Price Movements")
        
        # Select stocks to display
        selected_for_chart = st.multiselect(
            "Select stocks to display in charts:",
            options=st.session_state.selected_stocks,
            default=st.session_state.selected_stocks[:5]  # Show first 5 by default
        )
        
        if not selected_for_chart:
            st.info("Please select stocks to display charts")
            return
        
        # Chart type selection
        chart_type = st.selectbox(
            "Chart Type:",
            ["Line Chart", "Candlestick Chart", "Bar Chart"],
            key="price_chart_type"
        )
        
        # Time period selection
        days = st.slider("Time Period (days)", 1, 90, 30)
        
        # Generate charts
        for symbol in selected_for_chart:
            try:
                st.subheader(f"{symbol} - Price Chart")
                
                # Get historical data
                historical_data = self.dse_api.get_stock_historical_data(symbol, days)
                
                if historical_data:
                    if chart_type == "Line Chart":
                        self._create_line_chart(symbol, historical_data)
                    elif chart_type == "Candlestick Chart":
                        self._create_candlestick_chart(symbol, historical_data)
                    elif chart_type == "Bar Chart":
                        self._create_bar_chart(symbol, historical_data)
                else:
                    st.warning(f"No historical data available for {symbol}")
            
            except Exception as e:
                st.error(f"Error creating chart for {symbol}: {e}")
    
    def _create_line_chart(self, symbol: str, data: List[StockPriceHistory]):
        """Create line chart for stock price"""
        df = pd.DataFrame([{
            'Date': item.date,
            'Close': item.close_price,
            'Volume': item.volume
        } for item in data])
        
        fig = go.Figure()
        
        # Price line
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines',
            name='Price',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} - Price Movement",
            xaxis_title="Date",
            yaxis_title="Price (৳)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_candlestick_chart(self, symbol: str, data: List[StockPriceHistory]):
        """Create enhanced candlestick chart with technical indicators"""
        df = pd.DataFrame([{
            'Date': item.date,
            'Open': item.open_price,
            'High': item.high,
            'Low': item.low,
            'Close': item.close_price,
            'Volume': item.volume
        } for item in data])

        # Calculate technical indicators
        df = self._calculate_technical_indicators(df)

        # Create subplots for price and volume
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} - Candlestick Chart with Technical Indicators', 'Volume'),
            row_width=[0.2, 0.7]
        )

        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol,
            increasing_line_color='#00D100',
            decreasing_line_color='#FF4B4B'
        ), row=1, col=1)

        # Add moving averages
        if 'MA_5' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['MA_5'],
                mode='lines',
                name='MA(5)',
                line=dict(color='orange', width=1)
            ), row=1, col=1)

        if 'MA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['MA_20'],
                mode='lines',
                name='MA(20)',
                line=dict(color='blue', width=1)
            ), row=1, col=1)

        # Add volume bars
        colors = ['red' if row['Open'] > row['Close'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)

        # Update layout
        fig.update_layout(
            title=f"{symbol} - Enhanced Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price (৳)",
            xaxis2_title="Date",
            yaxis2_title="Volume",
            height=700,
            showlegend=True,
            hovermode='x unified'
        )

        # Remove range slider for cleaner look
        fig.update_layout(xaxis_rangeslider_visible=False)

        st.plotly_chart(fig, use_container_width=True)

        # Display key statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            current_price = df['Close'].iloc[-1]
            st.metric("Current Price", f"৳{current_price:.2f}")

        with col2:
            price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2] if len(df) > 1 else 0
            change_pct = (price_change / df['Close'].iloc[-2] * 100) if len(df) > 1 and df['Close'].iloc[-2] != 0 else 0
            st.metric("Change", f"৳{price_change:.2f}", f"{change_pct:+.2f}%")

        with col3:
            volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].mean()
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0
            st.metric("Volume", f"{volume:,.0f}", f"{volume_ratio:.1f}x avg")

        with col4:
            high_52w = df['High'].max()
            low_52w = df['Low'].min()
            st.metric("Range", f"৳{low_52w:.2f} - ৳{high_52w:.2f}")

    def _calculate_technical_indicators(self, df):
        """Calculate technical indicators for the dataframe"""
        # Simple Moving Averages
        if len(df) >= 5:
            df['MA_5'] = df['Close'].rolling(window=5).mean()
        if len(df) >= 20:
            df['MA_20'] = df['Close'].rolling(window=20).mean()

        # RSI (Relative Strength Index)
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

        # MACD (Moving Average Convergence Divergence)
        if len(df) >= 26:
            exp1 = df['Close'].ewm(span=12).mean()
            exp2 = df['Close'].ewm(span=26).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9).mean()

        return df
    
    def _create_bar_chart(self, symbol: str, data: List[StockPriceHistory]):
        """Create bar chart for stock volume"""
        df = pd.DataFrame([{
            'Date': item.date,
            'Volume': item.volume,
            'Price': item.close_price
        } for item in data])
        
        fig = go.Figure()
        
        # Volume bars
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        
        # Price line on secondary y-axis
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Price'],
            mode='lines',
            name='Price',
            yaxis='y2',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} - Volume & Price",
            xaxis_title="Date",
            yaxis=dict(title="Volume", side="left"),
            yaxis2=dict(title="Price (৳)", side="right", overlaying="y"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_portfolio_performance(self):
        """Render portfolio performance chart"""
        st.subheader("📈 Portfolio Performance")
        
        # Get portfolio history (simulated for now)
        try:
            # Create sample portfolio performance data
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            portfolio_values = []
            
            # Simulate portfolio value changes
            base_value = 100000  # Starting value
            for i, date in enumerate(dates):
                # Random walk simulation (replace with actual data later)
                change = np.random.normal(0, 0.02)  # 2% daily volatility
                base_value *= (1 + change)
                portfolio_values.append(base_value)
            
            # Create performance chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='green', width=3),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title="Portfolio Value Over Time",
                xaxis_title="Date",
                yaxis_title="Portfolio Value (৳)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0] * 100
                st.metric("Total Return", f"{total_return:+.2f}%")
            
            with col2:
                daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
                volatility = np.std(daily_returns) * np.sqrt(252) * 100  # Annualized
                st.metric("Volatility", f"{volatility:.2f}%")
            
            with col3:
                max_value = max(portfolio_values)
                current_value = portfolio_values[-1]
                drawdown = (max_value - current_value) / max_value * 100
                st.metric("Max Drawdown", f"{drawdown:.2f}%")
        
        except Exception as e:
            st.error(f"Error rendering portfolio performance: {e}")

    def _render_market_status_bar(self):
        """Render market status information bar"""
        try:
            from src.services.market_status import MarketStatusService
            market_service = MarketStatusService()
            market_status = market_service.get_market_status()

            # Create a colored status bar
            status_color = "#00D100" if market_status['is_open'] else "#FF4B4B"
            status_icon = "🟢" if market_status['is_open'] else "🔴"

            # Display market status in a container
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 2, 2])

                with col1:
                    st.markdown(f"<div style='background-color: {status_color}; color: white; padding: 10px; border-radius: 5px; text-align: center;'>"
                               f"<b>{status_icon} {market_status['status']}</b></div>", unsafe_allow_html=True)

                with col2:
                    st.info(f"⏰ **Current Time:** {market_status['current_time']}")

                with col3:
                    st.info(f"📅 **{market_status['next_change']}** in {market_status['time_until_change']}")

                with col4:
                    st.info(f"🕐 **Market Hours:** {market_status['market_hours']}")

            st.markdown("---")

        except Exception as e:
            st.error(f"Error loading market status: {e}")

    def _render_holdings_distribution(self):
        """Render holdings distribution pie chart"""
        st.subheader("🥧 Holdings Distribution")
        
        try:
            # Get portfolio holdings data
            holdings_data = []
            total_value = 0
            
            for symbol in st.session_state.selected_stocks:
                portfolio_item = st.session_state.portfolio_items.get(symbol)
                if portfolio_item and portfolio_item.quantity > 0:
                    value = portfolio_item.current_value
                    holdings_data.append({
                        'Symbol': symbol,
                        'Value': value,
                        'Percentage': 0  # Will calculate after getting total
                    })
                    total_value += value
            
            if holdings_data:
                # Calculate percentages
                for item in holdings_data:
                    item['Percentage'] = (item['Value'] / total_value) * 100
                
                # Create pie chart
                df = pd.DataFrame(holdings_data)
                
                fig = px.pie(
                    df,
                    values='Value',
                    names='Symbol',
                    title='Portfolio Holdings Distribution',
                    hover_data=['Percentage']
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
                # Holdings table
                st.subheader("Holdings Details")
                df_display = df.copy()
                df_display['Value'] = df_display['Value'].apply(lambda x: f"৳{x:,.2f}")
                df_display['Percentage'] = df_display['Percentage'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(
                    df_display[['Symbol', 'Value', 'Percentage']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No holdings found. Add transactions to see holdings distribution.")
        
        except Exception as e:
            st.error(f"Error rendering holdings distribution: {e}")
    
    def _render_stock_details(self):
        """Render detailed stock information table"""
        st.subheader("📋 Stock Details")
        
        try:
            # Get current stock data
            stocks_data = []
            
            for symbol in st.session_state.selected_stocks:
                stock = self.dse_api.get_stock_by_symbol(symbol)
                if stock:
                    # Get portfolio info
                    portfolio_item = st.session_state.portfolio_items.get(symbol)
                    quantity = portfolio_item.quantity if portfolio_item else 0
                    
                    stocks_data.append({
                        'Symbol': stock.symbol,
                        'Company Name': stock.name,
                        'LTP': f"৳{stock.current_price:.2f}",
                        'Previous Close': f"৳{stock.previous_close:.2f}",
                        'Change': f"{stock.price_change:+.2f}",
                        'Change %': f"{stock.price_change_percent:+.2f}%",
                        'High': f"৳{stock.high:.2f}" if stock.high else 'N/A',
                        'Low': f"৳{stock.low:.2f}" if stock.low else 'N/A',
                        'Volume': f"{stock.volume:,}",
                        'Holdings': quantity,
                        'Holdings Value': f"৳{quantity * stock.current_price:,.2f}",
                        'Last Updated': stock.last_updated.strftime('%H:%M:%S') if stock.last_updated else 'N/A'
                    })
            
            if stocks_data:
                df = pd.DataFrame(stocks_data)
                
                # Color code based on change
                def color_change(val):
                    if '+' in str(val):
                        return 'color: green'
                    elif '-' in str(val):
                        return 'color: red'
                    return ''
                
                styled_df = df.style.applymap(color_change, subset=['Change', 'Change %'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No stock data available")
        
        except Exception as e:
            st.error(f"Error rendering stock details: {e}")
