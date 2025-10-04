import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from src.models.portfolio import PortfolioItem, Transaction, TransactionType
from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager
from src.ui.components.reset_component import create_reset_component
from src.ui.components.time_range_selector import create_time_range_selector

class PortfolioUI:
    def __init__(self, dse_api: DSEAPIService, data_manager: DataManager):
        self.dse_api = dse_api
        self.data_manager = data_manager
        self.reset_component = create_reset_component(data_manager)
        self.time_range_selector = create_time_range_selector(default_range="1M")
    
    def render(self):
        """Render the portfolio management page"""
        st.title("💼 Portfolio Management")
        
        # Portfolio overview
        self._render_portfolio_overview()
        
        st.markdown("---")
        
        # Tabs for different portfolio views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Holdings", "📈 Performance", "💰 P&L Analysis", "📋 Transaction History", "🗑️ Reset Data"])

        with tab1:
            self._render_holdings_view()

        with tab2:
            self._render_performance_view()

        with tab3:
            self._render_pnl_analysis()

        with tab4:
            self._render_transaction_history()

        with tab5:
            self._render_reset_tab()
    
    def _render_portfolio_overview(self):
        """Render portfolio overview cards"""
        try:
            # Calculate portfolio metrics
            total_cost = 0
            total_current_value = 0
            total_gain_loss = 0
            holdings_count = 0
            
            for symbol, portfolio_item in st.session_state.portfolio_items.items():
                if portfolio_item.quantity > 0:
                    total_cost += portfolio_item.total_cost
                    total_current_value += portfolio_item.current_value
                    total_gain_loss += portfolio_item.gain_loss
                    holdings_count += 1
            
            # Display overview cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Portfolio Value",
                    f"৳{total_current_value:,.2f}",
                    delta=f"৳{total_gain_loss:+,.2f}"
                )
            
            with col2:
                gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
                st.metric(
                    "Total P&L",
                    f"{gain_loss_percent:+.2f}%",
                    delta=f"৳{total_gain_loss:+,.2f}"
                )
            
            with col3:
                st.metric(
                    "Total Investment",
                    f"৳{total_cost:,.2f}",
                    delta=f"{holdings_count} holdings"
                )
            
            with col4:
                # Calculate today's change
                today_change = 0
                for symbol, portfolio_item in st.session_state.portfolio_items.items():
                    if portfolio_item.quantity > 0:
                        stock = self.dse_api.get_stock_by_symbol(symbol)
                        if stock:
                            today_change += portfolio_item.quantity * stock.price_change
                
                st.metric(
                    "Today's Change",
                    f"৳{today_change:+,.2f}",
                    delta="Daily P&L"
                )
        
        except Exception as e:
            st.error(f"Error calculating portfolio overview: {e}")
    
    def _render_holdings_view(self):
        """Render detailed holdings view"""
        st.subheader("📊 Current Holdings")
        
        try:
            holdings_data = []
            
            for symbol, portfolio_item in st.session_state.portfolio_items.items():
                if portfolio_item.quantity > 0:
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    current_price = stock.current_price if stock else portfolio_item.current_price
                    
                    # Update current price in portfolio item
                    portfolio_item.current_price = current_price
                    
                    holdings_data.append({
                        'Symbol': symbol,
                        'Quantity': f"{portfolio_item.quantity:,}",
                        'Avg Cost': f"৳{portfolio_item.average_cost:.2f}",
                        'Current Price': f"৳{current_price:.2f}",
                        'Total Cost': f"৳{portfolio_item.total_cost:,.2f}",
                        'Current Value': f"৳{portfolio_item.current_value:,.2f}",
                        'P&L': f"৳{portfolio_item.gain_loss:+,.2f}",
                        'P&L %': f"{portfolio_item.gain_loss_percent:+.2f}%",
                        'Weight': f"{(portfolio_item.current_value / sum(item.current_value for item in st.session_state.portfolio_items.values() if item.quantity > 0)) * 100:.1f}%"
                    })
            
            if holdings_data:
                df = pd.DataFrame(holdings_data)
                
                # Sort by current value (largest holdings first)
                df['sort_value'] = df['Current Value'].str.replace('৳', '').str.replace(',', '').astype(float)
                df = df.sort_values('sort_value', ascending=False)

                # Color coding for P&L
                def color_pnl(val):
                    if '+' in str(val):
                        return 'color: green'
                    elif '-' in str(val):
                        return 'color: red'
                    return ''

                # Create a copy for display without the sort column
                display_df = df.drop('sort_value', axis=1)
                styled_df = display_df.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)

                # Holdings pie chart
                st.subheader("Holdings Distribution")

                try:
                    if len(df) > 0 and 'sort_value' in df.columns:
                        fig = px.pie(
                            df,
                            values='sort_value',
                            names='Symbol',
                            title='Portfolio Holdings by Value'
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data available for holdings chart")
                except Exception as chart_error:
                    st.error(f"Error creating holdings chart: {chart_error}")
                    st.info("Chart data debugging:")
                    st.write("DataFrame columns:", df.columns.tolist())
                    st.write("DataFrame shape:", df.shape)
            
            else:
                st.info("No holdings found. Add some transactions to see your portfolio holdings.")
        
        except Exception as e:
            st.error(f"Error rendering holdings view: {e}")
    
    def _render_performance_view(self):
        """Render portfolio performance charts"""
        st.subheader("📈 Portfolio Performance")

        try:
            # Time range selector
            start_date, end_date = self.time_range_selector.render(
                key_prefix="portfolio_performance",
                show_custom=True,
                compact=False
            )

            # Generate sample performance data (replace with actual data from data manager)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Simulate portfolio value progression
            portfolio_values = []
            benchmark_values = []  # DSEX benchmark
            
            initial_value = 100000
            initial_benchmark = 10000
            
            for i, date in enumerate(dates):
                # Portfolio performance (with some correlation to market)
                market_return = np.random.normal(0.001, 0.02)  # 0.1% daily return, 2% volatility
                portfolio_return = market_return + np.random.normal(0.0005, 0.01)  # Slightly better performance
                
                initial_value *= (1 + portfolio_return)
                initial_benchmark *= (1 + market_return)
                
                portfolio_values.append(initial_value)
                benchmark_values.append(initial_benchmark)
            
            # Create performance chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_values,
                mode='lines',
                name='Portfolio',
                line=dict(color='blue', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=benchmark_values,
                mode='lines',
                name='DSEX Benchmark',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title="Portfolio vs Benchmark Performance",
                xaxis_title="Date",
                yaxis_title="Value (৳)",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                portfolio_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0] * 100
                benchmark_return = (benchmark_values[-1] - benchmark_values[0]) / benchmark_values[0] * 100
                excess_return = portfolio_return - benchmark_return
                
                st.metric("Portfolio Return (30d)", f"{portfolio_return:+.2f}%")
                st.metric("Benchmark Return (30d)", f"{benchmark_return:+.2f}%")
                st.metric("Excess Return", f"{excess_return:+.2f}%")
            
            with col2:
                # Calculate Sharpe ratio (simplified)
                portfolio_returns = np.diff(portfolio_values) / portfolio_values[:-1]
                sharpe_ratio = np.mean(portfolio_returns) / np.std(portfolio_returns) * np.sqrt(252)
                
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
                
                # Calculate maximum drawdown
                peak = np.maximum.accumulate(portfolio_values)
                drawdown = (peak - portfolio_values) / peak * 100
                max_drawdown = np.max(drawdown)
                
                st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
            
            with col3:
                # Calculate volatility
                volatility = np.std(portfolio_returns) * np.sqrt(252) * 100
                st.metric("Volatility (Annual)", f"{volatility:.2f}%")
                
                # Calculate beta (simplified)
                benchmark_returns = np.diff(benchmark_values) / benchmark_values[:-1]
                covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
                benchmark_variance = np.var(benchmark_returns)
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 1
                
                st.metric("Beta", f"{beta:.2f}")
        
        except Exception as e:
            st.error(f"Error rendering performance view: {e}")
    
    def _render_pnl_analysis(self):
        """Render P&L analysis"""
        st.subheader("💰 Profit & Loss Analysis")
        
        try:
            # Calculate realized and unrealized P&L
            realized_pnl = 0
            unrealized_pnl = 0
            
            # Get transactions to calculate realized P&L
            for transaction in st.session_state.transactions:
                if transaction.transaction_type == TransactionType.SELL:
                    # Find corresponding buy transactions to calculate realized P&L
                    # This is a simplified calculation
                    realized_pnl += transaction.total_amount * 0.1  # Placeholder calculation
            
            # Calculate unrealized P&L from current holdings
            for portfolio_item in st.session_state.portfolio_items.values():
                if portfolio_item.quantity > 0:
                    unrealized_pnl += portfolio_item.gain_loss
            
            # Display P&L summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Realized P&L", f"৳{realized_pnl:+,.2f}")
            
            with col2:
                st.metric("Unrealized P&L", f"৳{unrealized_pnl:+,.2f}")
            
            with col3:
                total_pnl = realized_pnl + unrealized_pnl
                st.metric("Total P&L", f"৳{total_pnl:+,.2f}")
            
            # P&L by stock
            st.subheader("P&L by Stock")
            
            pnl_data = []
            for symbol, portfolio_item in st.session_state.portfolio_items.items():
                if portfolio_item.quantity > 0:
                    pnl_data.append({
                        'Symbol': symbol,
                        'Quantity': portfolio_item.quantity,
                        'Avg Cost': f"৳{portfolio_item.average_cost:.2f}",
                        'Current Price': f"৳{portfolio_item.current_price:.2f}",
                        'Unrealized P&L': f"৳{portfolio_item.gain_loss:+,.2f}",
                        'P&L %': f"{portfolio_item.gain_loss_percent:+.2f}%"
                    })
            
            if pnl_data:
                df = pd.DataFrame(pnl_data)
                
                # Sort by P&L (best performers first)
                df['sort_pnl'] = df['Unrealized P&L'].str.replace('৳', '').str.replace(',', '').str.replace('+', '').astype(float)
                df = df.sort_values('sort_pnl', ascending=False)
                
                # Color coding
                def color_pnl(val):
                    if '+' in str(val):
                        return 'color: green'
                    elif '-' in str(val):
                        return 'color: red'
                    return ''
                
                # Create display dataframe without sort column
                display_df = df.drop('sort_pnl', axis=1)
                styled_df = display_df.style.applymap(color_pnl, subset=['Unrealized P&L', 'P&L %'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # P&L distribution chart
                st.subheader("P&L Distribution")

                try:
                    if len(df) > 0 and 'sort_pnl' in df.columns:
                        fig = go.Figure()

                        colors = ['green' if '+' in pnl else 'red' for pnl in df['Unrealized P&L']]

                        fig.add_trace(go.Bar(
                            x=df['Symbol'],
                            y=df['sort_pnl'],
                            marker_color=colors,
                            text=df['P&L %'],
                            textposition='auto'
                        ))

                        fig.update_layout(
                            title="Unrealized P&L by Stock",
                            xaxis_title="Stock Symbol",
                            yaxis_title="P&L (৳)",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data available for P&L chart")
                except Exception as chart_error:
                    st.error(f"Error creating P&L chart: {chart_error}")
                    st.info("Chart data debugging:")
                    st.write("DataFrame columns:", df.columns.tolist())
                    st.write("DataFrame shape:", df.shape)
            
            else:
                st.info("No holdings found for P&L analysis.")
        
        except Exception as e:
            st.error(f"Error rendering P&L analysis: {e}")
    
    def _render_transaction_history(self):
        """Render transaction history"""
        st.subheader("📋 Transaction History")
        
        try:
            if st.session_state.transactions:
                # Display transactions in a table
                transactions_data = []
                for transaction in st.session_state.transactions:
                    transactions_data.append({
                        'Date': transaction.timestamp.strftime('%Y-%m-%d %H:%M'),
                        'Symbol': transaction.symbol,
                        'Type': transaction.transaction_type.value,
                        'Quantity': f"{transaction.quantity:,}",
                        'Price': f"৳{transaction.price:.2f}",
                        'Total': f"৳{transaction.total_amount:,.2f}",
                        'Notes': transaction.notes or ''
                    })
                
                df = pd.DataFrame(transactions_data)
                
                # Sort by date (newest first)
                df = df.sort_values('Date', ascending=False)
                
                # Color coding for transaction types
                def color_transaction_type(val):
                    if val == 'BUY':
                        return 'color: blue'
                    elif val == 'SELL':
                        return 'color: red'
                    return ''
                
                styled_df = df.style.applymap(color_transaction_type, subset=['Type'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # Transaction summary
                st.subheader("Transaction Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                total_transactions = len(st.session_state.transactions)
                buy_transactions = len([t for t in st.session_state.transactions if t.transaction_type == TransactionType.BUY])
                sell_transactions = len([t for t in st.session_state.transactions if t.transaction_type == TransactionType.SELL])
                
                total_buy_amount = sum(t.total_amount for t in st.session_state.transactions if t.transaction_type == TransactionType.BUY)
                total_sell_amount = sum(t.total_amount for t in st.session_state.transactions if t.transaction_type == TransactionType.SELL)
                
                with col1:
                    st.metric("Total Transactions", total_transactions)
                
                with col2:
                    st.metric("Buy Orders", buy_transactions)
                
                with col3:
                    st.metric("Total Buy Amount", f"৳{total_buy_amount:,.2f}")
                
                with col4:
                    st.metric("Total Sell Amount", f"৳{total_sell_amount:,.2f}")
                
                # Transaction volume chart
                if len(st.session_state.transactions) > 1:
                    st.subheader("Transaction Volume Over Time")
                    
                    # Group transactions by date
                    transaction_df = pd.DataFrame(transactions_data)
                    transaction_df['Date'] = pd.to_datetime(transaction_df['Date'])
                    transaction_df['Date_only'] = transaction_df['Date'].dt.date
                    
                    daily_transactions = transaction_df.groupby('Date_only').agg({
                        'Total': 'count',
                        'Symbol': lambda x: len(x.unique())
                    }).reset_index()
                    
                    daily_transactions.columns = ['Date', 'Transaction Count', 'Unique Stocks']
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=daily_transactions['Date'],
                        y=daily_transactions['Transaction Count'],
                        name='Transactions',
                        marker_color='lightblue'
                    ))
                    
                    fig.update_layout(
                        title="Daily Transaction Activity",
                        xaxis_title="Date",
                        yaxis_title="Number of Transactions",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No transactions found. Add some transactions to see your trading history.")
        
        except Exception as e:
            st.error(f"Error rendering transaction history: {e}")

    def _render_reset_tab(self):
        """Render the reset data tab"""
        st.subheader("🗑️ Reset Portfolio Data")

        # Show current data summary
        self._show_data_summary()

        # Render the reset component
        self.reset_component.render(
            title="Reset All Portfolio Data",
            location="portfolio",
            compact=False,
            button_key="portfolio_reset"
        )

    def _show_data_summary(self):
        """Show summary of current data that will be reset"""
        st.info("📊 **Current Data Summary**")

        col1, col2, col3 = st.columns(3)

        with col1:
            transaction_count = len(st.session_state.get('transactions', []))
            st.metric("Total Transactions", transaction_count)

        with col2:
            portfolio_items = st.session_state.get('portfolio_items', {})
            holdings_count = len([item for item in portfolio_items.values() if item.quantity > 0])
            st.metric("Active Holdings", holdings_count)

        with col3:
            total_value = sum(item.current_value for item in portfolio_items.values() if item.quantity > 0)
            st.metric("Portfolio Value", f"৳{total_value:,.2f}")
