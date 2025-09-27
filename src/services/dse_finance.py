"""
DSE Finance Service - Integrated with Stock Market Analyzer
Provides GOOGLEFINANCE-like functionality for Dhaka Stock Exchange
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional
import time
import streamlit as st
from urllib.parse import urljoin


class DSEFinanceService:
    """
    Dhaka Stock Exchange Finance data fetcher
    Integrated with the existing Stock Market Analyzer
    """

    def __init__(self):
        self.base_url = "https://www.dsebd.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # API endpoints
        self.endpoints = {
            'quotes': '/datafile/quotes.txt',
            'company_details': '/displayCompany.php',
            'top_20': '/top_20_share.php',
            'historical': '/day_end_archive.php',
            'suggest_list': '/ajax/suggestList.php'
        }

        # Cache for performance
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[str]:
        """Make HTTP request to DSE with error handling"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            st.error(f"Error fetching data: {e}")
            return None

    def _parse_quotes_data(self, data: str) -> Dict[str, Dict]:
        """Parse the quotes.txt file format"""
        stocks = {}
        if not data:
            return stocks

        lines = data.strip().split('\n')
        # Skip the header lines and look for actual data
        for line in lines[3:]:  # Skip the first 3 header lines
            if not line.strip():
                continue

            # Parse tab-separated format: Symbol \t Price
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        symbol = parts[0].strip()
                        price_str = parts[1].strip()

                        if symbol and price_str:
                            price = float(price_str)
                            stocks[symbol] = {
                                'symbol': symbol,
                                'ltp': price,
                                'high': price,  # Use current price as placeholder
                                'low': price,   # Use current price as placeholder
                                'close_p': price,
                                'ycp': price,   # Yesterday's close (placeholder)
                                'change': 0.0,  # Calculate if we had ycp
                                'trade': 0,     # Not available in this format
                                'value_mn': 0.0,
                                'volume': 0
                            }
                    except (ValueError, IndexError):
                        continue
        return stocks

    def _get_cached_quotes(self) -> Dict[str, Dict]:
        """Get cached quotes data or fetch fresh data"""
        # Simple caching without Streamlit decorator
        cache_key = 'quotes_data'
        current_time = datetime.now()

        if (cache_key in self._cache and
            (current_time - self._cache[cache_key]['timestamp']).seconds < self._cache_timeout):
            return self._cache[cache_key]['data']

        quotes_data = self._make_request(self.endpoints['quotes'])
        parsed_data = self._parse_quotes_data(quotes_data)

        self._cache[cache_key] = {
            'data': parsed_data,
            'timestamp': current_time
        }

        return parsed_data

    def dsefinance(self, symbol: str, attribute: str, start_date: str = None, end_date: str = None) -> Union[Dict, pd.DataFrame, None]:
        """
        Main function that replicates GOOGLEFINANCE functionality for DSE

        Args:
            symbol: Stock symbol (e.g., 'GP', 'SQURPHARMA')
            attribute: Data attribute to fetch
                - 'price': Current price and basic info
                - 'history': Historical data (requires start_date and end_date)
                - 'all': All available current data
                - 'volume': Current volume data
                - 'change': Price change data
        """
        symbol = symbol.upper().strip()
        attribute = attribute.lower().strip()

        if attribute == 'price':
            return self.get_current_price(symbol)
        elif attribute == 'history':
            if not start_date or not end_date:
                st.error("Historical data requires start_date and end_date")
                return None
            return self.get_historical_data(symbol, start_date, end_date)
        elif attribute == 'all':
            return self.get_all_data(symbol)
        elif attribute == 'volume':
            return self.get_volume_data(symbol)
        elif attribute == 'change':
            return self.get_change_data(symbol)
        else:
            st.error(f"Unknown attribute: {attribute}. Available: price, history, all, volume, change")
            return None

    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current stock price and basic info"""
        symbol = symbol.upper().strip()
        quotes = self._get_cached_quotes()

        if symbol in quotes:
            stock_data = quotes[symbol]
            change_percent = round((stock_data['change'] / stock_data['ycp'] * 100), 2) if stock_data['ycp'] != 0 else 0

            return {
                'symbol': symbol,
                'price': stock_data['ltp'],
                'high': stock_data['high'],
                'low': stock_data['low'],
                'previous_close': stock_data['ycp'],
                'change': stock_data['change'],
                'change_percent': change_percent,
                'volume': stock_data['volume'],
                'value_mn': stock_data['value_mn'],
                'trades': stock_data['trade'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        return None

    def get_volume_data(self, symbol: str) -> Optional[Dict]:
        """Get volume-specific data"""
        data = self.get_current_price(symbol)
        if data:
            return {
                'symbol': symbol,
                'volume': data['volume'],
                'value_mn': data['value_mn'],
                'trades': data['trades'],
                'timestamp': data['timestamp']
            }
        return None

    def get_change_data(self, symbol: str) -> Optional[Dict]:
        """Get change-specific data"""
        data = self.get_current_price(symbol)
        if data:
            return {
                'symbol': symbol,
                'change': data['change'],
                'change_percent': data['change_percent'],
                'current_price': data['price'],
                'previous_close': data['previous_close'],
                'timestamp': data['timestamp']
            }
        return None

    def get_all_data(self, symbol: str) -> Optional[Dict]:
        """Get all available data for a symbol"""
        return self.get_current_price(symbol)

    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get historical stock data
        Note: This generates sample data as DSE historical data access is limited
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')

            # Get current price as baseline
            current_data = self.get_current_price(symbol)
            if not current_data:
                return None

            return self._generate_historical_data(symbol, start_dt, end_dt, current_data['price'])

        except ValueError as e:
            st.error(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
            return None

    def _generate_historical_data(self, symbol: str, start_date: datetime, end_date: datetime, base_price: float) -> pd.DataFrame:
        """Generate sample historical data based on current price"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # Filter to DSE trading days (Sunday-Thursday)
        business_days = [date for date in dates if date.weekday() in [6, 0, 1, 2, 3]]

        historical_data = []
        for i, date in enumerate(business_days):
            # Generate realistic price variations
            price_variation = 0.95 + (0.1 * (i % 10) / 10)
            open_price = base_price * price_variation
            high_price = open_price * (1 + 0.03)
            low_price = open_price * (1 - 0.03)
            close_price = open_price + ((high_price - low_price) * 0.5)
            volume = 1000 + (i * 100)

            historical_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': volume,
                'Symbol': symbol
            })

        return pd.DataFrame(historical_data)

    def get_multiple_stocks(self, symbols: List[str], attribute: str = 'price') -> pd.DataFrame:
        """Get data for multiple stocks at once"""
        results = []

        for symbol in symbols:
            data = self.dsefinance(symbol, attribute)
            if data and isinstance(data, dict):
                results.append(data)

        return pd.DataFrame(results) if results else pd.DataFrame()

    def search_stocks(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for stocks by symbol"""
        query = query.upper().strip()
        quotes = self._get_cached_quotes()

        matching_stocks = []
        for symbol, data in quotes.items():
            if query in symbol:
                change_percent = round((data['change'] / data['ycp'] * 100), 2) if data['ycp'] != 0 else 0
                matching_stocks.append({
                    'symbol': symbol,
                    'price': data['ltp'],
                    'change': data['change'],
                    'change_percent': change_percent,
                    'volume': data['volume']
                })

        return matching_stocks[:limit]

    def get_market_summary(self) -> Dict:
        """Get overall market summary"""
        quotes = self._get_cached_quotes()

        if not quotes:
            return {}

        total_stocks = len(quotes)
        advancing = sum(1 for stock in quotes.values() if stock['change'] > 0)
        declining = sum(1 for stock in quotes.values() if stock['change'] < 0)
        unchanged = total_stocks - advancing - declining

        total_volume = sum(stock['volume'] for stock in quotes.values())
        total_value = sum(stock['value_mn'] for stock in quotes.values())

        return {
            'total_stocks': total_stocks,
            'advancing': advancing,
            'declining': declining,
            'unchanged': unchanged,
            'total_volume': total_volume,
            'total_value_mn': round(total_value, 2),
            'market_status': 'Open' if self._is_market_open() else 'Closed',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _is_market_open(self) -> bool:
        """Check if DSE market is currently open"""
        now = datetime.now()
        # DSE trades Sunday-Thursday, 10:30 AM - 2:30 PM
        if now.weekday() in [6, 0, 1, 2, 3]:  # Sunday-Thursday
            market_open = now.replace(hour=10, minute=30, second=0)
            market_close = now.replace(hour=14, minute=30, second=0)
            return market_open <= now <= market_close
        return False

    def export_to_csv(self, data: Union[Dict, pd.DataFrame, List[Dict]]) -> str:
        """Export data to CSV format"""
        if isinstance(data, pd.DataFrame):
            return data.to_csv(index=False)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
            return df.to_csv(index=False)
        else:
            return ""

    def export_to_json(self, data: Union[Dict, pd.DataFrame, List[Dict]]) -> str:
        """Export data to JSON format"""
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient='records', indent=2)
        elif isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, default=str)
        else:
            return "{}"