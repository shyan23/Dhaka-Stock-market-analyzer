# 📈 Stock Market Analyzer - Simple User Guide

## 🎯 **For Non-Tech Users: Complete Step-by-Step Guide**

### 🚀 **What This App Does**
This app helps you track your stock investments in the Dhaka Stock Exchange (DSE). Think of it as your personal stock portfolio manager that shows you:
- Current prices of your stocks
- How much profit or loss you're making
- Beautiful charts and graphs
- Professional reports you can print or share

---

## 📋 **Step 1: Getting Started (First Time Setup)**

### Option A: If You Have Python Installed
1. **Open Command Prompt** (Windows) or **Terminal** (Mac/Linux)
2. **Copy and paste these commands one by one:**
   ```bash
   cd Desktop/Code/stock_market_analyzer
   pip install -r requirements.txt
   streamlit run main.py
   ```
3. **Wait for your web browser to open automatically**

### Option B: If You Don't Have Python (Easier!)
1. Ask your tech-savvy friend to install Python and set this up once
2. After setup, you only need to run one simple command (see "Daily Use" below)

---

## 💻 **Daily Use (After Setup)**

### Starting the App:
1. **Open Command Prompt/Terminal**
2. **Type this command:**
   ```bash
   cd Desktop/Code/stock_market_analyzer
   streamlit run main.py
   ```
3. **Your web browser will open with the app**

### First Time App Setup:
1. **Choose Your Storage Method:**
   - **Google Sheets** (Recommended): Access from anywhere, automatic backup
   - **Local Database**: Faster, but only works on this computer

2. **If You Choose Google Sheets:**
   - Follow the on-screen instructions
   - You'll need to create a Google account if you don't have one
   - The app will guide you through connecting to Google Sheets

---

## 📊 **How to Use the App**

### **Step 1: Add Stocks to Track**
1. **Click "Stock Selector" in the sidebar**
2. **Search for stocks you own:**
   - Type stock names like "GP", "BRAC", "Square"
   - Or company names like "Grameenphone", "BRAC Bank"
3. **Click the "➕ Add" button** next to stocks you want to track
4. **Use Quick Add buttons** for popular stocks like GP, BRACBANK, etc.

### **Step 2: Record Your Transactions**
1. **Click "Transactions" in the sidebar**
2. **Click "New Transaction" tab**
3. **Fill in the form:**
   - **Select Stock**: Choose from your tracked stocks
   - **Type**: Buy or Sell
   - **Quantity**: How many shares
   - **Price**: The price automatically fills with current market price
   - **Use Quick Price Buttons**: "Use LTP", "-5%", "+5%"
4. **Click "Record Transaction"**

### **Step 3: View Your Portfolio**
1. **Click "Dashboard" to see overview**
2. **Click "Portfolio" for detailed view**
3. **See your:**
   - Total portfolio value
   - Profit/Loss for each stock
   - Beautiful charts and graphs

### **Step 4: Generate Reports**
1. **Click "Settings"**
2. **Click "Export & Reports" tab**
3. **Choose what you want:**
   - **PDF Report**: Professional report you can print
   - **Excel File**: Spreadsheet with all your data
   - **CSV Files**: Simple data files

---

## 🎨 **Understanding the Interface**

### **Sidebar (Left Side):**
- **Navigate**: Choose which page to view
- **Storage**: Shows if you're using Google Sheets or Local database
- **Tracked Stocks**: Quick list of your stocks
- **Portfolio Value**: Your total investment value

### **Main Pages:**

#### 🏠 **Dashboard**
- **Market Status**: Shows if DSE is open or closed
- **Portfolio Summary**: Total value, gains/losses
- **Charts**: Price movements, portfolio performance

#### 🔍 **Stock Selector**
- **Search**: Type stock names to find them
- **Quick Add**: Click popular stocks to add instantly
- **Currently Tracking**: See all your tracked stocks

#### 💼 **Portfolio**
- **Holdings**: All stocks you own
- **Performance**: Profit/loss for each stock
- **Analytics**: Detailed charts and metrics

#### 💹 **Transactions**
- **New Transaction**: Record buy/sell orders
- **Quick Trade**: Fast trading interface
- **Transaction Log**: History of all your trades

#### 📊 **Price Tracker**
- **Price Matrix**: Live prices in table format
- **Comparison**: Compare multiple stocks
- **Historical Data**: Price history and trends

#### ⚙️ **Settings**
- **Ticker Config**: Manage tracked stocks
- **API Settings**: Technical settings
- **Export**: Generate reports and download data

---

## 🎯 **Common Tasks Made Easy**

### **"I want to see how much money I've made/lost"**
1. Go to **Dashboard**
2. Look at the **Portfolio Summary** cards
3. Green numbers = Profit, Red numbers = Loss

### **"I want to add a new stock to track"**
1. Go to **Stock Selector**
2. Type the stock name in the search box
3. Click **"➕ Add"** next to the stock

### **"I bought some shares today"**
1. Go to **Transactions**
2. Click **"New Transaction"**
3. Select your stock, enter quantity, check the price
4. Click **"Record Transaction"**

### **"I want to see price charts"**
1. Go to **Dashboard**
2. Click **"Price Charts"** tab
3. Select stocks to display
4. Choose **"Candlestick Chart"** for detailed view

### **"I want to print a report for my advisor"**
1. Go to **Settings**
2. Click **"Export & Reports"**
3. Click **"Generate PDF Report"**
4. Download and print the PDF

### **"I want to see if the market is open"**
- Look at the **top of Dashboard** - it shows market status in real-time
- 🟢 = Market Open, 🔴 = Market Closed

---

## ⚠️ **Important Tips**

### **Daily Routine:**
1. **Open the app** (streamlit run main.py)
2. **Check Dashboard** for market status and portfolio overview
3. **Record any trades** you made
4. **Close the app** when done (Ctrl+C in command prompt)

### **Data Safety:**
- **Google Sheets Mode**: Your data is automatically backed up online
- **Local Mode**: Your data is only on this computer
- **Export regularly**: Download reports for your records

### **Getting Help:**
- **Market Status**: Check if market is open before expecting price updates
- **Price Updates**: Prices update every few minutes during market hours
- **Red/Green Colors**: Red = Loss, Green = Profit (universal stock market colors)

---

## 🆘 **Troubleshooting**

### **"The app won't start"**
1. Make sure you're in the right folder: `cd Desktop/Code/stock_market_analyzer`
2. Try: `pip install -r requirements.txt` again
3. Ask your tech friend to check Python installation

### **"I can't find my stocks"**
1. Try different search terms (both symbol and company name)
2. Check if you're spelling correctly
3. Some stocks might not be available on DSE

### **"My numbers look wrong"**
1. Make sure you recorded all your transactions
2. Check if you entered correct quantities and prices
3. Remember: the app only knows what you tell it

### **"The market status is wrong"**
- The app shows Bangladesh time (BST)
- DSE is open Sunday-Thursday, 10:30 AM - 2:30 PM

---

## 🎉 **You're Ready!**

This app will help you:
- ✅ **Track your investments** professionally
- ✅ **Monitor profits and losses** in real-time
- ✅ **Generate reports** for tax purposes or advisors
- ✅ **Make informed decisions** with charts and data
- ✅ **Stay organized** with automatic calculations

**Remember**: Start simple! Add a few stocks, record some transactions, and explore the features gradually. The app is designed to be intuitive - most buttons and features are self-explanatory.

**Happy investing!** 📈💰