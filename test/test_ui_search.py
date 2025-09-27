#!/usr/bin/env python3
"""
Test the UI search functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager
from src.ui.stock_selector import StockSelectorUI

def test_ui_search():
    print("🧪 Testing Stock Selector UI Components...")

    # Initialize services
    dse_api = DSEAPIService()
    data_manager = DataManager()
    stock_selector = StockSelectorUI(dse_api, data_manager)

    print("✅ Services initialized successfully")

    # Test the search logic that the UI uses
    print("\n🔍 Testing search logic...")

    test_queries = ['GP', 'BRAC', 'SQUARE', 'ACI', 'UNI']
    for query in test_queries:
        try:
            results = dse_api.search_stocks(query)
            print(f"Query '{query}': {len(results)} results")
            for i, result in enumerate(results[:2]):
                symbol = result.get('symbol', 'N/A')
                name = result.get('name', 'N/A')
                price = result.get('last_trade_price', 0)
                print(f"  {i+1}. {symbol} - {name} - ৳{price}")
        except Exception as e:
            print(f"Error searching for '{query}': {e}")

    print("\n✅ UI search testing completed!")

    # Test stock addition logic
    print("\n📝 Testing stock addition logic...")

    # Initialize mock session state
    class MockSessionState:
        def __init__(self):
            self.selected_stocks = []

    mock_session = MockSessionState()

    # Simulate adding stocks
    test_stocks = ['GP', 'BRACBANK', 'ACI']
    for stock in test_stocks:
        if stock not in mock_session.selected_stocks:
            mock_session.selected_stocks.append(stock)
            print(f"✅ Added {stock} to tracking")
        else:
            print(f"⚠️ {stock} already in tracking")

    print(f"\n📊 Final tracking list: {mock_session.selected_stocks}")

if __name__ == "__main__":
    test_ui_search()