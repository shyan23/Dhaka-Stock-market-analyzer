import json
import redis
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
import streamlit as st
from config import Config
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import Transaction, PortfolioItem, PortfolioSnapshot

class DataManager:
    def __init__(self, session_manager=None):
        self.config = Config()
        self.app_mode = self.config.APP_MODE
        self.session_manager = session_manager

        if self.app_mode == 'redis':
            self._init_redis()
        else:
            self._init_google_sheets()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                password=self.config.REDIS_PASSWORD if self.config.REDIS_PASSWORD else None,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connection established")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None

    def _get_user_prefix(self) -> str:
        """Get user prefix for Redis keys"""
        if self.session_manager:
            return self.session_manager.get_user_prefix()
        return "global_"
    
    def _init_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            from src.services.google_sheets import GoogleSheetsService
            self.sheets_service = GoogleSheetsService()
            if self.sheets_service.is_connected():
                print("Google Sheets service initialized successfully")
            else:
                print("Google Sheets service initialized but not connected")
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.sheets_service = None
    
    # Stock data methods
    def save_stock_data(self, stock: Stock) -> bool:
        """Save stock data to storage"""
        try:
            if self.app_mode == 'redis':
                return self._save_stock_to_redis(stock)
            else:
                return self._save_stock_to_sheets(stock)
        except Exception as e:
            print(f"Error saving stock data: {e}")
            return False
    
    def get_stock_data(self, symbol: str) -> Optional[Stock]:
        """Get stock data from storage"""
        try:
            if self.app_mode == 'redis':
                return self._get_stock_from_redis(symbol)
            else:
                return self._get_stock_from_sheets(symbol)
        except Exception as e:
            print(f"Error getting stock data: {e}")
            return None
    
    def save_historical_data(self, symbol: str, history: List[StockPriceHistory]) -> bool:
        """Save historical data for a stock"""
        try:
            if self.app_mode == 'redis':
                return self._save_historical_to_redis(symbol, history)
            else:
                return self._save_historical_to_sheets(symbol, history)
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
    
    def get_historical_data(self, symbol: str, days: int = 30) -> List[StockPriceHistory]:
        """Get historical data for a stock"""
        try:
            if self.app_mode == 'redis':
                return self._get_historical_from_redis(symbol, days)
            else:
                return self._get_historical_from_sheets(symbol, days)
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return []
    
    # Portfolio methods
    def save_transaction(self, transaction: Transaction) -> bool:
        """Save a transaction"""
        try:
            if self.app_mode == 'redis':
                return self._save_transaction_to_redis(transaction)
            else:
                return self._save_transaction_to_sheets(transaction)
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False
    
    def get_transactions(self, symbol: str = None) -> List[Transaction]:
        """Get transactions, optionally filtered by symbol"""
        try:
            if self.app_mode == 'redis':
                return self._get_transactions_from_redis(symbol)
            else:
                return self._get_transactions_from_sheets(symbol)
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> bool:
        """Save portfolio snapshot"""
        try:
            if self.app_mode == 'redis':
                return self._save_portfolio_snapshot_to_redis(snapshot)
            else:
                return self._save_portfolio_snapshot_to_sheets(snapshot)
        except Exception as e:
            print(f"Error saving portfolio snapshot: {e}")
            return False
    
    def get_portfolio_history(self, days: int = 30) -> List[PortfolioSnapshot]:
        """Get portfolio history"""
        try:
            if self.app_mode == 'redis':
                return self._get_portfolio_history_from_redis(days)
            else:
                return self._get_portfolio_history_from_sheets(days)
        except Exception as e:
            print(f"Error getting portfolio history: {e}")
            return []
    
    # Redis implementation
    def _save_stock_to_redis(self, stock: Stock) -> bool:
        """Save stock data to Redis"""
        if not self.redis_client:
            return False
        
        key = f"stock:{stock.symbol}"
        data = stock.to_dict()
        return self.redis_client.set(key, json.dumps(data), ex=3600)  # Expire in 1 hour
    
    def _get_stock_from_redis(self, symbol: str) -> Optional[Stock]:
        """Get stock data from Redis"""
        if not self.redis_client:
            return None
        
        key = f"stock:{symbol}"
        data = self.redis_client.get(key)
        if data:
            return Stock.from_dict(json.loads(data))
        return None
    
    def _save_historical_to_redis(self, symbol: str, history: List[StockPriceHistory]) -> bool:
        """Save historical data to Redis"""
        if not self.redis_client:
            return False
        
        key = f"historical:{symbol}"
        data = [item.to_dict() for item in history]
        return self.redis_client.set(key, json.dumps(data), ex=86400)  # Expire in 24 hours
    
    def _get_historical_from_redis(self, symbol: str, days: int = 30) -> List[StockPriceHistory]:
        """Get historical data from Redis"""
        if not self.redis_client:
            return []
        
        key = f"historical:{symbol}"
        data = self.redis_client.get(key)
        if data:
            history_data = json.loads(data)
            history = [StockPriceHistory.from_dict(item) for item in history_data]
            # Filter by days
            cutoff_date = datetime.now() - timedelta(days=days)
            return [item for item in history if item.date >= cutoff_date]
        return []
    
    def _save_transaction_to_redis(self, transaction: Transaction) -> bool:
        """Save transaction to Redis"""
        if not self.redis_client:
            return False
        
        key = f"transaction:{transaction.id}"
        data = transaction.to_dict()
        return self.redis_client.set(key, json.dumps(data))
    
    def _get_transactions_from_redis(self, symbol: str = None) -> List[Transaction]:
        """Get transactions from Redis"""
        if not self.redis_client:
            return []
        
        pattern = f"transaction:*"
        keys = self.redis_client.keys(pattern)
        transactions = []
        
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                transaction = Transaction.from_dict(json.loads(data))
                if symbol is None or transaction.symbol == symbol:
                    transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x.timestamp)
    
    def _save_portfolio_snapshot_to_redis(self, snapshot: PortfolioSnapshot) -> bool:
        """Save portfolio snapshot to Redis"""
        if not self.redis_client:
            return False
        
        key = f"portfolio_snapshot:{snapshot.timestamp.isoformat()}"
        data = snapshot.to_dict()
        return self.redis_client.set(key, json.dumps(data))
    
    def _get_portfolio_history_from_redis(self, days: int = 30) -> List[PortfolioSnapshot]:
        """Get portfolio history from Redis"""
        if not self.redis_client:
            return []
        
        pattern = f"portfolio_snapshot:*"
        keys = self.redis_client.keys(pattern)
        snapshots = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                snapshot = PortfolioSnapshot.from_dict(json.loads(data))
                if snapshot.timestamp >= cutoff_date:
                    snapshots.append(snapshot)
        
        return sorted(snapshots, key=lambda x: x.timestamp)
    
    # Google Sheets implementation
    def _save_stock_to_sheets(self, stock: Stock) -> bool:
        """Save stock data to Google Sheets"""
        if not self.sheets_service:
            return False
        return self.sheets_service.save_stock_data(stock)
    
    def _get_stock_from_sheets(self, symbol: str) -> Optional[Stock]:
        """Get stock data from Google Sheets"""
        if not self.sheets_service:
            return None
        return self.sheets_service.get_stock_data(symbol)
    
    def _save_historical_to_sheets(self, symbol: str, history: List[StockPriceHistory]) -> bool:
        """Save historical data to Google Sheets"""
        if not self.sheets_service:
            return False
        return self.sheets_service.save_historical_data(symbol, history)
    
    def _get_historical_from_sheets(self, symbol: str, days: int = 30) -> List[StockPriceHistory]:
        """Get historical data from Google Sheets"""
        if not self.sheets_service:
            return []
        return self.sheets_service.get_historical_data(symbol, days)
    
    def _save_transaction_to_sheets(self, transaction: Transaction) -> bool:
        """Save transaction to Google Sheets"""
        if not self.sheets_service:
            return False
        return self.sheets_service.save_transaction(transaction)
    
    def _get_transactions_from_sheets(self, symbol: str = None) -> List[Transaction]:
        """Get transactions from Google Sheets"""
        if not self.sheets_service:
            return []
        return self.sheets_service.get_transactions(symbol)
    
    def _save_portfolio_snapshot_to_sheets(self, snapshot: PortfolioSnapshot) -> bool:
        """Save portfolio snapshot to Google Sheets"""
        if not self.sheets_service:
            return False
        return self.sheets_service.save_portfolio_snapshot(snapshot)
    
    def _get_portfolio_history_from_sheets(self, days: int = 30) -> List[PortfolioSnapshot]:
        """Get portfolio history from Google Sheets"""
        if not self.sheets_service:
            return []
        return self.sheets_service.get_portfolio_history(days)

    # User-specific Redis methods for session state data
    def save_user_portfolio_items(self, portfolio_items: Dict[str, PortfolioItem]) -> bool:
        """Save user's portfolio items to Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return False

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}portfolio_items"

            # Convert portfolio items to serializable format
            data = {symbol: item.to_dict() for symbol, item in portfolio_items.items()}
            return self.redis_client.set(key, json.dumps(data))
        except Exception as e:
            print(f"Error saving portfolio items: {e}")
            return False

    def load_user_portfolio_items(self) -> Dict[str, PortfolioItem]:
        """Load user's portfolio items from Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return {}

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}portfolio_items"

            data = self.redis_client.get(key)
            if data:
                items_data = json.loads(data)
                return {symbol: PortfolioItem.from_dict(item_data)
                       for symbol, item_data in items_data.items()}
            return {}
        except Exception as e:
            print(f"Error loading portfolio items: {e}")
            return {}

    def save_user_transactions(self, transactions: List[Transaction]) -> bool:
        """Save user's transactions to Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return False

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}transactions"

            # Convert transactions to serializable format
            data = [transaction.to_dict() for transaction in transactions]
            return self.redis_client.set(key, json.dumps(data))
        except Exception as e:
            print(f"Error saving transactions: {e}")
            return False

    def load_user_transactions(self) -> List[Transaction]:
        """Load user's transactions from Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return []

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}transactions"

            data = self.redis_client.get(key)
            if data:
                transactions_data = json.loads(data)
                return [Transaction.from_dict(tx_data) for tx_data in transactions_data]
            return []
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return []

    def save_user_selected_stocks(self, selected_stocks: List[str]) -> bool:
        """Save user's selected stocks to Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return False

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}selected_stocks"
            return self.redis_client.set(key, json.dumps(selected_stocks))
        except Exception as e:
            print(f"Error saving selected stocks: {e}")
            return False

    def load_user_selected_stocks(self) -> List[str]:
        """Load user's selected stocks from Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return []

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}selected_stocks"

            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return []
        except Exception as e:
            print(f"Error loading selected stocks: {e}")
            return []

    def save_user_cash_balance(self, cash_balance: float) -> bool:
        """Save user's cash balance to Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return False

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}cash_balance"
            return self.redis_client.set(key, str(cash_balance))
        except Exception as e:
            print(f"Error saving cash balance: {e}")
            return False

    def load_user_cash_balance(self) -> float:
        """Load user's cash balance from Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return 100000.0  # Default balance

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}cash_balance"

            data = self.redis_client.get(key)
            if data:
                return float(data)
            return 100000.0  # Default balance
        except Exception as e:
            print(f"Error loading cash balance: {e}")
            return 100000.0

    def save_user_portfolio_settings(self, settings: Dict[str, Any]) -> bool:
        """Save user's portfolio settings to Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return False

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}portfolio_settings"
            return self.redis_client.set(key, json.dumps(settings))
        except Exception as e:
            print(f"Error saving portfolio settings: {e}")
            return False

    def load_user_portfolio_settings(self) -> Dict[str, Any]:
        """Load user's portfolio settings from Redis"""
        if self.app_mode != 'redis' or not self.redis_client:
            return {'initial_fund': 100000.0}

        try:
            user_prefix = self._get_user_prefix()
            key = f"{user_prefix}portfolio_settings"

            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return {'initial_fund': 100000.0}
        except Exception as e:
            print(f"Error loading portfolio settings: {e}")
            return {'initial_fund': 100000.0}

    def test_redis_connection(self) -> Dict[str, Any]:
        """Test Redis connection and return status"""
        if self.app_mode != 'redis':
            return {'connected': False, 'error': 'Not in Redis mode'}

        try:
            if self.redis_client:
                # Test basic operations
                test_key = "test_connection"
                test_value = "Redis is working!"

                self.redis_client.set(test_key, test_value, ex=10)  # Expire in 10 seconds
                result = self.redis_client.get(test_key)

                return {
                    'connected': True,
                    'test_result': result,
                    'config': {
                        'host': self.config.REDIS_HOST,
                        'port': self.config.REDIS_PORT,
                        'password_set': bool(self.config.REDIS_PASSWORD)
                    }
                }
            else:
                return {'connected': False, 'error': 'Redis client not initialized'}
        except Exception as e:
            return {'connected': False, 'error': str(e)}
