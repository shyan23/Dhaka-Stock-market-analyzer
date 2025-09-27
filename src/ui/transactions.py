import streamlit as st
import uuid
from datetime import datetime
from typing import List, Optional
from src.models.portfolio import Transaction, TransactionType, PortfolioItem
from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager

class TransactionsUI:
    def __init__(self, dse_api: DSEAPIService, data_manager: DataManager):
        self.dse_api = dse_api
        self.data_manager = data_manager
    
    def render(self):
        """Render the transactions page"""
        st.title("💹 Transaction Management")
        
        # Tabs for different transaction views
        tab1, tab2, tab3 = st.tabs(["➕ New Transaction", "📊 Quick Trade", "📋 Transaction Log"])
        
        with tab1:
            self._render_new_transaction()
        
        with tab2:
            self._render_quick_trade()
        
        with tab3:
            self._render_transaction_log()
    
    def _render_new_transaction(self):
        """Render new transaction form"""
        st.subheader("➕ Record New Transaction")
        
        # Transaction form
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock selection
                if st.session_state.selected_stocks:
                    symbol = st.selectbox(
                        "Select Stock:",
                        options=[""] + st.session_state.selected_stocks,
                        key="transaction_symbol"
                    )
                else:
                    st.warning("No stocks selected for tracking. Please go to Stock Selector to add stocks.")
                    symbol = None
                
                # Transaction type
                transaction_type = st.selectbox(
                    "Transaction Type:",
                    options=[TransactionType.BUY, TransactionType.SELL],
                    format_func=lambda x: x.value,
                    key="transaction_type"
                )
                
                # Quantity
                quantity = st.number_input(
                    "Quantity:",
                    min_value=1,
                    value=1,
                    step=1,
                    key="transaction_quantity"
                )
            
            with col2:
                # Get current price for selected stock
                current_stock_price = 0.01
                if symbol:
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    if stock and stock.current_price > 0:
                        current_stock_price = stock.current_price

                # Price
                price = st.number_input(
                    "Price per Share (৳):",
                    min_value=0.01,
                    value=current_stock_price,
                    step=0.01,
                    format="%.2f",
                    key="transaction_price"
                )

                # Current price display and suggestions
                if symbol:
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    if stock:
                        st.info(f"📊 Current LTP: ৳{stock.current_price:.2f}")

                        # Quick price buttons
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("Use LTP", key="use_ltp"):
                                st.session_state.transaction_price = stock.current_price
                                st.rerun()
                        with col_b:
                            if st.button("-5%", key="price_minus_5"):
                                st.session_state.transaction_price = stock.current_price * 0.95
                                st.rerun()
                        with col_c:
                            if st.button("+5%", key="price_plus_5"):
                                st.session_state.transaction_price = stock.current_price * 1.05
                                st.rerun()

                        # Price validation
                        price_diff = abs(price - stock.current_price) if price > 0 else 0
                        price_diff_percent = (price_diff / stock.current_price * 100) if stock.current_price > 0 else 0

                        if price > 0 and price_diff_percent > 10:  # 10% difference threshold
                            st.warning(f"⚠️ Price differs by {price_diff_percent:.1f}% from current LTP")
                        elif price > 0 and price_diff_percent > 5:
                            st.info(f"ℹ️ Price differs by {price_diff_percent:.1f}% from current LTP")
                    else:
                        st.error(f"❌ Could not fetch current price for {symbol}")
                
                # Notes
                notes = st.text_area(
                    "Notes (optional):",
                    placeholder="Add any notes about this transaction...",
                    key="transaction_notes"
                )
            
            # Holdings validation for sell transactions
            if symbol and transaction_type == TransactionType.SELL:
                portfolio_item = st.session_state.portfolio_items.get(symbol)
                if not portfolio_item or portfolio_item.quantity < quantity:
                    available_qty = portfolio_item.quantity if portfolio_item else 0
                    st.error(f"❌ Insufficient holdings! You have {available_qty} shares of {symbol}, trying to sell {quantity}")
                    can_proceed = False
                else:
                    st.success(f"✅ You have {portfolio_item.quantity} shares of {symbol}")
                    can_proceed = True
            else:
                can_proceed = True
            
            # Submit button with validation info
            submit_disabled = not can_proceed or not symbol or quantity <= 0 or price <= 0

            if submit_disabled:
                if not symbol:
                    st.error("⚠️ Please select a stock")
                elif quantity <= 0:
                    st.error("⚠️ Quantity must be greater than 0")
                elif price <= 0:
                    st.error("⚠️ Price must be greater than 0")
                elif not can_proceed:
                    st.error("⚠️ Cannot proceed with this transaction")

            submitted = st.form_submit_button(
                "💾 Record Transaction",
                type="primary",
                disabled=submit_disabled,
                help="All fields must be filled correctly to record transaction"
            )
            
            if submitted:
                self._process_transaction(symbol, transaction_type, quantity, price, notes)
    
    def _render_quick_trade(self):
        """Render quick trade interface"""
        st.subheader("📊 Quick Trade")
        st.markdown("Quick buy/sell interface for tracked stocks")
        
        if not st.session_state.selected_stocks:
            st.warning("No stocks selected for tracking. Please go to Stock Selector to add stocks.")
            return
        
        # Create quick trade cards for each stock
        for symbol in st.session_state.selected_stocks:
            with st.expander(f"🔹 {symbol}", expanded=False):
                try:
                    # Get current stock data
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    if not stock:
                        st.error(f"Could not fetch data for {symbol}")
                        continue
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.write(f"**{stock.name}**")
                        st.write(f"LTP: ৳{stock.current_price:.2f}")
                        st.write(f"Change: {stock.price_change_percent:+.2f}%")
                    
                    with col2:
                        # Current holdings
                        portfolio_item = st.session_state.portfolio_items.get(symbol)
                        current_holdings = portfolio_item.quantity if portfolio_item else 0
                        st.write(f"**Holdings:** {current_holdings:,}")
                        
                        if portfolio_item and portfolio_item.quantity > 0:
                            st.write(f"Avg Cost: ৳{portfolio_item.average_cost:.2f}")
                            st.write(f"P&L: {portfolio_item.gain_loss_percent:+.2f}%")
                    
                    with col3:
                        # Quick buy
                        st.write("**Quick Buy**")
                        buy_qty = st.number_input(
                            "Quantity",
                            min_value=1,
                            value=1,
                            step=1,
                            key=f"quick_buy_qty_{symbol}"
                        )
                        
                        if st.button("🟢 Buy", key=f"quick_buy_{symbol}"):
                            self._process_transaction(
                                symbol, 
                                TransactionType.BUY, 
                                buy_qty, 
                                stock.current_price,
                                "Quick buy"
                            )
                    
                    with col4:
                        # Quick sell
                        st.write("**Quick Sell**")
                        sell_qty = st.number_input(
                            "Quantity",
                            min_value=1,
                            max_value=current_holdings,
                            value=min(1, current_holdings),
                            step=1,
                            key=f"quick_sell_qty_{symbol}"
                        )
                        
                        if st.button(
                            "🔴 Sell", 
                            key=f"quick_sell_{symbol}",
                            disabled=current_holdings == 0
                        ):
                            if current_holdings >= sell_qty:
                                self._process_transaction(
                                    symbol, 
                                    TransactionType.SELL, 
                                    sell_qty, 
                                    stock.current_price,
                                    "Quick sell"
                                )
                            else:
                                st.error("Insufficient holdings!")
                    
                    with col5:
                        # Market info
                        st.write("**Market Info**")
                        st.write(f"High: ৳{stock.high:.2f}" if stock.high else "High: N/A")
                        st.write(f"Low: ৳{stock.low:.2f}" if stock.low else "Low: N/A")
                        st.write(f"Volume: {stock.volume:,}")
                
                except Exception as e:
                    st.error(f"Error loading data for {symbol}: {e}")
    
    def _render_transaction_log(self):
        """Render transaction log with filtering options"""
        st.subheader("📋 Transaction Log")
        
        if not st.session_state.transactions:
            st.info("No transactions recorded yet.")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filter by symbol
            all_symbols = list(set(t.symbol for t in st.session_state.transactions))
            selected_symbol = st.selectbox(
                "Filter by Stock:",
                options=["All"] + all_symbols,
                key="log_symbol_filter"
            )
        
        with col2:
            # Filter by transaction type
            transaction_type_filter = st.selectbox(
                "Filter by Type:",
                options=["All", "BUY", "SELL"],
                key="log_type_filter"
            )
        
        with col3:
            # Sort options
            sort_option = st.selectbox(
                "Sort by:",
                options=["Date (Newest)", "Date (Oldest)", "Symbol", "Amount"],
                key="log_sort_option"
            )
        
        # Apply filters
        filtered_transactions = st.session_state.transactions.copy()
        
        if selected_symbol != "All":
            filtered_transactions = [t for t in filtered_transactions if t.symbol == selected_symbol]
        
        if transaction_type_filter != "All":
            filtered_transactions = [t for t in filtered_transactions if t.transaction_type.value == transaction_type_filter]
        
        # Apply sorting
        if sort_option == "Date (Newest)":
            filtered_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        elif sort_option == "Date (Oldest)":
            filtered_transactions.sort(key=lambda x: x.timestamp)
        elif sort_option == "Symbol":
            filtered_transactions.sort(key=lambda x: x.symbol)
        elif sort_option == "Amount":
            filtered_transactions.sort(key=lambda x: x.total_amount, reverse=True)
        
        # Display transactions
        if filtered_transactions:
            st.write(f"Showing {len(filtered_transactions)} transactions")
            
            for i, transaction in enumerate(filtered_transactions):
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 2, 1])
                    
                    with col1:
                        st.write(transaction.timestamp.strftime('%m/%d'))
                    
                    with col2:
                        st.write(transaction.symbol)
                    
                    with col3:
                        color = "🟢" if transaction.transaction_type == TransactionType.BUY else "🔴"
                        st.write(f"{color} {transaction.transaction_type.value}")
                    
                    with col4:
                        st.write(f"{transaction.quantity:,}")
                    
                    with col5:
                        st.write(f"৳{transaction.price:.2f} × {transaction.quantity:,} = ৳{transaction.total_amount:,.2f}")
                        if transaction.notes:
                            st.caption(transaction.notes)
                    
                    with col6:
                        if st.button("🗑️", key=f"delete_{transaction.id}", help="Delete transaction"):
                            if st.button("Confirm", key=f"confirm_delete_{transaction.id}"):
                                self._delete_transaction(transaction.id)
                                st.rerun()
                    
                    if i < len(filtered_transactions) - 1:
                        st.divider()
        else:
            st.info("No transactions match the selected filters.")
    
    def _process_transaction(self, symbol: str, transaction_type: TransactionType, quantity: int, price: float, notes: str):
        """Process a new transaction"""
        try:
            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                symbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                price=price,
                timestamp=datetime.now(),
                notes=notes
            )
            
            # Add to transactions list
            st.session_state.transactions.append(transaction)
            
            # Update portfolio
            self._update_portfolio(transaction)
            
            # Save to data manager
            self.data_manager.save_transaction(transaction)
            
            # Success message
            st.success(f"✅ {transaction_type.value} transaction recorded for {symbol}")
            
            # Show transaction details
            st.info(f"""
            **Transaction Details:**
            - Symbol: {symbol}
            - Type: {transaction_type.value}
            - Quantity: {quantity:,}
            - Price: ৳{price:.2f}
            - Total: ৳{transaction.total_amount:,.2f}
            - Time: {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            st.rerun()
        
        except Exception as e:
            st.error(f"Error processing transaction: {e}")
    
    def _update_portfolio(self, transaction: Transaction):
        """Update portfolio based on transaction"""
        symbol = transaction.symbol
        current_item = st.session_state.portfolio_items.get(symbol)
        
        if transaction.transaction_type == TransactionType.BUY:
            if current_item:
                # Update existing holding
                total_quantity = current_item.quantity + transaction.quantity
                total_cost = current_item.total_cost + transaction.total_amount
                new_avg_cost = total_cost / total_quantity
                
                current_item.quantity = total_quantity
                current_item.average_cost = new_avg_cost
            else:
                # Create new holding
                stock = self.dse_api.get_stock_by_symbol(symbol)
                current_price = stock.current_price if stock else transaction.price
                
                st.session_state.portfolio_items[symbol] = PortfolioItem(
                    symbol=symbol,
                    quantity=transaction.quantity,
                    average_cost=transaction.price,
                    current_price=current_price,
                    last_updated=datetime.now()
                )
        
        elif transaction.transaction_type == TransactionType.SELL:
            if current_item and current_item.quantity >= transaction.quantity:
                # Update existing holding
                current_item.quantity -= transaction.quantity
                
                # If all shares sold, remove from portfolio
                if current_item.quantity == 0:
                    del st.session_state.portfolio_items[symbol]
            else:
                st.error(f"Error: Trying to sell {transaction.quantity} shares but only have {current_item.quantity if current_item else 0}")
    
    def _delete_transaction(self, transaction_id: str):
        """Delete a transaction"""
        try:
            # Find and remove transaction
            transaction_to_remove = None
            for transaction in st.session_state.transactions:
                if transaction.id == transaction_id:
                    transaction_to_remove = transaction
                    break
            
            if transaction_to_remove:
                st.session_state.transactions.remove(transaction_to_remove)
                st.success("Transaction deleted successfully!")
                
                # Note: In a real application, you would need to recalculate portfolio
                # based on remaining transactions. For simplicity, we're not doing that here.
            else:
                st.error("Transaction not found!")
        
        except Exception as e:
            st.error(f"Error deleting transaction: {e}")
