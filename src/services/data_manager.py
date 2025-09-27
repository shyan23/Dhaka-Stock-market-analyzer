import json
import redis
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
from config import Config
from src.models.stock import Stock, StockPriceHistory
from src.models.portfolio import Transaction, PortfolioItem, PortfolioSnapshot

class DataManager:
    def __init__(self):
        self.config = Config()
        self.app_mode = self.config.APP_MODE
        
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
            print("Redis connection established")
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
    
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
