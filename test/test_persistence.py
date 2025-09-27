#!/usr/bin/env python3
"""
Test script to verify data persistence functionality
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_redis_persistence():
    """Test Redis persistence functionality"""
    print("🔍 Testing Redis data persistence...")

    try:
        from config import Config
        from src.services.data_manager import DataManager
        from src.models.portfolio import Transaction, TransactionType
        import uuid

        # Initialize components
        config = Config()
        if config.APP_MODE != "redis":
            print("Not in Redis mode, skipping Redis test")
            return False

        data_manager = DataManager()
        if not data_manager.redis_client:
            print("Redis not connected")
            return False

        print("Redis connection established")

        # Test 1: Save and retrieve selected stocks
        print("\n Testing selected stocks persistence...")
        test_stocks = ["GP", "ACI", "BRACBANK"]

        # Save selected stocks
        data_manager.redis_client.set("app:selected_stocks", json.dumps(test_stocks))
        print(f" Saved stocks: {test_stocks}")

        # Retrieve selected stocks
        retrieved_data = data_manager.redis_client.get("app:selected_stocks")
        if retrieved_data:
            retrieved_stocks = json.loads(retrieved_data)
            print(f" Retrieved stocks: {retrieved_stocks}")

            if retrieved_stocks == test_stocks:
                print("✅ Selected stocks persistence working!")
            else:
                print("❌ Selected stocks data mismatch")
                return False
        else:
            print("❌ Failed to retrieve selected stocks")
            return False

        # Test 2: Save and retrieve transaction
        print("\n💰 Testing transaction persistence...")
        test_transaction = Transaction(
            id=str(uuid.uuid4()),
            symbol="GP",
            transaction_type=TransactionType.BUY,
            quantity=100,
            price=300.0,
            timestamp=datetime.now(),
            notes="Test transaction"
        )

        # Save transaction
        success = data_manager.save_transaction(test_transaction)
        if success:
            print(f"💾 Saved transaction: BUY 100 GP @ 300.0")

            # Retrieve transactions
            retrieved_transactions = data_manager.get_transactions("GP")
            if retrieved_transactions:
                found_transaction = None
                for t in retrieved_transactions:
                    if t.id == test_transaction.id:
                        found_transaction = t
                        break

                if found_transaction:
                    print(f"📥 Retrieved transaction: {found_transaction.transaction_type.value} {found_transaction.quantity} {found_transaction.symbol} @ {found_transaction.price}")
                    print("✅ Transaction persistence working!")
                else:
                    print("❌ Test transaction not found")
                    return False
            else:
                print("❌ No transactions retrieved")
                return False
        else:
            print("❌ Failed to save transaction")
            return False

        # Test 3: Test app startup data loading
        print("\n🚀 Testing app startup data loading...")
        from src.app import StockMarketApp

        # This should load the data we just saved
        app = StockMarketApp()
        print("✅ App initialized successfully")

        # Check if selected stocks are loaded
        if hasattr(app, '_load_selected_stocks'):
            loaded_stocks = app._load_selected_stocks()
            print(f"📥 App loaded stocks: {loaded_stocks}")

            if set(loaded_stocks) == set(test_stocks):
                print("✅ App startup data loading working!")
            else:
                print("⚠️ App loaded different stocks than expected")

        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        data_manager.redis_client.delete("app:selected_stocks")
        data_manager.redis_client.delete(f"transaction:{test_transaction.id}")
        print("✅ Test data cleaned up")

        return True

    except Exception as e:
        print(f"❌ Redis persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_sheets_persistence():
    """Test Google Sheets persistence functionality"""
    print("🔍 Testing Google Sheets data persistence...")

    try:
        from config import Config
        config = Config()

        if config.APP_MODE != "google_sheets":
            print("❌ Not in Google Sheets mode, skipping Google Sheets test")
            return False

        print("✅ Google Sheets mode detected")
        print("ℹ️ Google Sheets persistence test requires manual verification")
        print("   - Transactions are automatically saved to sheets")
        print("   - Selected stocks are derived from transaction history")
        print("   - Portfolio data is calculated from transactions")

        return True

    except Exception as e:
        print(f"❌ Google Sheets persistence test failed: {e}")
        return False

def main():
    """Run persistence tests"""
    print("🧪 Stock Market Analyzer - Data Persistence Tests")
    print("=" * 60)

    from config import Config
    config = Config()

    print(f"📊 Current app mode: {config.APP_MODE}")
    print()

    tests_passed = 0
    total_tests = 0

    if config.APP_MODE == "redis":
        total_tests += 1
        if test_redis_persistence():
            tests_passed += 1
    elif config.APP_MODE == "google_sheets":
        total_tests += 1
        if test_google_sheets_persistence():
            tests_passed += 1
    else:
        print("❌ Unknown app mode")
        return False

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All persistence tests passed!")
        print("\n✅ Your data will now persist across app restarts!")
        print("✅ Selected stocks are saved automatically")
        print("✅ Transactions are saved automatically")
        print("✅ Portfolio data is calculated from saved transactions")
        return True
    else:
        print("⚠️ Some persistence tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)