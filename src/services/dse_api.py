import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
from bs4 import BeautifulSoup
from config import Config
from src.models.stock import Stock, StockPriceHistory

class DSEAPIService:
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.DSE_BASE_URL
        self.endpoints = self.config.DSE_API_ENDPOINTS
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Any:
        """Make a request to the DSE API with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.session.headers.update({'Referer': self.base_url})
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            # Handle different response types
            content_type = response.headers.get('Content-Type', '').lower()
            if 'json' in content_type:
                return response.json()
            elif 'text' in content_type or 'plain' in content_type:
                return response.text
            else:
                return response.text

        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response from {endpoint}: {e}")
            return None
    
    def _parse_quotes_txt(self, content: str) -> List[Dict]:
        """Parse the quotes.txt content into structured data"""
        stocks = []
        if not content:
            return stocks

        lines = content.split('\n')
        for line in lines[3:]:  # Skip first 3 header lines
            line = line.strip()
            if line:
                # Handle tab-separated format: Symbol \t LTP \t High \t Low \t YCP \t Change \t Trade \t Value(mn) \t Volume
                if '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 9:
                        try:
                            symbol = parts[0].strip()
                            ltp = float(parts[1].strip()) if parts[1].strip() else 0.0
                            high = float(parts[2].strip()) if parts[2].strip() else ltp
                            low = float(parts[3].strip()) if parts[3].strip() else ltp
                            ycp = float(parts[4].strip()) if parts[4].strip() else ltp
                            change = float(parts[5].strip()) if parts[5].strip() else 0.0
                            trade = int(parts[6].strip()) if parts[6].strip() else 0
                            value_mn = float(parts[7].strip()) if parts[7].strip() else 0.0
                            volume = int(parts[8].strip()) if parts[8].strip() else 0

                            if symbol and ltp > 0:
                                stocks.append({
                                    'symbol': symbol,
                                    'trading_code': symbol,
                                    'last_trade_price': ltp,
                                    'previous_close': ycp,
                                    'high': high,
                                    'low': low,
                                    'change': change,
                                    'volume': volume,
                                    'trades': trade,
                                    'value_mn': value_mn,
                                    'name': symbol
                                })
                        except (ValueError, IndexError):
                            # Fallback: try minimal parsing
                            try:
                                symbol = parts[0].strip()
                                price = float(parts[1].strip()) if parts[1].strip() else 0.0
                                if symbol and price > 0:
                                    stocks.append({
                                        'symbol': symbol,
                                        'trading_code': symbol,
                                        'last_trade_price': price,
                                        'previous_close': price,
                                        'name': symbol
                                    })
                            except:
                                continue
                    else:
                        # Handle minimal format
                        try:
                            symbol = parts[0].strip()
                            price_str = ''
                            for part in parts[1:]:
                                part = part.strip()
                                if part:
                                    price_str = part
                                    break
                            if symbol and price_str:
                                price = float(price_str)
                                if price > 0:
                                    stocks.append({
                                        'symbol': symbol,
                                        'trading_code': symbol,
                                        'last_trade_price': price,
                                        'previous_close': price,
                                        'name': symbol
                                    })
                        except ValueError:
                            continue
                else:
                    # Fallback to space-based parsing
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            symbol = parts[0].strip()
                            price_str = parts[1].strip()
                            if symbol and price_str:
                                price = float(price_str)
                                if price > 0:
                                    stocks.append({
                                        'symbol': symbol,
                                        'trading_code': symbol,
                                        'last_trade_price': price,
                                        'previous_close': price,
                                        'name': symbol
                                    })
                        except ValueError:
                            continue

        return stocks

    def get_company_list(self) -> List[Dict]:
        """Get list of all companies from DSE quotes"""
        content = self._make_request(self.endpoints['quotes_txt'])
        if content:
            return self._parse_quotes_txt(content)
        return []
    
    def get_latest_prices(self) -> List[Stock]:
        """Get latest prices for all stocks from quotes.txt"""
        content = self._make_request(self.endpoints['quotes_txt'])
        stocks = []

        if content:
            stock_data = self._parse_quotes_txt(content)
            for item in stock_data:
                try:
                    stock = Stock(
                        symbol=item['symbol'],
                        name=item['name'],
                        current_price=item['last_trade_price'],
                        previous_close=item.get('previous_close', item['last_trade_price']),
                        volume=item.get('volume', 0),
                        high=item.get('high'),
                        low=item.get('low'),
                        open_price=None,
                        last_updated=datetime.now()
                    )
                    stocks.append(stock)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing stock data for {item.get('symbol', 'Unknown')}: {e}")
                    continue

        return stocks
    
    def _parse_top_20_shares(self, content: str) -> List[Dict]:
        """Parse the top_20_share.php HTML content"""
        stocks = []
        try:
            soup = BeautifulSoup(content, 'html.parser')
            tables = soup.find_all('table', class_='table')
            if not tables:
                tables = soup.find_all('table')

            # Use the first table which contains the main data
            if tables:
                table = tables[0]
                rows = table.find_all('tr')

                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 6:
                        try:
                            rank = cells[0].get_text(strip=True)
                            symbol = cells[1].get_text(strip=True)
                            ltp = float(cells[2].get_text(strip=True))
                            high = float(cells[3].get_text(strip=True))
                            low = float(cells[4].get_text(strip=True))
                            ycp = float(cells[5].get_text(strip=True))

                            stocks.append({
                                'rank': int(rank),
                                'symbol': symbol,
                                'ltp': ltp,
                                'high': high,
                                'low': low,
                                'ycp': ycp,
                                'change': ltp - ycp,
                                'change_percent': ((ltp - ycp) / ycp * 100) if ycp > 0 else 0
                            })
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            print(f"Error parsing top 20 shares: {e}")

        return stocks

    def get_top30_stocks(self) -> List[Stock]:
        """Get top 20 stocks from DSE top_20_share.php (only 20 available)"""
        content = self._make_request(self.endpoints['top_20_shares'])
        stocks = []

        if content:
            top_stocks_data = self._parse_top_20_shares(content)
            for item in top_stocks_data:
                try:
                    stock = Stock(
                        symbol=item['symbol'],
                        name=item['symbol'],
                        current_price=item['ltp'],
                        previous_close=item['ycp'],
                        volume=0,  # Not available in this endpoint
                        high=item['high'],
                        low=item['low'],
                        open_price=None,
                        last_updated=datetime.now()
                    )
                    stocks.append(stock)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing top stock data for {item.get('symbol', 'Unknown')}: {e}")
                    continue

        return stocks
    
    def _parse_company_details(self, content: str, symbol: str) -> Optional[Dict]:
        """Parse the displayCompany.php HTML content for detailed stock info"""
        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Extract basic stock info from the page
            stock_info = {
                'symbol': symbol,
                'name': symbol,  # Default to symbol
                'current_price': 0.0,
                'volume': 0,
                'high': None,
                'low': None,
                'previous_close': None
            }

            # Look for price information in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        text = ' '.join(cell_texts).lower()

                        # Look for key price indicators
                        if 'last trading price' in text or 'ltp' in text:
                            for cell_text in cell_texts:
                                try:
                                    if cell_text and cell_text.replace('.', '').replace(',', '').isdigit():
                                        stock_info['current_price'] = float(cell_text.replace(',', ''))
                                        break
                                except ValueError:
                                    continue

                        elif 'volume' in text:
                            for cell_text in cell_texts:
                                try:
                                    if cell_text and cell_text.replace(',', '').isdigit():
                                        stock_info['volume'] = int(cell_text.replace(',', ''))
                                        break
                                except ValueError:
                                    continue

            return stock_info if stock_info['current_price'] > 0 else None

        except Exception as e:
            print(f"Error parsing company details for {symbol}: {e}")
            return None

    def get_stock_details(self, symbol: str) -> Optional[Dict]:
        """Get detailed information for a specific stock"""
        params = {'name': symbol}
        content = self._make_request(self.endpoints['company_details'], params)
        if content:
            return self._parse_company_details(content, symbol)
        return None
    
    def _try_get_historical_from_archive(self, symbol: str, days: int = 30) -> List[StockPriceHistory]:
        """Try to get real historical data from archive endpoint"""
        try:
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Format dates as required
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            # Build URL with parameters
            url = f"{self.base_url}{self.endpoints['historical_archive']}"
            params = {
                'startDate': start_str,
                'endDate': end_str,
                'inst': symbol,
                'archive': 'data'
            }

            response = self.session.get(url, params=params, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for the specific table with the "Day End Summary" structure
                tables = soup.find_all('table')

                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 2:  # Must have at least header + data rows
                        # Check if this is the Day End Summary table
                        header_row = rows[0]
                        headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]

                        # Look for the specific column structure: #, DATE, TRADING CODE, LTP*, HIGH, LOW, OPENP*, CLOSEP*, YCP, etc.
                        header_text = ' '.join(headers).upper()

                        if ('DATE' in header_text and 'TRADING CODE' in header_text and
                            'LTP' in header_text and 'HIGH' in header_text and 'LOW' in header_text and
                            'OPENP' in header_text and 'CLOSEP' in header_text):

                            # Found the correct table, now parse the data
                            history = []

                            for row in rows[1:]:  # Skip header row
                                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]

                                # Expected columns: #, DATE, TRADING CODE, LTP*, HIGH, LOW, OPENP*, CLOSEP*, YCP, TRADE, VALUE, VOLUME
                                if len(cells) >= 12 and cells[2] == symbol:  # Check if this row is for our symbol
                                    try:
                                        date_str = cells[1]  # DATE column
                                        ltp = float(cells[3])  # LTP* column
                                        high = float(cells[4])  # HIGH column
                                        low = float(cells[5])  # LOW column
                                        open_price = float(cells[6])  # OPENP* column
                                        close_price = float(cells[7])  # CLOSEP* column
                                        volume = int(float(cells[11].replace(',', '')))  # VOLUME column (remove commas)

                                        # Parse date
                                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

                                        price_history = StockPriceHistory(
                                            symbol=symbol,
                                            date=date_obj,
                                            open_price=open_price,
                                            high=high,
                                            low=low,
                                            close_price=close_price,
                                            volume=volume
                                        )
                                        history.append(price_history)

                                    except (ValueError, IndexError) as e:
                                        print(f"Error parsing row for {symbol}: {e}")
                                        continue

                            if history:
                                return sorted(history, key=lambda x: x.date)

        except Exception as e:
            print(f"Error fetching historical data from archive: {e}")

        return []

    def get_stock_historical_data(self, symbol: str, days: int = 30) -> List[StockPriceHistory]:
        """Get historical data for a specific stock"""
        # Try to get real historical data from archive
        historical_data = self._try_get_historical_from_archive(symbol, days)

        if historical_data:
            return historical_data

        # If no real data found, raise an error
        raise ValueError(f"No historical data available for symbol '{symbol}' for the requested {days} days period. The archive endpoint may not contain data for this symbol or time range.")
    
    def get_dsex_data(self, symbol: str = None) -> Dict:
        """Get DSEX data, optionally filtered by symbol"""
        params = {'symbol': symbol} if symbol else None
        return self._make_request(self.endpoints['dsexdata'], params)
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by name or symbol with enhanced details"""
        try:
            # Get fresh data directly from quotes.txt
            content = self._make_request(self.endpoints['quotes_txt'])
            if not content:
                return []

            company_list = self._parse_quotes_txt(content)
            query_lower = query.lower().strip()

            results = []
            for company in company_list:
                symbol = company.get('symbol', '').lower()
                name = company.get('name', '').lower()
                trading_code = company.get('trading_code', '').lower()

                # Check for matches (case-insensitive)
                if (query_lower in symbol or
                    query_lower in name or
                    query_lower in trading_code or
                    symbol.startswith(query_lower) or
                    query_lower == symbol):  # Exact match priority

                    # Enhance with additional details from displayCompany.php
                    enhanced_company = self._enhance_company_details(company)
                    results.append(enhanced_company)

            # Sort results: exact matches first, then partial matches
            def sort_key(company):
                symbol = company.get('symbol', '').lower()
                if symbol == query_lower:
                    return 0  # Exact match first
                elif symbol.startswith(query_lower):
                    return 1  # Starts with match second
                else:
                    return 2  # Contains match last

            results.sort(key=sort_key)
            return results[:20]  # Limit results to 20

        except Exception as e:
            print(f"Error in search_stocks: {e}")
            return []

    def _enhance_company_details(self, company: Dict) -> Dict:
        """Enhance company details using displayCompany.php endpoint"""
        try:
            symbol = company.get('symbol', '').upper()
            # Use the displayCompany.php endpoint with uppercase symbol
            params = {'name': symbol}
            details_content = self._make_request(self.endpoints['company_details'], params)

            if details_content:
                # Parse additional details if available
                enhanced = company.copy()
                # You can add more parsing here if needed for additional details
                # For now, just return the original with confirmed API call
                enhanced['details_available'] = True
                return enhanced
            else:
                company['details_available'] = False
                return company

        except Exception as e:
            company['details_available'] = False
            return company

    def get_all_symbols(self) -> List[str]:
        """Get list of all available stock symbols for suggestions"""
        try:
            content = self._make_request(self.endpoints['quotes_txt'])
            if content:
                company_list = self._parse_quotes_txt(content)
                return [company.get('symbol', '').upper() for company in company_list if company.get('symbol')]
            return []
        except Exception as e:
            print(f"Error getting all symbols: {e}")
            return []

    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Get a specific stock by its symbol"""
        content = self._make_request(self.endpoints['quotes_txt'])
        if content:
            stock_data = self._parse_quotes_txt(content)
            for item in stock_data:
                if item['symbol'].upper() == symbol.upper():
                    try:
                        return Stock(
                            symbol=item['symbol'],
                            name=item['name'],
                            current_price=item['last_trade_price'],
                            previous_close=item.get('previous_close', item['last_trade_price']),
                            volume=item.get('volume', 0),
                            high=item.get('high'),
                            low=item.get('low'),
                            open_price=None,
                            last_updated=datetime.now()
                        )
                    except (ValueError, TypeError):
                        return None
        return None
