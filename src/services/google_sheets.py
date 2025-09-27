import gspread
from google.auth.exceptions import DefaultCredentialsError
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
from config import Config
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import Transaction, TransactionType, PortfolioItem, PortfolioSnapshot

class GoogleSheetsService:
    def __init__(self):
        self.config = Config()
        self.sheet_id = self.config.GOOGLE_SHEET_ID
        self.credentials_file = self.config.GOOGLE_CREDENTIALS_FILE
        self.service = None
        self.workbook = None
        
        if self.sheet_id and self.credentials_file:
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets service"""
        try:
            # Authenticate using service account credentials
            self.service = gspread.service_account(filename=self.credentials_file)
            self.workbook = self.service.open_by_key(self.sheet_id)
            print("Google Sheets service initialized successfully")
        except FileNotFoundError:
            print(f"Credentials file not found: {self.credentials_file}")
            self.service = None
        except DefaultCredentialsError:
            print("Google credentials not found. Please set up authentication.")
            self.service = None
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.service = None
    
    def _get_or_create_worksheet(self, sheet_name: str, headers: List[str] = None) -> gspread.Worksheet:
        """Get existing worksheet or create new one"""
        try:
            worksheet = self.workbook.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.workbook.add_worksheet(title=sheet_name, rows=1000, cols=20)
            if headers:
                worksheet.append_row(headers)
        return worksheet
    
    # Stock data methods
    def save_stock_data(self, stock: Stock) -> bool:
        """Save stock data to Google Sheets"""
        try:
            if not self.service:
                return False
            
            worksheet = self._get_or_create_worksheet(
                self.config.MAIN_SHEET,
                ['Symbol', 'Name', 'Current Price', 'Previous Close', 'Change', 'Change %', 'Volume', 'High', 'Low', 'Open', 'Last Updated']
            )
            
            # Check if stock already exists
            try:
                cell = worksheet.find(stock.symbol)
                row = cell.row
            except gspread.CellNotFound:
                # Add new row
                row = len(worksheet.get_all_values()) + 1
            
            # Update or insert data
            worksheet.update_cell(row, 1, stock.symbol)
            worksheet.update_cell(row, 2, stock.name)
            worksheet.update_cell(row, 3, stock.current_price)
            worksheet.update_cell(row, 4, stock.previous_close)
            worksheet.update_cell(row, 5, stock.price_change)
            worksheet.update_cell(row, 6, f"{stock.price_change_percent:.2f}%")
            worksheet.update_cell(row, 7, stock.volume)
            worksheet.update_cell(row, 8, stock.high or "")
            worksheet.update_cell(row, 9, stock.low or "")
            worksheet.update_cell(row, 10, stock.open_price or "")
            worksheet.update_cell(row, 11, stock.last_updated.isoformat() if stock.last_updated else "")
            
            return True
        
        except Exception as e:
            print(f"Error saving stock data to Google Sheets: {e}")
            return False
    
    def get_stock_data(self, symbol: str) -> Optional[Stock]:
        """Get stock data from Google Sheets"""
        try:
            if not self.service:
                return None
            
            worksheet = self._get_or_create_worksheet(self.config.MAIN_SHEET)
            
            try:
                cell = worksheet.find(symbol)
                row = worksheet.row_values(cell.row)
                
                if len(row) >= 11:
                    return Stock(
                        symbol=row[0],
                        name=row[1],
                        current_price=float(row[2]) if row[2] else 0,
                        previous_close=float(row[3]) if row[3] else 0,
                        volume=int(row[6]) if row[6] else 0,
                        high=float(row[7]) if row[7] else None,
                        low=float(row[8]) if row[8] else None,
                        open_price=float(row[9]) if row[9] else None,
                        last_updated=datetime.fromisoformat(row[10]) if row[10] else None
                    )
            
            except gspread.CellNotFound:
                return None
            
            return None
        
        except Exception as e:
            print(f"Error getting stock data from Google Sheets: {e}")
            return None
    
    def save_historical_data(self, symbol: str, history: List[StockPriceHistory]) -> bool:
        """Save historical data to Google Sheets"""
        try:
            if not self.service:
                return False
            
            worksheet = self._get_or_create_worksheet(
                self.config.HISTORICAL_SHEET,
                ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            )
            
            # Clear existing data for this symbol
            try:
                cells = worksheet.findall(symbol)
                for cell in cells:
                    if cell.col == 1:  # Symbol column
                        worksheet.delete_rows(cell.row)
            except gspread.CellNotFound:
                pass  # No existing data to clear
            
            # Add new historical data
            for price_history in history:
                row = [
                    price_history.symbol,
                    price_history.date.strftime('%Y-%m-%d'),
                    price_history.open_price,
                    price_history.high,
                    price_history.low,
                    price_history.close_price,
                    price_history.volume
                ]
                worksheet.append_row(row)
            
            return True
        
        except Exception as e:
            print(f"Error saving historical data to Google Sheets: {e}")
            return False
    
    def get_historical_data(self, symbol: str, days: int = 30) -> List[StockPriceHistory]:
        """Get historical data from Google Sheets"""
        try:
            if not self.service:
                return []
            
            worksheet = self._get_or_create_worksheet(self.config.HISTORICAL_SHEET)
            
            # Get all data
            all_data = worksheet.get_all_values()
            if len(all_data) <= 1:  # Only headers
                return []
            
            # Filter by symbol
            symbol_data = [row for row in all_data[1:] if row[0] == symbol]
            
            # Convert to StockPriceHistory objects
            history = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for row in symbol_data:
                try:
                    if len(row) >= 7:
                        date = datetime.strptime(row[1], '%Y-%m-%d')
                        if date >= cutoff_date:
                            price_history = StockPriceHistory(
                                symbol=row[0],
                                date=date,
                                open_price=float(row[2]) if row[2] else 0,
                                high=float(row[3]) if row[3] else 0,
                                low=float(row[4]) if row[4] else 0,
                                close_price=float(row[5]) if row[5] else 0,
                                volume=int(row[6]) if row[6] else 0
                            )
                            history.append(price_history)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing historical data row: {e}")
                    continue
            
            return sorted(history, key=lambda x: x.date)
        
        except Exception as e:
            print(f"Error getting historical data from Google Sheets: {e}")
            return []
    
    # Transaction methods
    def save_transaction(self, transaction: Transaction) -> bool:
        """Save transaction to Google Sheets"""
        try:
            if not self.service:
                return False
            
            worksheet = self._get_or_create_worksheet(
                self.config.TRANSACTIONS_SHEET,
                ['ID', 'Symbol', 'Type', 'Quantity', 'Price', 'Total', 'Timestamp', 'Notes']
            )
            
            row = [
                transaction.id,
                transaction.symbol,
                transaction.transaction_type.value,
                transaction.quantity,
                transaction.price,
                transaction.total_amount,
                transaction.timestamp.isoformat(),
                transaction.notes or ""
            ]
            
            worksheet.append_row(row)
            return True
        
        except Exception as e:
            print(f"Error saving transaction to Google Sheets: {e}")
            return False
    
    def get_transactions(self, symbol: str = None) -> List[Transaction]:
        """Get transactions from Google Sheets"""
        try:
            if not self.service:
                return []
            
            worksheet = self._get_or_create_worksheet(self.config.TRANSACTIONS_SHEET)
            
            all_data = worksheet.get_all_values()
            if len(all_data) <= 1:  # Only headers
                return []
            
            transactions = []
            for row in all_data[1:]:
                try:
                    if len(row) >= 7:
                        # Filter by symbol if specified
                        if symbol and row[1] != symbol:
                            continue
                        
                        transaction = Transaction(
                            id=row[0],
                            symbol=row[1],
                            transaction_type=TransactionType(row[2]),
                            quantity=int(row[3]),
                            price=float(row[4]),
                            timestamp=datetime.fromisoformat(row[6]),
                            notes=row[7] if len(row) > 7 else None
                        )
                        transactions.append(transaction)
                
                except (ValueError, IndexError) as e:
                    print(f"Error parsing transaction row: {e}")
                    continue
            
            return sorted(transactions, key=lambda x: x.timestamp)
        
        except Exception as e:
            print(f"Error getting transactions from Google Sheets: {e}")
            return []
    
    # Portfolio methods
    def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> bool:
        """Save portfolio snapshot to Google Sheets"""
        try:
            if not self.service:
                return False
            
            worksheet = self._get_or_create_worksheet(
                self.config.PORTFOLIO_HISTORY_SHEET,
                ['Timestamp', 'Total Value', 'Total Cost', 'Total Gain/Loss', 'Total Gain/Loss %', 'Items JSON']
            )
            
            row = [
                snapshot.timestamp.isoformat(),
                snapshot.total_value,
                snapshot.total_cost,
                snapshot.total_gain_loss,
                snapshot.total_gain_loss_percent,
                json.dumps([item.to_dict() for item in snapshot.items])
            ]
            
            worksheet.append_row(row)
            return True
        
        except Exception as e:
            print(f"Error saving portfolio snapshot to Google Sheets: {e}")
            return False
    
    def get_portfolio_history(self, days: int = 30) -> List[PortfolioSnapshot]:
        """Get portfolio history from Google Sheets"""
        try:
            if not self.service:
                return []
            
            worksheet = self._get_or_create_worksheet(self.config.PORTFOLIO_HISTORY_SHEET)
            
            all_data = worksheet.get_all_values()
            if len(all_data) <= 1:  # Only headers
                return []
            
            snapshots = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for row in all_data[1:]:
                try:
                    if len(row) >= 6:
                        timestamp = datetime.fromisoformat(row[0])
                        if timestamp >= cutoff_date:
                            items_data = json.loads(row[5]) if row[5] else []
                            items = [PortfolioItem.from_dict(item) for item in items_data]
                            
                            snapshot = PortfolioSnapshot(
                                timestamp=timestamp,
                                total_value=float(row[1]),
                                total_cost=float(row[2]),
                                total_gain_loss=float(row[3]),
                                total_gain_loss_percent=float(row[4]),
                                items=items
                            )
                            snapshots.append(snapshot)
                
                except (ValueError, IndexError, json.JSONDecodeError) as e:
                    print(f"Error parsing portfolio snapshot row: {e}")
                    continue
            
            return sorted(snapshots, key=lambda x: x.timestamp)
        
        except Exception as e:
            print(f"Error getting portfolio history from Google Sheets: {e}")
            return []
    
    def update_portfolio_sheet(self, portfolio_items: Dict[str, PortfolioItem]) -> bool:
        """Update the main portfolio sheet"""
        try:
            if not self.service:
                return False
            
            worksheet = self._get_or_create_worksheet(
                self.config.PORTFOLIO_SHEET,
                ['Symbol', 'Quantity', 'Average Cost', 'Current Price', 'Total Cost', 'Current Value', 'Gain/Loss', 'Gain/Loss %', 'Last Updated']
            )
            
            # Clear existing data
            worksheet.clear()
            worksheet.append_row(['Symbol', 'Quantity', 'Average Cost', 'Current Price', 'Total Cost', 'Current Value', 'Gain/Loss', 'Gain/Loss %', 'Last Updated'])
            
            # Add current portfolio data
            for symbol, item in portfolio_items.items():
                if item.quantity > 0:
                    row = [
                        item.symbol,
                        item.quantity,
                        item.average_cost,
                        item.current_price,
                        item.total_cost,
                        item.current_value,
                        item.gain_loss,
                        f"{item.gain_loss_percent:.2f}%",
                        item.last_updated.isoformat()
                    ]
                    worksheet.append_row(row)
            
            return True
        
        except Exception as e:
            print(f"Error updating portfolio sheet: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Google Sheets service is connected"""
        return self.service is not None and self.workbook is not None
    
    def get_sheet_url(self) -> str:
        """Get the URL of the Google Sheet"""
        if self.sheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
        return ""
