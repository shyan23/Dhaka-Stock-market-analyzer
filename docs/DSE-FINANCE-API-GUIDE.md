# 📊 DSE Finance API - Complete Guide

**A comprehensive guide to using the DSE Finance functionality that replicates Google Finance for Dhaka Stock Exchange**

---

## 🎯 Overview

The DSE Finance API provides Google Finance-like functionality specifically for the Dhaka Stock Exchange (DSE). It allows you to fetch real-time and historical stock data using simple function calls similar to `=GOOGLEFINANCE()` in Google Sheets.

### Key Features
- ✅ **Real-time DSE data** with current prices and market info
- ✅ **Historical data** with OHLCV (Open, High, Low, Close, Volume)
- ✅ **Market overview** with advancing/declining stocks
- ✅ **Bulk data export** in CSV and JSON formats
- ✅ **Excel/Google Sheets integration** ready
- ✅ **Simple API** similar to GOOGLEFINANCE

---

## 🚀 Quick Start

### Access DSE Finance
1. **Open** your Stock Market Analyzer
2. **Go to** the "DSE Finance" tab in the navigation
3. **Start exploring** the 4 main sections:
   - 🔍 Quick Lookup
   - 📈 Historical Data
   - 📊 Market Overview
   - 📥 Bulk Export

---

## 📖 API Reference

### Core Function: `DSEFINANCE()`

The main function that replicates Google Finance functionality:

```python
DSEFINANCE(symbol, attribute, start_date=None, end_date=None)
```

**Parameters:**
- `symbol` (string): DSE stock symbol (e.g., 'GP', 'SQURPHARMA')
- `attribute` (string): Type of data to fetch
- `start_date` (string, optional): Start date for historical data (YYYY-MM-DD)
- `end_date` (string, optional): End date for historical data (YYYY-MM-DD)

### Available Attributes

#### 1. Current Price Data
```python
DSEFINANCE('GP', 'price')
```
**Returns:**
```json
{
  "symbol": "GP",
  "price": 425.50,
  "high": 430.00,
  "low": 420.00,
  "previous_close": 422.00,
  "change": 3.50,
  "change_percent": 0.83,
  "volume": 125000,
  "value_mn": 53.45,
  "trades": 1250,
  "timestamp": "2024-01-15 14:30:00"
}
```

#### 2. Volume Data
```python
DSEFINANCE('GP', 'volume')
```
**Returns:**
```json
{
  "symbol": "GP",
  "volume": 125000,
  "value_mn": 53.45,
  "trades": 1250,
  "timestamp": "2024-01-15 14:30:00"
}
```

#### 3. Change Data
```python
DSEFINANCE('GP', 'change')
```
**Returns:**
```json
{
  "symbol": "GP",
  "change": 3.50,
  "change_percent": 0.83,
  "current_price": 425.50,
  "previous_close": 422.00,
  "timestamp": "2024-01-15 14:30:00"
}
```

#### 4. All Data
```python
DSEFINANCE('GP', 'all')
```
**Returns:** Complete dataset combining all above fields

#### 5. Historical Data
```python
DSEFINANCE('GP', 'history', '2024-01-01', '2024-01-31')
```
**Returns:** Pandas DataFrame with columns:
- Date
- Open
- High
- Low
- Close
- Volume
- Symbol

---

## 🖥️ Using the Web Interface

### 1. Quick Lookup Tab

**Search for Stocks:**
- Type stock symbol in search box
- View search results with current prices
- Click popular stocks for quick access
- Get detailed information for any stock

**Stock Details Include:**
- Current price with change indicator
- High/Low prices for the day
- Trading volume and value
- Previous close price
- API usage examples

### 2. Historical Data Tab

**Get Historical Charts:**
- Enter stock symbol
- Select time period (1 week to 1 year, or custom)
- View interactive candlestick charts
- Download data in CSV or JSON format

**Features:**
- Interactive Plotly charts
- Zoom and pan functionality
- Data table view
- Export capabilities

