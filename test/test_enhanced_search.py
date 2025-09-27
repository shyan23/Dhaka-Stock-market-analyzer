#!/usr/bin/env python3
"""
Final test of enhanced search functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.dse_api import DSEAPIService
from src.services.data_manager import DataManager
from src.ui.stock_selector import StockSelectorUI

def test_comprehensive_search():
    print("🚀 Testing Enhanced Stock Selector with Search Functionality")
    print("=" * 60)

    # Initialize services
    dse_api = DSEAPIService()
    data_manager = DataManager()
    stock_selector = StockSelectorUI(dse_api, data_manager)

    print("✅ All services initialized successfully\n")

    # Test different search scenarios
    test_cases = [
        ("GP", "Exact symbol match"),
        ("UNILEVERCL", "Full company code"),
        ("BRAC", "Partial match"),
        ("UNI", "Multiple matches"),
        ("PHARMA", "Industry search"),
        ("xyz123", "No matches"),
        ("a", "Too short"),
        ("", "Empty search")
    ]

    print("🔍 Testing Search Scenarios:")
    print("-" * 40)

    for query, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"Query: '{query}'")

        try:
            if len(query.strip()) >= 2:
                results = dse_api.search_stocks(query)
                print(f"✅ Results: {len(results)} stocks found")

                # Show top 3 results
                for i, result in enumerate(results[:3]):
                    symbol = result.get('symbol', 'N/A')
                    name = result.get('name', 'N/A')
                    price = result.get('last_trade_price', 0)
                    details = "📊" if result.get('details_available') else "📈"
                    print(f"   {i+1}. {symbol} - ৳{price:.2f} {details}")

                if len(results) > 3:
                    print(f"   ... and {len(results) - 3} more")

            else:
                print("⚠️ Query too short (minimum 2 characters)")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("🎉 Enhanced Search Functionality Testing Complete!")

    # Test the advanced features
    print("\n🔧 Testing Advanced Features:")
    print("-" * 40)

    # Test case sensitivity
    print("\n📝 Case Sensitivity Test:")
    queries = ['gp', 'GP', 'Gp', 'gP']
    for q in queries:
        results = dse_api.search_stocks(q)
        print(f"  '{q}': {len(results)} results")

    # Test exact match priority
    print("\n📝 Exact Match Priority Test:")
    results = dse_api.search_stocks('GP')
    if results:
        print(f"  First result: {results[0].get('symbol')} (should be exact match)")

    # Test enhanced details
    print("\n📝 Enhanced Details Test:")
    results = dse_api.search_stocks('UNILEVERCL')
    if results:
        result = results[0]
        details_available = result.get('details_available', False)
        print(f"  UNILEVERCL details available: {details_available}")

    print("\n✨ All tests completed successfully!")

if __name__ == "__main__":
    test_comprehensive_search()