"""
Time Range Selector Component for Stock Market Analyzer
Provides reusable time range selection functionality for charts
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any


class TimeRangeSelector:
    """Reusable component for selecting time ranges for charts"""

    # Predefined time ranges
    PREDEFINED_RANGES = {
        "1W": {"days": 7, "label": "1 Week"},
        "2W": {"days": 14, "label": "2 Weeks"},
        "1M": {"days": 30, "label": "1 Month"},
        "3M": {"days": 90, "label": "3 Months"},
        "6M": {"days": 180, "label": "6 Months"},
        "1Y": {"days": 365, "label": "1 Year"},
        "2Y": {"days": 730, "label": "2 Years"},
        "Custom": {"days": None, "label": "Custom Range"}
    }

    def __init__(self, default_range: str = "1M"):
        """
        Initialize the time range selector

        Args:
            default_range: Default time range key (e.g., "1M", "3M", "1Y")
        """
        self.default_range = default_range

    def render(self,
               key_prefix: str = "time_range",
               show_custom: bool = True,
               compact: bool = False) -> Tuple[datetime, datetime]:
        """
        Render the time range selector and return start and end dates

        Args:
            key_prefix: Unique prefix for component keys
            show_custom: Whether to show custom range option
            compact: Whether to use compact layout

        Returns:
            Tuple of (start_date, end_date)
        """
        if compact:
            return self._render_compact(key_prefix, show_custom)
        else:
            return self._render_full(key_prefix, show_custom)

    def _render_compact(self, key_prefix: str, show_custom: bool) -> Tuple[datetime, datetime]:
        """Render compact version in a single row"""
        col1, col2 = st.columns([2, 3])

        with col1:
            st.write("**Time Range:**")

        with col2:
            # Filter ranges if custom is not shown
            available_ranges = dict(self.PREDEFINED_RANGES)
            if not show_custom:
                available_ranges.pop("Custom", None)

            selected_range = st.selectbox(
                "Range",
                options=list(available_ranges.keys()),
                format_func=lambda x: available_ranges[x]["label"],
                index=list(available_ranges.keys()).index(self.default_range) if self.default_range in available_ranges else 0,
                key=f"{key_prefix}_compact_select",
                label_visibility="collapsed"
            )

            return self._calculate_dates(selected_range, key_prefix, show_custom)

    def _render_full(self, key_prefix: str, show_custom: bool) -> Tuple[datetime, datetime]:
        """Render full version with detailed controls"""
        st.write("**📅 Select Time Range:**")

        col1, col2 = st.columns([1, 2])

        with col1:
            # Filter ranges if custom is not shown
            available_ranges = dict(self.PREDEFINED_RANGES)
            if not show_custom:
                available_ranges.pop("Custom", None)

            selected_range = st.selectbox(
                "Time Period",
                options=list(available_ranges.keys()),
                format_func=lambda x: available_ranges[x]["label"],
                index=list(available_ranges.keys()).index(self.default_range) if self.default_range in available_ranges else 0,
                key=f"{key_prefix}_full_select"
            )

        with col2:
            # Show date preview
            start_date, end_date = self._calculate_dates(selected_range, key_prefix, show_custom)
            st.info(f"📊 **Data Range:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        return start_date, end_date

    def _calculate_dates(self, selected_range: str, key_prefix: str, show_custom: bool) -> Tuple[datetime, datetime]:
        """Calculate start and end dates based on selected range"""
        end_date = datetime.now()

        if selected_range == "Custom" and show_custom:
            # Custom date range selection
            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=end_date.date() - timedelta(days=30),
                    max_value=end_date.date(),
                    key=f"{key_prefix}_start_date"
                )

            with col2:
                end_date_input = st.date_input(
                    "End Date",
                    value=end_date.date(),
                    min_value=start_date if 'start_date' in locals() else end_date.date() - timedelta(days=365),
                    max_value=end_date.date(),
                    key=f"{key_prefix}_end_date"
                )

            # Convert to datetime
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date_input, datetime.max.time())

        else:
            # Predefined range
            range_config = self.PREDEFINED_RANGES[selected_range]
            days = range_config["days"]
            start_date = end_date - timedelta(days=days)

        return start_date, end_date

    def get_range_info(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get information about the selected range"""
        duration = end_date - start_date

        return {
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration.days,
            "duration_text": self._format_duration(duration.days),
            "is_weekend_included": True,  # Always true for stock data
            "trading_days_estimate": max(1, int(duration.days * 5/7))  # Rough estimate
        }

    def _format_duration(self, days: int) -> str:
        """Format duration in human-readable text"""
        if days <= 7:
            return f"{days} day{'s' if days != 1 else ''}"
        elif days <= 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''}"
        elif days <= 365:
            months = days // 30
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            years = days // 365
            return f"{years} year{'s' if years != 1 else ''}"


def create_time_range_selector(default_range: str = "1M") -> TimeRangeSelector:
    """Factory function to create a time range selector"""
    return TimeRangeSelector(default_range)