### 3. Market Overview Tab

**Market Statistics:**
- Current market status (Open/Closed)
- Total stocks traded
- Advancing vs declining stocks
- Total volume and value
- Market composition pie chart

**Top Performers:**
- Top gainers of the day
- Top losers of the day
- Real-time percentage changes

### 4. Bulk Export Tab

**Export Options:**
- Multiple stocks current data
- Single stock historical data
- Complete market summary
- All stocks current data

**Export Formats:**
- CSV for Excel analysis
- JSON for programming use

---

## 📊 Excel/Google Sheets Integration

### Using in Excel

**Setup:** Create a custom function or use VBA to call the API

**Example VBA Function:**
```vba
Function DSEFINANCE(symbol As String, attribute As String, Optional startDate As String, Optional endDate As String)
    ' Call your Python API endpoint
    ' Return the data to Excel cell
End Function
```

**Usage in Excel:**
```excel
=DSEFINANCE("GP", "price")
=DSEFINANCE("SQURPHARMA", "volume")
=DSEFINANCE("BEXIMCO", "change")
```

### Using in Google Sheets

**Setup:** Use Google Apps Script to create custom function

**Example Apps Script:**
```javascript
function DSEFINANCE(symbol, attribute, startDate, endDate) {
  // Call your API endpoint
  // Return data to Google Sheets
}
```

**Usage in Google Sheets:**
```
=DSEFINANCE("GP", "price")
=DSEFINANCE("LHBL", "history", "2024-01-01", "2024-01-31")
```

---

## 🔧 Advanced Usage

### Bulk Data Processing

**Get Multiple Stocks:**
```python
symbols = ['GP', 'SQURPHARMA', 'BEXIMCO', 'LHBL']
bulk_data = dse_finance.get_multiple_stocks(symbols, 'price')
```

**Search Stocks:**
```python
results = dse_finance.search_stocks('BANK')  # Find all bank stocks
```

**Market Summary:**
```python
summary = dse_finance.get_market_summary()
```

### Data Export

**CSV Export:**
```python
csv_data = dse_finance.export_to_csv(data)
```

**JSON Export:**
```python
json_data = dse_finance.export_to_json(data)
```

---

## 📅 Working with Dates

### Date Formats

**Supported Format:** YYYY-MM-DD
- ✅ Correct: "2024-01-15"
- ❌ Incorrect: "15/01/2024", "Jan 15, 2024"

### DSE Trading Days

**Market Schedule:**
- **Trading Days:** Sunday - Thursday
- **Market Hours:** 10:30 AM - 2:30 PM (Bangladesh Time)
- **Holidays:** Public holidays in Bangladesh

**Note:** Historical data only includes trading days

---

## 💡 Practical Examples

### 1. Portfolio Tracking

```python
# Track your portfolio stocks
portfolio_stocks = ['GP', 'SQURPHARMA', 'BEXIMCO', 'LHBL', 'BRACBANK']

for stock in portfolio_stocks:
    data = DSEFINANCE(stock, 'price')
    print(f"{stock}: ৳{data['price']} ({data['change_percent']:+.2f}%)")
```

### 2. Market Analysis

```python
# Get market overview
market = dse_finance.get_market_summary()
print(f"Market Status: {market['market_status']}")
print(f"Advancing: {market['advancing']}")
print(f"Declining: {market['declining']}")
```

### 3. Historical Analysis

```python
# Analyze 3-month performance
historical = DSEFINANCE('GP', 'history', '2023-10-01', '2023-12-31')
start_price = historical.iloc[0]['Open']
end_price = historical.iloc[-1]['Close']
performance = ((end_price - start_price) / start_price) * 100
print(f"3-month performance: {performance:.2f}%")
```

### 4. Top Performers

```python
# Find top performing stocks
all_stocks = dse_finance.search_stocks('', limit=100)
top_gainers = sorted(all_stocks, key=lambda x: x['change_percent'], reverse=True)[:10]

for stock in top_gainers:
    print(f"{stock['symbol']}: +{stock['change_percent']:.2f}%")
```

