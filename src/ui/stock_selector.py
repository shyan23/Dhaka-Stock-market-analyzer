import streamlit as st
import pandas as pd
from datetime import datetime
from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager
import difflib
class StockSelectorUI:
    def __init__(self, dse_api: DSEAPIService, data_manager: DataManager):
        self.dse_api = dse_api
        self.data_manager = data_manager
    
    def render(self):
        """Render the stock selector page"""
        st.title("🔍 Stock Selector")
        st.markdown("Select stocks to track in your portfolio")
        
        # Search and select stocks
        self._render_stock_search()
        
        st.markdown("---")
        
        # Display selected stocks
        self._render_selected_stocks()
        
        # Display top 30 stocks
        self._render_top30_stocks()
    
    def _render_stock_search(self):
        """Render improved stock search interface"""
        st.subheader("🔍 Search Stocks")

        # Search input with real-time search
        search_query = st.text_input(
            "Search by company name or trading code",
            placeholder="e.g., Grameenphone, GP, BRAC Bank, BRACBANK, Square",
            key="stock_search_input"
        )

        # Auto-search when user types (with minimum 2 characters)
        if search_query and len(search_query.strip()) >= 2:
            with st.spinner("🔍 Searching stocks..."):
                self._display_search_results(search_query.strip())
        elif search_query and len(search_query.strip()) < 2:
            st.info("💡 Type at least 2 characters to search")
        elif not search_query:
            # Show helpful search examples when input is empty
            st.info("🔍 **Search examples:**\n"
                   "- Stock symbol: `GP`, `BRAC`, `ACI`\n"
                   "- Company name: `Grameenphone`, `Unilever`\n"
                   "- Partial matches: `UNI`, `BANK`, `PHARMA`")

        st.markdown("---")

        # Quick add popular stocks
        st.subheader("⚡ Quick Add Popular Stocks")
        st.caption("Click any stock below to add it to your tracking list")
        
        popular_stocks = [
            ("GP", "Grameenphone Ltd", "Telecommunications"),
            ("BRACBANK", "BRAC Bank Limited", "Banking"),
            ("SQUARETEXT", "Square Textiles Ltd", "Textiles"),
            ("ACI", "ACI Limited", "Pharmaceuticals"),
            ("BEXIMCO", "Beximco Pharmaceuticals Ltd", "Pharmaceuticals"),
            ("ORIONPHARM", "Orion Pharma Ltd", "Pharmaceuticals"),
            ("RENATA", "Renata Limited", "Pharmaceuticals"),
            ("UNION", "Union Capital Limited", "Banking"),
            ("NBL", "National Bank Limited", "Banking"),
            ("EBL", "Eastern Bank Limited", "Banking")
        ]

        # Display popular stocks in a more attractive grid
        for i in range(0, len(popular_stocks), 5):
            cols = st.columns(5)
            for j in range(5):
                if i + j < len(popular_stocks):
                    symbol, name, sector = popular_stocks[i + j]
                    with cols[j]:
                        # Check if already selected
                        is_selected = symbol in st.session_state.selected_stocks

                        if is_selected:
                            st.success(f"✅ {symbol}")
                            st.caption(f"{name[:20]}...")
                        else:
                            if st.button(
                                f"➕ {symbol}",
                                help=f"{name} | {sector}",
                                key=f"quick_add_{symbol}",
                                use_container_width=True
                            ):
                                self._add_stock_to_tracking(symbol, name)
                            st.caption(f"{name[:20]}...")
    


    def _display_search_results(self, query: str):
        """Display improved search results with case-insensitivity and suggestions"""
        try:
            import time
            start_time = time.time()

            # Always ship uppercased query to the server
            query_upper = query.upper()
            search_results = self.dse_api.search_stocks(query_upper)
            search_time = time.time() - start_time

            if search_results:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"🔍 Search Results for '{query}'")
                with col2:
                    st.caption(f"⚡ {search_time:.2f}s")

                st.caption(f"Found {len(search_results)} matching stocks")

                for idx, result in enumerate(search_results[:10]):  # Limit to 10
                    symbol = result.get('symbol', result.get('trading_code', '')).upper()
                    name = result.get('name', symbol)
                    price = result.get('last_trade_price', 0)
                    details_available = result.get('details_available', False)

                    is_selected = symbol in st.session_state.selected_stocks
                    is_exact_match = symbol == query_upper
                    border_style = "border-left: 4px solid #00D100;" if is_exact_match else "border-left: 4px solid #1f77b4;"

                    with st.container():
                        st.markdown(f"""
                        <div style="{border_style} padding: 10px; margin: 5px 0; background-color: {'#f0f8f0' if is_selected else '#f9f9f9'}; border-radius: 5px;">
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1, 1])

                        with col1:
                            if is_exact_match:
                                st.markdown(f"🎯 **{symbol}**")
                            else:
                                st.markdown(f"**{symbol}**")

                        with col2:
                            display_name = name if name != symbol else "N/A"
                            st.write(display_name)

                        with col3:
                            if price > 0:
                                st.metric("", f"৳{price:.2f}")
                            else:
                                st.write("N/A")

                        with col4:
                            st.write("📊" if details_available else "📈")

                        with col5:
                            if is_selected:
                                st.success("✅")
                            else:
                                if st.button(
                                    "➕",
                                    key=f"search_add_{idx}_{symbol}",
                                    help=f"Add {symbol} to tracking",
                                    use_container_width=True
                                ):
                                    self._add_stock_to_tracking(symbol, name)

                if len(search_results) > 10:
                    st.info(f"💡 Showing top 10 results. Found {len(search_results)} total matches. Try a more specific search.")

            else:
                # No results → show suggestion
                all_symbols = self.dse_api.get_all_symbols()  # you must expose this in your API/service
                suggestions = difflib.get_close_matches(query_upper, all_symbols, n=3, cutoff=0.6)

                st.warning(f"❌ No stocks found for '{query}'")

                if suggestions:
                    st.info(f"💡 Did you mean: {', '.join(suggestions)} ?")
                else:
                    st.info("💡 Try searching with:\n- Stock symbol (e.g., GP, BRAC)\n- Company name (e.g., Grameenphone, Bank)\n- Partial matches work too!")

        except Exception as e:
            st.error(f"❌ Error searching stocks: {e}")
            st.info("💡 Please try again or check your connection.")


    def _add_stock_to_tracking(self, symbol: str, name: str = ""):
        """Helper function to add stock to tracking list"""
        if symbol not in st.session_state.selected_stocks:
            st.session_state.selected_stocks.append(symbol)

            # Save to persistent storage
            # Save to persistent storage
            self.data_manager.save_user_selected_stocks(st.session_state.selected_stocks)

            display_name = f"{symbol} ({name})" if name and name != symbol else symbol
            st.success(f"✅ Added {display_name} to tracking list!")
            st.balloons()  # Fun UX touch
            st.rerun()
        else:
            st.warning(f"⚠️ {symbol} is already being tracked")
    
    def _render_selected_stocks(self):
        """Render currently selected stocks with improved UX"""
        if st.session_state.selected_stocks:
            # Header with stock count
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"📊 Currently Tracking ({len(st.session_state.selected_stocks)} stocks)")
            with col2:
                if st.button("🔄 Refresh Prices", help="Refresh all stock prices"):
                    st.rerun()

            # Quick management options
            with st.expander("🛠️ Manage Tracked Stocks"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("📤 Export List", help="Export tracked stocks list"):
                        stock_list = "\n".join(st.session_state.selected_stocks)
                        st.download_button(
                            label="Download as TXT",
                            data=stock_list,
                            file_name=f"tracked_stocks_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )

                with col2:
                    if st.button("🗑️ Clear All", help="Remove all tracked stocks"):
                        if st.button("⚠️ Confirm Clear All", key="confirm_clear_all"):
                            st.session_state.selected_stocks = []
                            # Save to persistent storage
                            self.data_manager.save_user_selected_stocks(st.session_state.selected_stocks)
                            st.success("All stocks removed from tracking!")
                            st.rerun()

                with col3:
                    # Bulk remove selection
                    remove_symbols = st.multiselect(
                        "Select stocks to remove:",
                        st.session_state.selected_stocks,
                        key="bulk_remove"
                    )
                    if remove_symbols and st.button("🗑️ Remove Selected"):
                        for symbol in remove_symbols:
                            if symbol in st.session_state.selected_stocks:
                                st.session_state.selected_stocks.remove(symbol)
                        # Save to persistent storage
                        self.data_manager.save_user_selected_stocks(st.session_state.selected_stocks)
                        st.success(f"Removed {len(remove_symbols)} stocks from tracking!")
                        st.rerun()

            # Get current prices for selected stocks
            if st.button("🔍 Show Details", key="show_details"):
                with st.spinner("🔄 Fetching latest prices..."):
                    self._display_tracked_stocks_table()
            else:
                # Show compact grid view by default
                self._display_tracked_stocks_grid()
        else:
            st.info("📝 No stocks currently being tracked. Use the search above or quick-add buttons to start tracking stocks.")

    def _display_tracked_stocks_grid(self):
        """Display tracked stocks in a compact grid format"""
        # Show stocks in a compact grid (4 per row)
        stocks_per_row = 4
        for i in range(0, len(st.session_state.selected_stocks), stocks_per_row):
            cols = st.columns(stocks_per_row)
            for j in range(stocks_per_row):
                if i + j < len(st.session_state.selected_stocks):
                    symbol = st.session_state.selected_stocks[i + j]
                    with cols[j]:
                        try:
                            stock = self.dse_api.get_stock_by_symbol(symbol)
                            if stock:
                                # Color based on price change
                                change_color = "🟢" if stock.price_change >= 0 else "🔴"

                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; text-align: center;">
                                    <h4>{symbol}</h4>
                                    <p><strong>৳{stock.current_price:.2f}</strong></p>
                                    <p>{change_color} {stock.price_change:+.2f} ({stock.price_change_percent:+.2f}%)</p>
                                    <small>{stock.name[:20]}...</small>
                                </div>
                                """, unsafe_allow_html=True)

                                # Quick remove button
                                if st.button("❌", key=f"remove_{symbol}", help=f"Remove {symbol}"):
                                    st.session_state.selected_stocks.remove(symbol)
                                    # Save to persistent storage
                                    self.data_manager.save_user_selected_stocks(st.session_state.selected_stocks)
                                    st.success(f"Removed {symbol}!")
                                    st.rerun()
                            else:
                                st.error(f"❌ {symbol}")
                        except Exception as e:
                            st.error(f"❌ {symbol}\nError: {str(e)[:30]}...")

    def _display_tracked_stocks_table(self):
        """Display tracked stocks in detailed table format"""
        stocks_data = []
        for symbol in st.session_state.selected_stocks:
            try:
                stock = self.dse_api.get_stock_by_symbol(symbol)
                if stock:
                    stocks_data.append({
                        'Symbol': stock.symbol,
                        'Name': stock.name,
                        'LTP': stock.current_price,
                        'Change': stock.price_change,
                        'Change %': stock.price_change_percent,
                        'Volume': stock.volume,
                        'Last Updated': stock.last_updated.strftime('%H:%M:%S') if stock.last_updated else 'N/A'
                    })
                else:
                    stocks_data.append({
                        'Symbol': symbol,
                        'Name': 'N/A',
                        'LTP': 0,
                        'Change': 0,
                        'Change %': 0,
                        'Volume': 0,
                        'Last Updated': 'Error'
                    })
            except Exception:
                stocks_data.append({
                    'Symbol': symbol,
                    'Name': 'Error',
                    'LTP': 0,
                    'Change': 0,
                    'Change %': 0,
                    'Volume': 0,
                    'Last Updated': 'Error'
                })

        if stocks_data:
            df = pd.DataFrame(stocks_data)

            # Apply styling to the dataframe
            def color_change(val):
                if isinstance(val, (int, float)):
                    return 'color: green' if val > 0 else 'color: red' if val < 0 else 'color: gray'
                return ''

            styled_df = df.style.applymap(color_change, subset=['Change', 'Change %']) \
                              .format({
                                  'LTP': '৳{:.2f}',
                                  'Change': '{:+.2f}',
                                  'Change %': '{:+.2f}%',
                                  'Volume': '{:,}'
                              })

            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No data available for selected stocks")
    
    def _render_top30_stocks(self):
        """Render top 30 stocks"""
        st.subheader("🏆 Top 30 Stocks")
        
        if st.button("🔄 Refresh Top 30", type="secondary"):
            with st.spinner("Fetching top 30 stocks..."):
                try:
                    top30_stocks = self.dse_api.get_top30_stocks()
                    
                    if top30_stocks:
                        # Display top 30 in a table
                        df_data = []
                        for stock in top30_stocks:
                            df_data.append({
                                'Symbol': stock.symbol,
                                'Name': stock.name,
                                'LTP': f"৳{stock.current_price:.2f}",
                                'Change': f"{stock.price_change:+.2f}",
                                'Change %': f"{stock.price_change_percent:+.2f}%",
                                'Volume': f"{stock.volume:,}",
                                'High': f"৳{stock.high:.2f}" if stock.high else 'N/A',
                                'Low': f"৳{stock.low:.2f}" if stock.low else 'N/A'
                            })
                        
                        if df_data:
                            df = pd.DataFrame(df_data)
                            
                            # Add selection checkboxes
                            selected_stocks = st.multiselect(
                                "Select stocks to add to tracking:",
                                options=df['Symbol'].tolist(),
                                key="top30_selection"
                            )
                            
                            # Display the table
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Add selected stocks
                            if selected_stocks:
                                if st.button("➕ Add Selected to Tracking", type="primary"):
                                    added_count = 0
                                    for symbol in selected_stocks:
                                        if symbol not in st.session_state.selected_stocks:
                                            st.session_state.selected_stocks.append(symbol)
                                            added_count += 1

                                    # Save to persistent storage if any stocks were added
                                    if added_count > 0:
                                        # Save to persistent storage
                                        self.data_manager.save_user_selected_stocks(st.session_state.selected_stocks)
                                    
                                    if added_count > 0:
                                        st.success(f"Added {added_count} stocks to tracking!")
                                        st.rerun()
                                    else:
                                        st.info("All selected stocks are already being tracked")
                    
                except Exception as e:
                    st.error(f"Error fetching top 30 stocks: {e}")
        else:
            st.info("Click 'Refresh Top 30' to see the latest top performing stocks")
