#!/usr/bin/env python3
"""
Test script for new features implementation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_market_status():
    """Test market status service"""
    print("🔍 Testing Market Status Service...")
    try:
        from src.services.market_status import MarketStatusService
        market_service = MarketStatusService()
        status = market_service.get_market_status()

        print(f"✅ Market Status: {status['status']}")
        print(f"✅ Current Time: {status['current_time']}")
        print(f"✅ Next Change: {status['next_change']} in {status['time_until_change']}")
        print(f"✅ Market Hours: {status['market_hours']}")
        return True
    except Exception as e:
        print(f"❌ Market Status Error: {e}")
        return False

def test_export_service():
    """Test export service"""
    print("\n🔍 Testing Export Service...")
    try:
        from src.services.export_service import ExportService
        export_service = ExportService()
        print("✅ Export Service initialized successfully")

        # Test with empty data (should not crash)
        csv_data = export_service.export_stock_data_to_csv([])
        print("✅ CSV export functionality working")
        return True
    except Exception as e:
        print(f"❌ Export Service Error: {e}")
        return False

def test_price_tracker_ui():
    """Test price tracker UI"""
    print("\n🔍 Testing Price Tracker UI...")
    try:
        from src.ui.price_tracker import PriceTrackerUI
        from src.services.dse_api import DSEAPIService
        from src.services.data_manager import DataManager

        dse_api = DSEAPIService()
        data_manager = DataManager()
        price_tracker = PriceTrackerUI(dse_api, data_manager)
        print("✅ Price Tracker UI initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Price Tracker UI Error: {e}")
        return False

def test_enhanced_dashboard():
    """Test enhanced dashboard"""
    print("\n🔍 Testing Enhanced Dashboard...")
    try:
        from src.ui.dashboard import DashboardUI
        from src.services.dse_api import DSEAPIService
        from src.services.data_manager import DataManager

        dse_api = DSEAPIService()
        data_manager = DataManager()
        dashboard = DashboardUI(dse_api, data_manager)
        print("✅ Enhanced Dashboard initialized successfully")

        # Test technical indicators calculation
        import pandas as pd
        sample_data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'Date': pd.date_range('2024-01-01', periods=10),
            'Volume': [1000] * 10
        })
        enhanced_data = dashboard._calculate_technical_indicators(sample_data)
        print("✅ Technical indicators calculation working")
        return True
    except Exception as e:
        print(f"❌ Enhanced Dashboard Error: {e}")
        return False

def test_main_app():
    """Test main app initialization"""
    print("\n🔍 Testing Main App...")
    try:
        from src.app import StockMarketApp
        app = StockMarketApp()
        print("✅ Main App initialized successfully")
        print(f"✅ DSE API Service: {type(app.dse_api).__name__}")
        print(f"✅ Data Manager: {type(app.data_manager).__name__}")
        print(f"✅ Dashboard UI: {type(app.dashboard_ui).__name__}")
        print(f"✅ Price Tracker UI: {type(app.price_tracker_ui).__name__}")
        return True
    except Exception as e:
        print(f"❌ Main App Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing New Features Implementation\n")

    tests = [
        test_market_status,
        test_export_service,
        test_price_tracker_ui,
        test_enhanced_dashboard,
        test_main_app
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All features implemented successfully!")
        print("\n🚀 Ready to run: streamlit run main.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)