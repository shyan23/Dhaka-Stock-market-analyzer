import streamlit as st
import uuid
from datetime import datetime
from typing import List, Optional
from src.models.portfolio import Transaction, TransactionType, PortfolioItem
from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager
from src.ui.components.reset_component import create_reset_component

class TransactionsUI:
    def __init__(self, dse_api: DSEAPIService, data_manager: DataManager):
        self.dse_api = dse_api
        self.data_manager = data_manager
        self.reset_component = create_reset_component(data_manager)
    
    def render(self):
        """Render the transactions page"""
        st.title("💹 Transaction Management")
        
        # Tabs for different transaction views
        tab1, tab2, tab3, tab4 = st.tabs(["➕ New Transaction", "📊 Quick Trade", "📋 Transaction Log", "🗑️ Reset Data"])

        with tab1:
            self._render_new_transaction()

        with tab2:
            self._render_quick_trade()

        with tab3:
            self._render_transaction_log()

        with tab4:
            self._render_reset_tab()
    
    def _render_new_transaction(self):
        """Render new transaction form"""
        st.subheader("➕ Record New Transaction")

        # Initialize cash balance if not exists
        if 'cash_balance' not in st.session_state:
            st.session_state.cash_balance = st.session_state.portfolio_settings.get('initial_fund', 100000.0)

        # Cash Management Section
        col_cash1, col_cash2, col_cash3 = st.columns([2, 1, 1])
        with col_cash1:
            st.metric("💰 Available Cash", f"৳{st.session_state.cash_balance:,.2f}")
        with col_cash2:
            if st.button("💵 Deposit Cash", key="deposit_cash_btn"):
                st.session_state.show_deposit_form = True
        with col_cash3:
            if st.button("📊 Cash History", key="cash_history_btn"):
                st.session_state.show_cash_history = True

        # Deposit cash form
        if st.session_state.get('show_deposit_form', False):
            with st.form("deposit_form"):
                st.subheader("💵 Deposit Cash")
                deposit_amount = st.number_input(
                    "Deposit Amount (৳):",
                    min_value=100.0,
                    value=10000.0,
                    step=1000.0,
                    format="%.2f"
                )
                deposit_note = st.text_input("Note (optional):", placeholder="e.g., Monthly investment")

                col_dep1, col_dep2 = st.columns(2)
                with col_dep1:
                    if st.form_submit_button("💾 Deposit", type="primary"):
                        st.session_state.cash_balance += deposit_amount
                        # Log the deposit
                        if 'cash_transactions' not in st.session_state:
                            st.session_state.cash_transactions = []
                        st.session_state.cash_transactions.append({
                            'type': 'DEPOSIT',
                            'amount': deposit_amount,
                            'note': deposit_note,
                            'timestamp': datetime.now(),
                            'balance': st.session_state.cash_balance
                        })
                        st.success(f"✅ Deposited ৳{deposit_amount:,.2f}")
                        st.session_state.show_deposit_form = False
                        st.rerun()
                with col_dep2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_deposit_form = False
                        st.rerun()

        # Price suggestion buttons (outside form)
        selected_symbol = st.session_state.get('temp_transaction_symbol', '')
        if selected_symbol and st.session_state.selected_stocks and selected_symbol in st.session_state.selected_stocks:
            stock = self.dse_api.get_stock_by_symbol(selected_symbol)
            if stock:
                st.info(f"📊 Current LTP for {selected_symbol}: ৳{stock.current_price:.2f}")

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

        # Transaction form
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock selection
                if st.session_state.selected_stocks:
                    symbol = st.selectbox(
                        "Select Stock:",
                        options=st.session_state.selected_stocks,
                        key="transaction_symbol"
                    )
                    # Store in temp variable for price suggestions (without callback)
                    if symbol:
                        st.session_state.temp_transaction_symbol = symbol
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
                current_stock_price = st.session_state.get('transaction_price', 0.01)
                if symbol:
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    if stock and stock.current_price > 0 and current_stock_price == 0.01:
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

                # Price validation (simplified, no buttons inside form)
                if symbol:
                    stock = self.dse_api.get_stock_by_symbol(symbol)
                    if stock:
                        price_diff = abs(price - stock.current_price) if price > 0 else 0
                        price_diff_percent = (price_diff / stock.current_price * 100) if stock.current_price > 0 else 0

                        if price > 0 and price_diff_percent > 10:  # 10% difference threshold
                            st.warning(f"⚠️ Price differs by {price_diff_percent:.1f}% from current LTP")
                        elif price > 0 and price_diff_percent > 5:
                            st.info(f"ℹ️ Price differs by {price_diff_percent:.1f}% from current LTP")
                    else:
                        st.error(f"❌ Could not fetch current price for {symbol}")
                
                # Transaction Date
                transaction_date = st.date_input(
                    "Transaction Date:",
                    value=datetime.now().date(),
                    max_value=datetime.now().date(),
                    key="transaction_date",
                    help="Select the date when the transaction occurred"
                )

                # Brokerage Fee
                st.write("**Brokerage & Fees:**")
                col_fee1, col_fee2 = st.columns(2)
                with col_fee1:
                    brokerage_type = st.selectbox(
                        "Fee Type:",
                        options=["Percentage", "Fixed Amount"],
                        key="brokerage_type",
                        help="Choose between percentage-based or fixed fee"
                    )
                with col_fee2:
                    if brokerage_type == "Percentage":
                        brokerage_rate = st.number_input(
                            "Brokerage Rate (%):",
                            min_value=0.0,
                            max_value=5.0,
                            value=0.5,
                            step=0.1,
                            format="%.2f",
                            key="brokerage_rate",
                            help="Typical rate: 0.3-0.5%"
                        )
                        brokerage_fee = (price * quantity * brokerage_rate / 100) if price > 0 and quantity > 0 else 0
                    else:
                        brokerage_fee = st.number_input(
                            "Fixed Fee (৳):",
                            min_value=0.0,
                            value=50.0,
                            step=10.0,
                            format="%.2f",
                            key="brokerage_fee",
                            help="Fixed brokerage fee amount"
                        )

                if brokerage_fee > 0:
                    st.info(f"💰 Brokerage Fee: ৳{brokerage_fee:.2f}")

                # Notes
                notes = st.text_area(
                    "Notes (optional):",
                    placeholder="Add any notes about this transaction...",
                    key="transaction_notes"
                )
            
            # Cash balance and holdings validation
            can_proceed = True
            total_cost = (price * quantity) + brokerage_fee

            # For buy transactions, check cash balance
            if symbol and transaction_type == TransactionType.BUY:
                if total_cost > st.session_state.cash_balance:
                    st.error(f"❌ Insufficient cash! Need ৳{total_cost:,.2f} but only have ৳{st.session_state.cash_balance:,.2f}")
                    st.info(f"💡 You need ৳{total_cost - st.session_state.cash_balance:,.2f} more. Use 'Deposit Cash' button above.")
                    can_proceed = False
                else:
                    st.success(f"✅ Sufficient cash available. Cost: ৳{total_cost:,.2f}")

            # For sell transactions, check holdings
            elif symbol and transaction_type == TransactionType.SELL:
                portfolio_item = st.session_state.portfolio_items.get(symbol)
                if not portfolio_item or portfolio_item.quantity < quantity:
                    available_qty = portfolio_item.quantity if portfolio_item else 0
                    st.error(f"❌ Insufficient holdings! You have {available_qty} shares of {symbol}, trying to sell {quantity}")
                    can_proceed = False
                else:
                    proceeds = (price * quantity) - brokerage_fee
                    st.success(f"✅ You have {portfolio_item.quantity} shares of {symbol}. Proceeds: ৳{proceeds:,.2f}")

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
                # Convert date to datetime
                transaction_datetime = datetime.combine(transaction_date, datetime.now().time())
                self._process_transaction(symbol, transaction_type, quantity, price, notes, transaction_datetime, brokerage_fee)
    
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
    
    def _process_transaction(self, symbol: str, transaction_type: TransactionType, quantity: int, price: float, notes: str, transaction_datetime: datetime = None, brokerage_fee: float = 0.0):
        """Process a new transaction with cash management and brokerage fees"""
        try:
            # Calculate total costs/proceeds
            base_amount = price * quantity

            if transaction_type == TransactionType.BUY:
                total_cost = base_amount + brokerage_fee
                # Check cash balance one more time
                if total_cost > st.session_state.cash_balance:
                    st.error(f"❌ Insufficient cash for transaction!")
                    return
                # Deduct from cash
                st.session_state.cash_balance -= total_cost
            else:  # SELL
                proceeds = base_amount - brokerage_fee
                # Add to cash
                st.session_state.cash_balance += proceeds

            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                symbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                price=price,
                timestamp=transaction_datetime or datetime.now(),
                notes=f"{notes}\nBrokerage Fee: ৳{brokerage_fee:.2f}" if brokerage_fee > 0 else notes
            )

            # Add to transactions list
            st.session_state.transactions.append(transaction)

            # Update portfolio
            self._update_portfolio(transaction)

            # Save to data manager
            self.data_manager.save_transaction(transaction)

            # Log cash transaction
            if 'cash_transactions' not in st.session_state:
                st.session_state.cash_transactions = []

            cash_type = "BUY" if transaction_type == TransactionType.BUY else "SELL"
            amount = -total_cost if transaction_type == TransactionType.BUY else proceeds

            st.session_state.cash_transactions.append({
                'type': cash_type,
                'amount': amount,
                'note': f"{symbol} - {quantity:,} shares @ ৳{price:.2f}",
                'timestamp': transaction_datetime or datetime.now(),
                'balance': st.session_state.cash_balance,
                'brokerage_fee': brokerage_fee
            })

            # Success message
            st.success(f"✅ {transaction_type.value} transaction recorded for {symbol}")

            # Show transaction details
            if transaction_type == TransactionType.BUY:
                st.info(f"""
                **Transaction Details:**
                - Symbol: {symbol}
                - Type: {transaction_type.value}
                - Quantity: {quantity:,}
                - Price: ৳{price:.2f}
                - Subtotal: ৳{base_amount:,.2f}
                - Brokerage Fee: ৳{brokerage_fee:.2f}
                - Total Cost: ৳{total_cost:,.2f}
                - Remaining Cash: ৳{st.session_state.cash_balance:,.2f}
                - Time: {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                """)
            else:
                st.info(f"""
                **Transaction Details:**
                - Symbol: {symbol}
                - Type: {transaction_type.value}
                - Quantity: {quantity:,}
                - Price: ৳{price:.2f}
                - Subtotal: ৳{base_amount:,.2f}
                - Brokerage Fee: ৳{brokerage_fee:.2f}
                - Net Proceeds: ৳{proceeds:,.2f}
                - Total Cash: ৳{st.session_state.cash_balance:,.2f}
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

    def _render_reset_tab(self):
        """Render the reset data tab"""
        st.subheader("🗑️ Reset Transaction Data")

        # Show current transaction summary
        self._show_transaction_summary()

        # Render the reset component
        self.reset_component.render(
            title="Reset All Transaction Data",
            location="transactions",
            compact=False,
            button_key="transactions_reset"
        )

    def _show_transaction_summary(self):
        """Show summary of current transaction data that will be reset"""
        st.info("📊 **Current Transaction Summary**")

        transactions = st.session_state.get('transactions', [])
        portfolio_items = st.session_state.get('portfolio_items', {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Transactions", len(transactions))

        with col2:
            buy_transactions = len([t for t in transactions if t.transaction_type == TransactionType.BUY])
            st.metric("Buy Orders", buy_transactions)

        with col3:
            sell_transactions = len([t for t in transactions if t.transaction_type == TransactionType.SELL])
            st.metric("Sell Orders", sell_transactions)

        with col4:
            active_holdings = len([item for item in portfolio_items.values() if item.quantity > 0])
            st.metric("Active Holdings", active_holdings)

        # Show total investment amounts
        if transactions:
            col1, col2, col3 = st.columns(3)

            with col1:
                total_buy_amount = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.BUY)
                st.metric("Total Buy Amount", f"৳{total_buy_amount:,.2f}")

            with col2:
                total_sell_amount = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.SELL)
                st.metric("Total Sell Amount", f"৳{total_sell_amount:,.2f}")

            with col3:
                net_investment = total_buy_amount - total_sell_amount
                st.metric("Net Investment", f"৳{net_investment:,.2f}")

        else:
            st.info("No transactions found to display summary.")
