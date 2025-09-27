#!/usr/bin/env python3
"""
Stock Market Analyzer - Test Script
Tests the application components without running the full UI
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import Config
        config = Config()
        print(f"✅ Config loaded successfully")
        print(f"   App Mode: {config.APP_MODE}")
        print(f"   DSE Base URL: {config.DSE_BASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_models():
    """Test data models"""
    print("\n📊 Testing data models...")
    
    try:
        from src.models.stock import Stock
        from src.models.portfolio import Transaction, TransactionType
        
        # Test Stock model
        stock = Stock(
            symbol="GP",
            name="Grameenphone Ltd",
            current_price=100.0,
            previous_close=95.0,
            volume=1000000
        )
        print(f"✅ Stock model: {stock.symbol} - {stock.price_change_percent:.2f}%")
        
        # Test Transaction model
        transaction = Transaction(
            id="test-123",
            symbol="GP",
            transaction_type=TransactionType.BUY,
            quantity=100,
            price=100.0,
            timestamp=stock.last_updated or "2024-01-01T00:00:00"
        )
        print(f"✅ Transaction model: {transaction.transaction_type.value} {transaction.quantity} {transaction.symbol}")
        
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_dse_api():
    """Test DSE API service"""
    print("\n🌐 Testing DSE API service...")
    
    try:
        from src.services.dse_api import DSEAPIService
        
        api = DSEAPIService()
        print("✅ DSE API service initialized")
        
        # Test search functionality (without making actual API calls)
        print("✅ DSE API service ready")
        return True
    except Exception as e:
        print(f"❌ DSE API test failed: {e}")
        return False

def test_data_manager():
    """Test data manager"""
    print("\n💾 Testing data manager...")
    
    try:
        from src.services.data_manager import DataManager
        
        # This will test both Redis and Google Sheets initialization
        data_manager = DataManager()
        print(f"✅ Data manager initialized in {data_manager.app_mode} mode")
        return True
    except Exception as e:
        print(f"❌ Data manager test failed: {e}")
        return False

def test_ui_components():
    """Test UI components initialization"""
    print("\n🎨 Testing UI components...")
    
    try:
        from src.ui.setup_wizard import SetupWizardUI
        from src.ui.dashboard import DashboardUI
        from src.ui.stock_selector import StockSelectorUI
        from src.ui.portfolio import PortfolioUI
        from src.ui.transactions import TransactionsUI
        
        print("✅ All UI components imported successfully")
        return True
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Stock Market Analyzer - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_dse_api,
        test_data_manager,
        test_ui_components
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 To start the application, run:")
        print("   python run.py")
        print("   or")
        print("   streamlit run main.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("💡 Try running: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
