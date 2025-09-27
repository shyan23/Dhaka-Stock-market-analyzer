import json
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path

class StorageMigrator:
    """Service to handle migration between different storage backends"""

    def __init__(self, data_manager=None):
        self.data_manager = data_manager

    def migrate_storage(self, from_type: str, to_type: str, config_data: Dict[str, Any] = None) -> bool:
        """
        Migrate data from one storage type to another

        Args:
            from_type: Source storage type ('redis' or 'google_sheets')
            to_type: Target storage type ('redis' or 'google_sheets')
            config_data: Configuration data for the target storage

        Returns:
            bool: Success status
        """
        try:
            # Step 1: Backup current data
            backup_data = self._create_full_backup()
            if not backup_data:
                st.error("Failed to create backup of current data")
                return False

            # Step 2: Update configuration
            success = self._update_storage_config(to_type, config_data)
            if not success:
                st.error("Failed to update storage configuration")
                return False

            # Step 3: Reinitialize data manager with new config
            from src.services.data_manager import DataManager
            from config import Config

            # Force reload of config
            new_config = Config()
            new_data_manager = DataManager()

            # Step 4: Restore data to new storage
            success = self._restore_data_to_storage(backup_data, new_data_manager, to_type)
            if not success:
                st.error("Failed to restore data to new storage")
                # Rollback configuration
                self._update_storage_config(from_type, config_data)
                return False

            # Step 5: Update session state
            self._update_session_state(new_data_manager)

            # Step 6: Save storage type preference to Redis
            self._save_storage_preference(to_type)

            st.success(f"Successfully migrated from {from_type} to {to_type}!")
            return True

        except Exception as e:
            st.error(f"Migration failed: {str(e)}")
            return False

    def _create_full_backup(self) -> Optional[Dict[str, Any]]:
        """Create a complete backup of current data"""
        try:
            backup_data = {
                'selected_stocks': st.session_state.get('selected_stocks', []),
                'portfolio_items': {},
                'transactions': [],
                'backup_timestamp': datetime.now().isoformat(),
                'source_storage_type': st.session_state.get('app_mode', 'redis')
            }

            # Backup portfolio items
            portfolio_items = st.session_state.get('portfolio_items', {})
            for symbol, item in portfolio_items.items():
                if hasattr(item, 'to_dict'):
                    backup_data['portfolio_items'][symbol] = item.to_dict()
                else:
                    # Manual conversion if to_dict doesn't exist
                    backup_data['portfolio_items'][symbol] = {
                        'symbol': item.symbol,
                        'quantity': item.quantity,
                        'average_cost': item.average_cost,
                        'current_price': item.current_price,
                        'last_updated': item.last_updated.isoformat() if hasattr(item, 'last_updated') else datetime.now().isoformat()
                    }

            # Backup transactions
            transactions = st.session_state.get('transactions', [])
            for trans in transactions:
                if hasattr(trans, 'to_dict'):
                    backup_data['transactions'].append(trans.to_dict())
                else:
                    # Manual conversion if to_dict doesn't exist
                    backup_data['transactions'].append({
                        'symbol': trans.symbol,
                        'transaction_type': trans.transaction_type.value if hasattr(trans.transaction_type, 'value') else str(trans.transaction_type),
                        'quantity': trans.quantity,
                        'price': trans.price,
                        'timestamp': trans.timestamp.isoformat() if hasattr(trans, 'timestamp') else datetime.now().isoformat(),
                        'notes': getattr(trans, 'notes', '')
                    })

            return backup_data

        except Exception as e:
            st.error(f"Failed to create backup: {str(e)}")
            return None

    def _update_storage_config(self, storage_type: str, config_data: Dict[str, Any] = None) -> bool:
        """Update storage configuration in config.json and environment"""
        try:
            # Update config.json
            config_path = Path("config.json")
            current_config = {}

            if config_path.exists():
                with open(config_path, 'r') as f:
                    current_config = json.load(f)

            # Update storage configuration
            current_config.update({
                'storage_type': storage_type,
                'app_mode': storage_type,
                'last_updated': datetime.now().isoformat()
            })

            # Add specific configuration for the storage type
            if config_data:
                current_config.update(config_data)

            # Write updated configuration
            with open(config_path, 'w') as f:
                json.dump(current_config, f, indent=2)

            # Update environment variable for current session
            os.environ['APP_MODE'] = storage_type

            # Save to Redis if available (for persistence across container restarts)
            self._save_storage_preference(storage_type)

            return True

        except Exception as e:
            st.error(f"Failed to update configuration: {str(e)}")
            return False

    def _restore_data_to_storage(self, backup_data: Dict[str, Any], data_manager, storage_type: str) -> bool:
        """Restore data to the new storage backend"""
        try:
            # Restore transactions first (portfolio is calculated from transactions)
            transactions = backup_data.get('transactions', [])

            for trans_data in transactions:
                # Recreate transaction object
                from src.models.portfolio import Transaction, TransactionType

                transaction = Transaction(
                    symbol=trans_data['symbol'],
                    transaction_type=TransactionType(trans_data['transaction_type']),
                    quantity=trans_data['quantity'],
                    price=trans_data['price'],
                    timestamp=datetime.fromisoformat(trans_data['timestamp']),
                    notes=trans_data.get('notes', '')
                )

                # Save to new storage
                success = data_manager.save_transaction(transaction)
                if not success:
                    st.warning(f"Failed to save transaction for {trans_data['symbol']}")

            # Restore selected stocks to Redis (if using Redis)
            if storage_type == 'redis' and data_manager.redis_client:
                selected_stocks = backup_data.get('selected_stocks', [])
                stocks_json = json.dumps(selected_stocks)
                data_manager.redis_client.set("app:selected_stocks", stocks_json)

            return True

        except Exception as e:
            st.error(f"Failed to restore data: {str(e)}")
            return False

    def _update_session_state(self, new_data_manager):
        """Update Streamlit session state with new data manager"""
        try:
            # Update app instance in session state
            if hasattr(st.session_state, 'app_instance'):
                st.session_state.app_instance.data_manager = new_data_manager

                # Reload data from new storage
                st.session_state.selected_stocks = st.session_state.app_instance._load_selected_stocks()
                st.session_state.portfolio_items = st.session_state.app_instance._load_portfolio_items()
                st.session_state.transactions = st.session_state.app_instance._load_transactions()

                # Update app mode
                from config import Config
                new_config = Config()
                st.session_state.app_mode = new_config.APP_MODE

        except Exception as e:
            st.warning(f"Session state update warning: {str(e)}")

    def _save_storage_preference(self, storage_type: str):
        """Save storage preference to Redis for persistence"""
        try:
            # Try to connect to Redis to save preference
            import redis
            from config import Config

            config = Config()
            redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
                decode_responses=True
            )

            # Save storage preference
            preference_data = {
                'storage_type': storage_type,
                'last_updated': datetime.now().isoformat()
            }

            redis_client.set("app:storage_preference", json.dumps(preference_data))

        except Exception as e:
            # Silently fail - this is just for convenience
            pass

    def get_storage_preference(self) -> Optional[str]:
        """Get stored storage preference from Redis"""
        try:
            import redis
            from config import Config

            config = Config()
            redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
                decode_responses=True
            )

            preference_data = redis_client.get("app:storage_preference")
            if preference_data:
                data = json.loads(preference_data)
                return data.get('storage_type')

        except Exception as e:
            # Silently fail - return None
            pass

        return None

    def test_storage_connection(self, storage_type: str, config_data: Dict[str, Any] = None) -> bool:
        """Test connection to a storage backend"""
        try:
            if storage_type == 'redis':
                import redis
                from config import Config

                config = Config()
                redis_client = redis.Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
                    decode_responses=True
                )

                # Test connection
                redis_client.ping()
                return True

            elif storage_type == 'google_sheets':
                from src.services.google_sheets import GoogleSheetsService

                # Get credentials file path from config_data
                credentials_file = config_data.get('google_credentials_file', '')
                sheet_id = config_data.get('google_sheet_id', '')

                if not credentials_file or not sheet_id:
                    return False

                # Test Google Sheets connection
                sheets_service = GoogleSheetsService(credentials_file, sheet_id)
                return sheets_service.is_connected()

        except Exception as e:
            return False

        return False