---

## 🔍 Comparison with GOOGLEFINANCE

| Feature | GOOGLEFINANCE | DSEFINANCE |
|---------|---------------|------------|
| **Market Coverage** | Global markets | Dhaka Stock Exchange |
| **Real-time Data** | ✅ Yes | ✅ Yes |
| **Historical Data** | ✅ Yes | ✅ Yes (Generated) |
| **Syntax** | `=GOOGLEFINANCE("GOOG", "price")` | `=DSEFINANCE("GP", "price")` |
| **Attributes** | price, volume, marketcap, etc. | price, volume, change, history |
| **Date Range** | Flexible | YYYY-MM-DD format |
| **Export** | Google Sheets only | CSV, JSON, Excel |

---

## ⚡ Performance Tips

### Caching
- Data is cached for 5 minutes to improve performance
- Subsequent requests for the same data return cached results
- Cache automatically refreshes for real-time accuracy

### Bulk Operations
- Use bulk export for multiple stocks
- Batch API calls when possible
- Consider rate limits for large datasets

### Optimal Usage
- Use 'price' attribute for current market data
- Use 'history' for chart analysis
- Use 'all' when you need complete information
- Use 'volume' or 'change' for specific metrics

---

## 🛠️ Technical Implementation

### API Endpoints Used
- **Quotes Data:** `https://www.dsebd.org/datafile/quotes.txt`
- **Company Details:** `https://www.dsebd.org/displayCompany.php`
- **Top Performers:** `https://www.dsebd.org/top_20_share.php`

### Data Sources
- **Real-time Data:** Direct from DSE website
- **Historical Data:** Generated based on current prices
- **Market Status:** Calculated based on DSE trading hours

### Error Handling
- Network timeouts with retry logic
- Invalid symbol handling
- Date validation for historical data
- Graceful degradation when API is unavailable

---

## 📋 Supported Stocks

### Popular DSE Stocks
- **Banking:** BRACBANK, EBL, DBH, CITYBANK
- **Pharmaceuticals:** SQURPHARMA, BEXIMCO, ACI, RENATA
- **Telecommunications:** GP (Grameenphone)
- **Textiles:** LHBL, HEIDELBERG
- **Food & Beverages:** PRAN, OLYMPIC
- **Cement:** HEIDELBERG, CONFIDCEM
- **Power:** SUMMIT, NORTHERN

### All Listed Stocks
The API supports all stocks listed on the Dhaka Stock Exchange. Use the search function to find specific stocks.

---

## 🆘 Troubleshooting

### Common Issues

**"No data found for symbol"**
- Verify the stock symbol is correct
- Check if the stock is listed on DSE
- Try searching for the stock first

**"Invalid date format"**
- Use YYYY-MM-DD format only
- Ensure start_date is before end_date
- Use trading days only (Sunday-Thursday)

**"Connection timeout"**
- Check internet connection
- DSE website might be temporarily unavailable
- Try again after a few minutes

**"Historical data not available"**
- Currently generates sample data
- Real historical data requires premium access
- Use for demonstration and testing purposes

---

## 🎉 Conclusion

The DSE Finance API provides a powerful and intuitive way to access Dhaka Stock Exchange data. With its Google Finance-like syntax and comprehensive features, it's perfect for:

- **Individual investors** tracking portfolios
- **Financial analysts** conducting market research
- **Developers** building financial applications
- **Students** learning about the DSE market

### Key Benefits:
✅ **Familiar syntax** similar to Google Finance
✅ **Real-time data** from DSE
✅ **Multiple export formats** for analysis
✅ **Clean, simple interface** for non-technical users
✅ **Comprehensive API** for developers

**Start exploring DSE Finance today and take your stock market analysis to the next level!** 📈

---

*For support and additional features, refer to the main application documentation or contact your developer.*