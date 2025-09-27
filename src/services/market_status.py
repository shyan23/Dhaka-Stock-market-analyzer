from datetime import datetime, time, timedelta
from typing import Dict, Any
import pytz

class MarketStatusService:
    def __init__(self):
        # DSE trading hours (Bangladesh Standard Time)
        self.bst_tz = pytz.timezone('Asia/Dhaka')
        self.market_open_time = time(10, 30)  # 10:30 AM
        self.market_close_time = time(14, 30)  # 2:30 PM

        # DSE trading days (Sunday to Thursday in Bangladesh)
        self.trading_days = [6, 0, 1, 2, 3]  # Sunday=6, Monday=0, etc.

    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        now_bst = datetime.now(self.bst_tz)
        current_time = now_bst.time()
        current_weekday = now_bst.weekday()

        is_trading_day = current_weekday in self.trading_days
        is_trading_hours = (
            self.market_open_time <= current_time <= self.market_close_time
        )

        market_open = is_trading_day and is_trading_hours

        # Calculate next market session
        if market_open:
            status = "OPEN"
            next_change = "Market closes"
            next_time = now_bst.replace(
                hour=self.market_close_time.hour,
                minute=self.market_close_time.minute,
                second=0,
                microsecond=0
            )
        else:
            status = "CLOSED"
            if is_trading_day and current_time < self.market_open_time:
                # Same day, before opening
                next_change = "Market opens"
                next_time = now_bst.replace(
                    hour=self.market_open_time.hour,
                    minute=self.market_open_time.minute,
                    second=0,
                    microsecond=0
                )
            else:
                # Find next trading day
                next_change = "Market opens"
                days_ahead = 1
                next_day = now_bst.weekday() + 1
                while (next_day % 7) not in self.trading_days:
                    days_ahead += 1
                    next_day += 1

                next_time = now_bst.replace(
                    hour=self.market_open_time.hour,
                    minute=self.market_open_time.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(days=days_ahead)

        time_until_change = next_time - now_bst
        hours, remainder = divmod(time_until_change.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        return {
            'status': status,
            'is_open': market_open,
            'current_time': now_bst.strftime('%H:%M:%S BST'),
            'next_change': next_change,
            'time_until_change': f"{int(hours):02d}:{int(minutes):02d}",
            'market_hours': f"{self.market_open_time.strftime('%H:%M')} - {self.market_close_time.strftime('%H:%M')} BST",
            'trading_days': "Sunday - Thursday"
        }

    def is_market_open(self) -> bool:
        """Simple check if market is currently open"""
        return self.get_market_status()['is_open']