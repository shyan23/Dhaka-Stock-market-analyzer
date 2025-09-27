import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Reload environment variables each time Config is instantiated
        load_dotenv(override=True)

        # Google Sheets Configuration
        self.GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', '')
        self.GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')

        # Redis Configuration
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

        # Stock Data Configuration
        self.YAHOO_FINANCE_ENABLED = os.getenv('YAHOO_FINANCE_ENABLED', 'true').lower() == 'true'
        self.UPDATE_INTERVAL_MINUTES = int(os.getenv('UPDATE_INTERVAL_MINUTES', 5))

        # App Configuration
        self.APP_MODE = os.getenv('APP_MODE', 'google_sheets')  # 'google_sheets' or 'redis'

        # Sheet Names (for Google Sheets version)
        self.MAIN_SHEET = 'Stock_Data'
        self.HISTORICAL_SHEET = 'Historical_Data'
        self.TRANSACTIONS_SHEET = 'Transactions'
        self.PORTFOLIO_SHEET = 'Portfolio'
        self.PORTFOLIO_HISTORY_SHEET = 'Portfolio_History'
    
        # DSE API Configuration
        self.DSE_BASE_URL = 'https://www.dsebd.org'
        self.DSE_API_ENDPOINTS = {
            'quotes_txt': '/datafile/quotes.txt',
            'company_details': '/displayCompany.php',
            'top_20_shares': '/top_20_share.php',
            'historical_archive': '/day_end_archive.php',
            'latest_by_ltp': '/latest_share_price_scroll_by_ltp.php',
            'latest_by_change': '/latest_share_price_scroll_by_change.php',
            'latest_by_value': '/latest_share_price_scroll_by_value.php',
            'suggest_list': '/ajax/suggestList.php'
        }


