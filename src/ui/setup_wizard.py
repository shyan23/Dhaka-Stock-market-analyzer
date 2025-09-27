import streamlit as st
import os
import json
from typing import Dict, Any
from config import Config

class SetupWizardUI:
    def __init__(self):
        self.config = Config()
    
    def render(self):
        """Render the setup wizard"""
        st.title("🚀 Stock Market Analyzer Setup")
        st.markdown("Welcome! Let's set up your Stock Market Analyzer.")
        
        # Check if already configured
        if self._is_already_configured():
            st.success("✅ Configuration found! Your app is ready to use.")
            if st.button("🔄 Reconfigure"):
                self._clear_configuration()
                st.rerun()
            return
        
        # Database selection
        st.header("📊 Choose Your Data Storage")
        st.markdown("Select how you want to store your portfolio and transaction data:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗄️ Local Database (Redis)")
            st.markdown("""
            **Features:**
            - ✅ Fast local storage
            - ✅ No internet required after setup
            - ✅ Complete privacy
            - ✅ Easy to backup
            
            **Requirements:**
            - Redis server installed locally
            - Minimal setup required
            """)
            
            if st.button("Choose Redis", key="choose_redis", type="primary"):
                st.session_state.setup_mode = "redis"
                st.rerun()
        
        with col2:
            st.subheader("📈 Google Sheets Integration")
            st.markdown("""
            **Features:**
            - ✅ Access from anywhere
            - ✅ Automatic backups
            - ✅ Share with advisors
            - ✅ Export to Excel
            
            **Requirements:**
            - Google account
            - Google Sheets API setup
            - Service account credentials
            """)
            
            if st.button("Choose Google Sheets", key="choose_sheets"):
                st.session_state.setup_mode = "google_sheets"
                st.rerun()
        
        # Configuration based on selection
        if 'setup_mode' in st.session_state:
            if st.session_state.setup_mode == "redis":
                self._render_redis_setup()
            elif st.session_state.setup_mode == "google_sheets":
                self._render_google_sheets_setup()
    
    def _is_already_configured(self) -> bool:
        """Check if the app is already configured"""
        return (os.path.exists('.env') and 
                (self.config.APP_MODE == "redis" or 
                 (self.config.APP_MODE == "google_sheets" and 
                  self.config.GOOGLE_CREDENTIALS_FILE and 
                  self.config.GOOGLE_SHEET_ID)))
    
    def _clear_configuration(self):
        """Clear existing configuration"""
        if os.path.exists('.env'):
            os.remove('.env')
        st.success("Configuration cleared. Please restart the app.")
    
    def _render_redis_setup(self):
        """Render Redis setup configuration"""
        st.header("🗄️ Redis Database Setup")
        
        st.info("""
        **Redis Setup Instructions:**
        
        1. **Install Redis:**
           - Windows: Download from https://github.com/microsoftarchive/redis/releases
           - macOS: `brew install redis`
           - Linux: `sudo apt-get install redis-server`
        
        2. **Start Redis Server:**
           - Windows: Run `redis-server.exe`
           - macOS/Linux: `redis-server`
        
        3. **Configure Connection:**
        """)
        
        with st.form("redis_config"):
            st.subheader("Redis Configuration")
            
            redis_host = st.text_input(
                "Redis Host",
                value="localhost",
                help="Usually 'localhost' for local installation"
            )
            
            redis_port = st.number_input(
                "Redis Port",
                value=6379,
                min_value=1,
                max_value=65535,
                help="Default Redis port is 6379"
            )
            
            redis_password = st.text_input(
                "Redis Password (optional)",
                type="password",
                help="Leave empty if no password is set"
            )
            
            # Test connection
            test_connection = st.checkbox("Test connection", value=True)
            
            submitted = st.form_submit_button("Save Redis Configuration", type="primary")
            
            if submitted:
                if test_connection:
                    if self._test_redis_connection(redis_host, redis_port, redis_password):
                        self._save_redis_config(redis_host, redis_port, redis_password)
                        st.success("✅ Redis configuration saved successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to connect to Redis. Please check your configuration.")
                else:
                    self._save_redis_config(redis_host, redis_port, redis_password)
                    st.success("✅ Redis configuration saved!")
                    st.rerun()
    
    def _render_google_sheets_setup(self):
        """Render Google Sheets setup configuration"""
        st.header("📈 Google Sheets Integration Setup")
        
        # Step-by-step instructions
        st.markdown("""
        ## 📋 Setup Instructions
        
        Follow these steps to set up Google Sheets integration:
        """)
        
        with st.expander("Step 1: Create Google Cloud Project", expanded=True):
            st.markdown("""
            **1.1 Create a new Google Cloud Project:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Click "Select a project" → "New Project"
            3. Enter project name: `Stock Market Analyzer`
            4. Click "Create"
            """)
        
        with st.expander("Step 2: Enable Google Sheets API", expanded=True):
            st.markdown("""
            **2.1 Enable the Google Sheets API:**
            1. In your project, go to "APIs & Services" → "Library"
            2. Search for "Google Sheets API"
            3. Click on it and press "Enable"
            """)
        
        with st.expander("Step 3: Create Service Account", expanded=True):
            st.markdown("""
            **3.1 Create a Service Account:**
            1. Go to "APIs & Services" → "Credentials"
            2. Click "Create Credentials" → "Service Account"
            3. Enter name: `stock-analyzer-service`
            4. Click "Create and Continue"
            5. Skip role assignment for now, click "Continue"
            6. Click "Done"
            """)
        
        with st.expander("Step 4: Generate Service Account Key", expanded=True):
            st.markdown("""
            **4.1 Generate and download the key:**
            1. In "Credentials" page, find your service account
            2. Click on the service account email
            3. Go to "Keys" tab → "Add Key" → "Create new key"
            4. Choose "JSON" format
            5. Click "Create" - this downloads the credentials file
            6. Save it as `service-account-key.json`
            """)
        
        with st.expander("Step 5: Create Google Sheet", expanded=True):
            st.markdown("""
            **5.1 Create a new Google Sheet:**
            1. Go to [Google Sheets](https://sheets.google.com/)
            2. Click "Blank" to create a new sheet
            3. Name it "Stock Market Portfolio"
            4. Copy the Sheet ID from the URL:
               ```
               https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
               ```
            """)
        
        with st.expander("Step 6: Share Sheet with Service Account", expanded=True):
            st.markdown("""
            **6.1 Share the sheet with your service account:**
            1. In your Google Sheet, click "Share" button
            2. Add the service account email (from the JSON file)
            3. Give it "Editor" permissions
            4. Click "Send"
            """)
        
        st.markdown("---")
        
        # File upload and configuration
        st.subheader("📁 Upload Configuration Files")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Upload Service Account Key:**")
            uploaded_file = st.file_uploader(
                "Choose JSON file",
                type=['json'],
                help="Upload the service-account-key.json file you downloaded"
            )
        
        with col2:
            st.markdown("**Enter Google Sheet Details:**")
            sheet_id = st.text_input(
                "Google Sheet ID",
                placeholder="1ABC123...",
                help="The ID from your Google Sheet URL"
            )
        
        if uploaded_file and sheet_id:
            # Process the uploaded file
            try:
                # Save the credentials file
                credentials_content = uploaded_file.read().decode('utf-8')
                
                # Validate JSON
                credentials_data = json.loads(credentials_content)
                
                if 'type' in credentials_data and credentials_data['type'] == 'service_account':
                    # Save to file
                    credentials_file_path = 'service-account-key.json'
                    with open(credentials_file_path, 'w') as f:
                        f.write(credentials_content)
                    
                    # Save configuration
                    self._save_google_sheets_config(credentials_file_path, sheet_id)
                    
                    st.success("✅ Google Sheets configuration saved successfully!")
                    
                    # Test connection
                    if self._test_google_sheets_connection():
                        st.success("✅ Connection to Google Sheets successful!")
                        st.balloons()
                        
                        # Show next steps
                        st.info("""
                        **🎉 Setup Complete!**

                        Your Stock Market Analyzer is now configured with Google Sheets integration.
                        The app will automatically create the following sheets:
                        - Stock_Data: Current stock prices
                        - Historical_Data: Price history
                        - Transactions: Your buy/sell transactions
                        - Portfolio: Current holdings
                        - Portfolio_History: Portfolio performance over time
                        """)

                        st.rerun()
                    else:
                        st.error("❌ Failed to connect to Google Sheets. Please check your configuration.")
                
                else:
                    st.error("❌ Invalid service account key file. Please upload the correct JSON file.")
            
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please upload a valid service account key file.")
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")
        
        # Alternative: Manual configuration
        st.markdown("---")
        st.subheader("🔧 Manual Configuration")
        
        with st.expander("Enter configuration manually"):
            with st.form("manual_sheets_config"):
                credentials_path = st.text_input(
                    "Path to credentials file",
                    value="service-account-key.json",
                    help="Path to your service account JSON file"
                )
                
                manual_sheet_id = st.text_input(
                    "Google Sheet ID",
                    placeholder="1ABC123...",
                    help="The ID from your Google Sheet URL"
                )
                
                if st.form_submit_button("Save Manual Configuration"):
                    if os.path.exists(credentials_path):
                        self._save_google_sheets_config(credentials_path, manual_sheet_id)
                        if self._test_google_sheets_connection():
                            st.success("✅ Manual configuration saved and tested!")
                            st.rerun()
                        else:
                            st.error("❌ Configuration saved but connection failed.")
                    else:
                        st.error(f"❌ Credentials file not found: {credentials_path}")
    
    def _test_redis_connection(self, host: str, port: int, password: str) -> bool:
        """Test Redis connection"""
        try:
            import redis
            client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                decode_responses=True
            )
            client.ping()
            return True
        except Exception as e:
            st.error(f"Redis connection error: {e}")
            return False
    
    def _test_google_sheets_connection(self) -> bool:
        """Test Google Sheets connection"""
        try:
            from src.services.google_sheets import GoogleSheetsService
            service = GoogleSheetsService()
            return service.is_connected()
        except Exception as e:
            st.error(f"Google Sheets connection error: {e}")
            return False
    
    def _save_redis_config(self, host: str, port: int, password: str):
        """Save Redis configuration to .env file"""
        env_content = f"""
# Redis Configuration
REDIS_HOST={host}
REDIS_PORT={port}
REDIS_PASSWORD={password}

# App Configuration
APP_MODE=redis
YAHOO_FINANCE_ENABLED=true
UPDATE_INTERVAL_MINUTES=5
"""
        
        with open('.env', 'w') as f:
            f.write(env_content.strip())
    
    def _save_google_sheets_config(self, credentials_path: str, sheet_id: str):
        """Save Google Sheets configuration to .env file"""
        env_content = f"""
# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE={credentials_path}
GOOGLE_SHEET_ID={sheet_id}

# App Configuration
APP_MODE=google_sheets
YAHOO_FINANCE_ENABLED=true
UPDATE_INTERVAL_MINUTES=5
"""
        
        with open('.env', 'w') as f:
            f.write(env_content.strip())
